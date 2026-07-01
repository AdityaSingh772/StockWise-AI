import yfinance as yf
import pandas as pd
from typing import Optional
import logging
from app.models.schemas import StockData

logger = logging.getLogger(__name__)

# Common company name → ticker mappings for natural language queries
COMPANY_TICKER_MAP = {
    # US Tech
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
    "netflix": "NFLX",
    "intel": "INTC",
    "amd": "AMD",
    "qualcomm": "QCOM",
    "salesforce": "CRM",
    "adobe": "ADBE",
    "oracle": "ORCL",
    "paypal": "PYPL",
    "uber": "UBER",
    "lyft": "LYFT",
    "airbnb": "ABNB",
    "spotify": "SPOT",
    "twitter": "TWTR",
    "snap": "SNAP",
    "zoom": "ZM",
    "shopify": "SHOP",
    "square": "SQ",
    "block": "SQ",
    "palantir": "PLTR",
    "coinbase": "COIN",
    "robinhood": "HOOD",
    "snowflake": "SNOW",
    "datadog": "DDOG",
    "cloudflare": "NET",
    "mongodb": "MDB",
    "okta": "OKTA",
    "twilio": "TWLO",
    "docusign": "DOCU",
    # US Finance
    "jpmorgan": "JPM",
    "jp morgan": "JPM",
    "bank of america": "BAC",
    "wells fargo": "WFC",
    "goldman sachs": "GS",
    "morgan stanley": "MS",
    "citigroup": "C",
    "visa": "V",
    "mastercard": "MA",
    "american express": "AXP",
    "berkshire": "BRK-B",
    "berkshire hathaway": "BRK-B",
    # US Others
    "disney": "DIS",
    "walmart": "WMT",
    "johnson & johnson": "JNJ",
    "pfizer": "PFE",
    "coca cola": "KO",
    "pepsico": "PEP",
    "nike": "NKE",
    "boeing": "BA",
    "ford": "F",
    "general motors": "GM",
    "exxon": "XOM",
    "chevron": "CVX",
    # Indian stocks (NSE)
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "tata consultancy": "TCS.NS",
    "infosys": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfc": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "state bank": "SBIN.NS",
    "sbi": "SBIN.NS",
    "axis bank": "AXISBANK.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bajaj": "BAJFINANCE.NS",
    "kotak": "KOTAKBANK.NS",
    "kotak mahindra": "KOTAKBANK.NS",
    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",
    "tata motors": "TATAMOTORS.NS",
    "tata steel": "TATASTEEL.NS",
    "hindalco": "HINDALCO.NS",
    "sun pharma": "SUNPHARMA.NS",
    "dr reddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "asian paints": "ASIANPAINT.NS",
    "hul": "HINDUNILVR.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "ongc": "ONGC.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "zomato": "ZOMATO.NS",
    "paytm": "PAYTM.NS",
    "nykaa": "NYKAA.NS",
    "delhivery": "DELHIVERY.NS",
    # Chinese
    "alibaba": "BABA",
    "tencent": "TCEHY",
    "baidu": "BIDU",
    # Others
    "samsung": "005930.KS",
    "toyota": "TM",
    "volkswagen": "VWAGY",
    "lvmh": "LVMUY",
    "nestlé": "NSRGY",
    "nestle": "NSRGY",
}


def resolve_ticker(query: str) -> Optional[str]:
    """
    Resolve a company name or ticker symbol to a valid ticker.
    Returns None if not found.
    """
    query_lower = query.lower().strip()

    # Check direct mapping first
    if query_lower in COMPANY_TICKER_MAP:
        return COMPANY_TICKER_MAP[query_lower]

    # Check partial matches
    for company, ticker in COMPANY_TICKER_MAP.items():
        if company in query_lower or query_lower in company:
            return ticker

    # Assume the query itself might be a ticker symbol
    ticker_upper = query.upper().strip()
    return ticker_upper


def fetch_stock_data(ticker: str) -> StockData:
    """
    Fetch comprehensive stock data using yfinance.
    Returns a StockData model with all available fields.
    """
    try:
        logger.info(f"Fetching data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check if it returned valid data
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            # Try to get at least basic info
            if not info or "longName" not in info:
                return StockData(
                    ticker=ticker,
                    company_name=ticker,
                    error=f"Could not find stock data for '{ticker}'. Please check the ticker symbol or company name."
                )

        # Get price history (last 30 days)
        history_df = stock.history(period="1mo")
        price_history = []
        history_dates = []
        if not history_df.empty:
            price_history = [round(p, 2) for p in history_df["Close"].tolist()]
            history_dates = [str(d.date()) for d in history_df.index.tolist()]

        # Helper to safely get numeric values
        def safe_float(key: str) -> Optional[float]:
            val = info.get(key)
            if val is not None and isinstance(val, (int, float)) and not pd.isna(val):
                return float(val)
            return None

        def safe_int(key: str) -> Optional[int]:
            val = info.get(key)
            if val is not None and isinstance(val, (int, float)) and not pd.isna(val):
                return int(val)
            return None

        current_price = safe_float("currentPrice") or safe_float("regularMarketPrice")

        return StockData(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName") or ticker,
            current_price=current_price,
            currency=info.get("currency", "USD"),
            market_cap=safe_float("marketCap"),
            pe_ratio=safe_float("trailingPE"),
            eps=safe_float("trailingEps"),
            revenue=safe_float("totalRevenue"),
            net_income=safe_float("netIncomeToCommon"),
            week_52_high=safe_float("fiftyTwoWeekHigh"),
            week_52_low=safe_float("fiftyTwoWeekLow"),
            volume=safe_int("volume"),
            avg_volume=safe_int("averageVolume"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            country=info.get("country"),
            employees=safe_int("fullTimeEmployees"),
            description=info.get("longBusinessSummary"),
            website=info.get("website"),
            dividend_yield=safe_float("dividendYield"),
            beta=safe_float("beta"),
            pb_ratio=safe_float("priceToBook"),
            ps_ratio=safe_float("priceToSalesTrailing12Months"),
            debt_to_equity=safe_float("debtToEquity"),
            return_on_equity=safe_float("returnOnEquity"),
            profit_margin=safe_float("profitMargins"),
            operating_margin=safe_float("operatingMargins"),
            gross_profit=safe_float("grossProfits"),
            free_cashflow=safe_float("freeCashflow"),
            price_history=price_history,
            history_dates=history_dates,
        )

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return StockData(
            ticker=ticker,
            company_name=ticker,
            error=f"Failed to fetch data for '{ticker}': {str(e)}"
        )


def format_number(value: Optional[float], prefix: str = "", suffix: str = "") -> str:
    """Format large numbers into human-readable form (B, M, K)."""
    if value is None:
        return "N/A"
    abs_val = abs(value)
    if abs_val >= 1_000_000_000_000:
        return f"{prefix}{value/1_000_000_000_000:.2f}T{suffix}"
    elif abs_val >= 1_000_000_000:
        return f"{prefix}{value/1_000_000_000:.2f}B{suffix}"
    elif abs_val >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M{suffix}"
    elif abs_val >= 1_000:
        return f"{prefix}{value/1_000:.2f}K{suffix}"
    else:
        return f"{prefix}{value:.2f}{suffix}"


def format_percentage(value: Optional[float]) -> str:
    """Format a decimal ratio as a percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"
