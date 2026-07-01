import logging
import json
from datetime import datetime


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.WARNING)


def format_currency(value: float, currency: str = "USD") -> str:
    """Format a number as currency with symbol."""
    symbols = {"USD": "$", "INR": "₹", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, currency + " ")
    if abs(value) >= 1_000_000_000_000:
        return f"{symbol}{value/1_000_000_000_000:.2f}T"
    elif abs(value) >= 1_000_000_000:
        return f"{symbol}{value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{symbol}{value/1_000_000:.2f}M"
    else:
        return f"{symbol}{value:,.2f}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length characters."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def is_market_hours() -> bool:
    """
    Check if US stock market is approximately open.
    Market hours: Mon-Fri, 9:30 AM - 4:00 PM ET (UTC-4 / UTC-5).
    This is a rough check without timezone library dependency.
    """
    now_utc = datetime.utcnow()
    # Market is closed on weekends
    if now_utc.weekday() >= 5:
        return False
    # Market open: ~13:30 UTC (9:30 ET), close ~20:00 UTC (4:00 PM ET)
    market_open_utc_hour = 13
    market_close_utc_hour = 20
    return market_open_utc_hour <= now_utc.hour < market_close_utc_hour


def sanitize_markdown(text: str) -> str:
    """
    Escape special markdown characters in plain text strings
    to prevent Telegram parse errors.
    """
    # Characters that need escaping in Telegram MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
