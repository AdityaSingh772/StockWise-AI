from pydantic import BaseModel
from typing import Optional


class StockData(BaseModel):
    """Raw stock data fetched from yfinance."""
    ticker: str
    company_name: str
    current_price: Optional[float] = None
    currency: Optional[str] = "USD"
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employees: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    gross_profit: Optional[float] = None
    free_cashflow: Optional[float] = None
    # Price history (last 30 days as list of closing prices)
    price_history: Optional[list] = None
    history_dates: Optional[list] = None
    error: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    user_message: str
    chat_id: int
    user_name: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model containing the formatted analysis report."""
    success: bool
    report: Optional[str] = None
    error: Optional[str] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None


class WebhookPayload(BaseModel):
    """Telegram webhook update payload."""
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None
