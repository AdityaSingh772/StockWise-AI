import logging
from langgraph.graph import StateGraph, END
from app.graph.state import WorkflowState
from app.graph.nodes import classify_intent, extract_entities
from app.services.stock_service import fetch_stock_data
from app.services.groq_service import generate_analysis, generate_comparison
from app.prompts.templates import get_help_message, get_welcome_message

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Node: Receive Message (entry point / init)
# ──────────────────────────────────────────────
def receive_message(state: WorkflowState) -> WorkflowState:
    """Node 1: Receive and log the incoming message."""
    logger.info(f"[Node 1] Received message from chat_id={state['chat_id']}: {state['user_message']}")
    state["step"] = "receive_message"
    state["intent"] = None
    state["tickers"] = None
    state["company_names"] = None
    state["stock_data"] = None
    state["report"] = None
    state["error"] = None
    return state


# ──────────────────────────────────────────────
# Node: Fetch Live Data
# ──────────────────────────────────────────────
def fetch_live_data(state: WorkflowState) -> WorkflowState:
    """Node 4: Fetch live stock data from yfinance for all identified tickers."""
    state["step"] = "fetch_live_data"
    tickers = state.get("tickers") or []

    if not tickers:
        state["error"] = "No tickers to fetch data for."
        return state

    stock_data_list = []
    for ticker in tickers[:2]:  # Max 2 stocks
        data = fetch_stock_data(ticker)
        stock_data_list.append(data)
        if data.error:
            logger.warning(f"Error fetching {ticker}: {data.error}")

    state["stock_data"] = stock_data_list

    # Check if all fetches failed
    all_failed = all(s.error for s in stock_data_list)
    if all_failed:
        errors = " | ".join(s.error for s in stock_data_list if s.error)
        state["error"] = f"❌ {errors}"

    return state


# ──────────────────────────────────────────────
# Node: Generate AI Analysis
# ──────────────────────────────────────────────
def generate_ai_analysis(state: WorkflowState) -> WorkflowState:
    """Node 5: Generate AI analysis using Groq/Llama3."""
    state["step"] = "generate_ai_analysis"
    stock_data = state.get("stock_data") or []
    intent = state.get("intent")
    user_message = state.get("user_message", "")

    if not stock_data:
        state["error"] = "No stock data available for analysis."
        return state

    if intent == "compare" and len(stock_data) >= 2:
        analysis = generate_comparison(stock_data[0], stock_data[1], user_message)
    else:
        analysis = generate_analysis(stock_data[0], user_message)

    state["report"] = analysis
    return state


# ──────────────────────────────────────────────
# Node: Create Report
# ──────────────────────────────────────────────
def create_report(state: WorkflowState) -> WorkflowState:
    """Node 6: Assemble the final formatted report to be sent."""
    state["step"] = "create_report"

    if state.get("error") and not state.get("report"):
        # Error is already set, report will show error
        return state

    if not state.get("report"):
        state["error"] = "Failed to generate report."

    return state


# ──────────────────────────────────────────────
# Node: Handle Help
# ──────────────────────────────────────────────
def handle_help(state: WorkflowState) -> WorkflowState:
    """Handle help/unknown intent with a friendly help message."""
    state["step"] = "handle_help"
    state["report"] = get_help_message()
    return state


# ──────────────────────────────────────────────
# Routing logic
# ──────────────────────────────────────────────
def route_after_intent(state: WorkflowState) -> str:
    """Route based on classified intent."""
    intent = state.get("intent")
    error = state.get("error")

    if error or intent in ("help", "unknown"):
        return "handle_help"
    elif intent in ("analyze", "compare"):
        return "extract_entities"
    else:
        return "handle_help"


def route_after_extraction(state: WorkflowState) -> str:
    """Route after entity extraction."""
    error = state.get("error")
    tickers = state.get("tickers")

    if error or not tickers:
        return "handle_help"
    return "fetch_live_data"


def route_after_fetch(state: WorkflowState) -> str:
    """Route after fetching live data."""
    error = state.get("error")
    stock_data = state.get("stock_data") or []
    all_failed = all(s.error for s in stock_data)

    if error and all_failed:
        return END  # Will send error message
    return "generate_ai_analysis"


# ──────────────────────────────────────────────
# Build the LangGraph Workflow
# ──────────────────────────────────────────────
def build_workflow():
    """Construct and compile the LangGraph StateGraph."""
    workflow = StateGraph(WorkflowState)

    # Add all nodes
    workflow.add_node("receive_message", receive_message)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("fetch_live_data", fetch_live_data)
    workflow.add_node("generate_ai_analysis", generate_ai_analysis)
    workflow.add_node("create_report", create_report)
    workflow.add_node("handle_help", handle_help)

    # Set entry point
    workflow.set_entry_point("receive_message")

    # Add edges
    workflow.add_edge("receive_message", "classify_intent")
    workflow.add_conditional_edges("classify_intent", route_after_intent)
    workflow.add_conditional_edges("extract_entities", route_after_extraction)
    workflow.add_conditional_edges("fetch_live_data", route_after_fetch)
    workflow.add_edge("generate_ai_analysis", "create_report")
    workflow.add_edge("create_report", END)
    workflow.add_edge("handle_help", END)

    return workflow.compile()


# Compiled workflow (singleton)
stock_analysis_workflow = build_workflow()


async def run_workflow(user_message: str, chat_id: int, user_name: str = None) -> dict:
    """
    Run the full stock analysis workflow.
    Returns a dict with 'report', 'error', 'ticker', 'company_name'.
    """
    try:
        initial_state: WorkflowState = {
            "user_message": user_message,
            "chat_id": chat_id,
            "user_name": user_name,
            "intent": None,
            "tickers": None,
            "company_names": None,
            "stock_data": None,
            "report": None,
            "error": None,
            "step": None,
        }

        result = stock_analysis_workflow.invoke(initial_state)

        if result.get("error") and not result.get("report"):
            return {
                "success": False,
                "report": result["error"],
                "error": result["error"],
                "ticker": None,
                "company_name": None,
            }

        stock_data = result.get("stock_data") or []
        ticker = stock_data[0].ticker if stock_data else None
        company = stock_data[0].company_name if stock_data else None

        return {
            "success": True,
            "report": result.get("report", "Analysis complete."),
            "error": None,
            "ticker": ticker,
            "company_name": company,
        }

    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {
            "success": False,
            "report": f"⚠️ An error occurred: {str(e)}",
            "error": str(e),
            "ticker": None,
            "company_name": None,
        }
