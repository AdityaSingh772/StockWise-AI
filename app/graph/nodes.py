import re
import logging
from app.graph.state import WorkflowState
from app.services.stock_service import resolve_ticker, COMPANY_TICKER_MAP

logger = logging.getLogger(__name__)

# Keywords that indicate a comparison intent
COMPARE_KEYWORDS = [
    "compare", "vs", "versus", "against", "or", "better",
    "difference between", "which is better", "vs.", "and",
]

# Keywords that indicate a help intent
HELP_KEYWORDS = [
    "help", "how", "what can you", "what do you", "commands",
    "guide", "tutorial", "instructions", "start"
]

# Keywords that indicate analysis intent
ANALYZE_KEYWORDS = [
    "analyze", "analyse", "analysis", "report", "tell me about",
    "show me", "what is", "price", "stock", "share", "investment",
    "buy", "sell", "hold", "pe ratio", "market cap", "revenue",
    "earnings", "profit", "overvalued", "undervalued", "worth",
    "movement", "today", "performance", "forecast",
]


def classify_intent(state: WorkflowState) -> WorkflowState:
    """
    Node 2: Classify the user's intent.
    Determines if user wants to analyze, compare, get help, or unknown.
    """
    message = state["user_message"].lower()
    logger.info(f"Classifying intent for: {message}")

    state["step"] = "intent_classification"

    # Check for help intent
    if any(kw in message for kw in HELP_KEYWORDS) and not any(kw in message for kw in ANALYZE_KEYWORDS):
        state["intent"] = "help"
        return state

    # Check for comparison intent (two companies mentioned)
    compare_signals = sum(1 for kw in COMPARE_KEYWORDS if kw in message)
    if compare_signals >= 1:
        state["intent"] = "compare"
    else:
        state["intent"] = "analyze"

    logger.info(f"Classified intent: {state['intent']}")
    return state


def extract_entities(state: WorkflowState) -> WorkflowState:
    """
    Node 3: Extract company names/tickers from the user message.
    Resolves names to ticker symbols.
    """
    message = state["user_message"]
    message_lower = message.lower()
    state["step"] = "entity_extraction"
    found_companies = []
    found_tickers = []

    # Check against known company names in our map
    # Sort by length descending to match longer names first
    sorted_companies = sorted(COMPANY_TICKER_MAP.keys(), key=len, reverse=True)
    matched_tickers_set = set()

    for company in sorted_companies:
        if company in message_lower:
            ticker = COMPANY_TICKER_MAP[company]
            if ticker not in matched_tickers_set:
                matched_tickers_set.add(ticker)
                found_companies.append(company)
                found_tickers.append(ticker)
            # For comparison, we want up to 2; for analysis, 1 is enough
            if state["intent"] == "analyze" and len(found_tickers) >= 1:
                break
            if state["intent"] == "compare" and len(found_tickers) >= 2:
                break

    # If nothing found via name map, look for explicit ticker symbols (ALL_CAPS 1-5 chars)
    if not found_tickers:
        ticker_pattern = r'\b([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\b'
        raw_tickers = re.findall(ticker_pattern, message)
        # Filter out common words that aren't tickers
        stop_words = {"I", "A", "THE", "IS", "IN", "OF", "TO", "FOR", "ON", "AT", "BY", "AN", "BE"}
        for t in raw_tickers:
            if t not in stop_words:
                found_tickers.append(t)
                found_companies.append(t)
                if state["intent"] == "compare" and len(found_tickers) >= 2:
                    break
                elif len(found_tickers) >= 1 and state["intent"] == "analyze":
                    break

    # Last resort: try to resolve the whole message as a ticker/company
    if not found_tickers:
        ticker = resolve_ticker(message.strip())
        if ticker:
            found_tickers = [ticker]
            found_companies = [message.strip()]

    state["company_names"] = found_companies
    state["tickers"] = found_tickers

    if not found_tickers:
        state["error"] = (
            "❓ I couldn't identify a stock or company name in your message.\n\n"
            "Try commands like:\n"
            "• `Analyze Apple`\n"
            "• `Compare Tesla vs Ford`\n"
            "• `TSLA` (ticker symbol)\n"
            "• `/analyze AAPL`"
        )
        state["intent"] = "unknown"

    logger.info(f"Extracted tickers: {state['tickers']}")
    return state
