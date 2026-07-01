from typing import TypedDict, Optional, Literal
from app.models.schemas import StockData


class WorkflowState(TypedDict):
    """
    Shared state object passed through all LangGraph workflow nodes.
    Each node reads and writes to this state.
    """
    # Input
    user_message: str
    chat_id: int
    user_name: Optional[str]

    # Intent classification
    intent: Optional[Literal["analyze", "compare", "help", "unknown"]]

    # Extracted entities
    tickers: Optional[list[str]]        # Resolved ticker symbols
    company_names: Optional[list[str]]  # Raw company names from user message

    # Fetched stock data
    stock_data: Optional[list[StockData]]

    # Generated content
    report: Optional[str]

    # Error handling
    error: Optional[str]

    # Metadata
    step: Optional[str]   # Current workflow step name
