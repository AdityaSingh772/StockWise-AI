import pytest
import asyncio


# ──────────────────────────────────────────────
# Stock Service Tests
# ──────────────────────────────────────────────

def test_resolve_ticker_known_company():
    from app.services.stock_service import resolve_ticker
    assert resolve_ticker("apple") == "AAPL"
    assert resolve_ticker("Tesla") == "TSLA"
    assert resolve_ticker("TCS") == "TCS.NS"


def test_resolve_ticker_direct_symbol():
    from app.services.stock_service import resolve_ticker
    result = resolve_ticker("MSFT")
    assert result == "MSFT"


def test_format_number():
    from app.services.stock_service import format_number
    assert "T" in format_number(1_000_000_000_000)
    assert "B" in format_number(2_500_000_000)
    assert "M" in format_number(500_000_000)
    assert "K" in format_number(50_000)


def test_format_percentage():
    from app.services.stock_service import format_percentage
    assert format_percentage(0.25) == "25.00%"
    assert format_percentage(None) == "N/A"
    assert format_percentage(0.0312) == "3.12%"


# ──────────────────────────────────────────────
# Intent Classification Tests
# ──────────────────────────────────────────────

def test_classify_intent_analyze():
    from app.graph.nodes import classify_intent
    state = {
        "user_message": "Analyze Apple stock",
        "chat_id": 123,
        "user_name": "Test",
        "intent": None,
        "tickers": None,
        "company_names": None,
        "stock_data": None,
        "report": None,
        "error": None,
        "step": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "analyze"


def test_classify_intent_compare():
    from app.graph.nodes import classify_intent
    state = {
        "user_message": "Compare Apple vs Microsoft",
        "chat_id": 123,
        "user_name": "Test",
        "intent": None,
        "tickers": None,
        "company_names": None,
        "stock_data": None,
        "report": None,
        "error": None,
        "step": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "compare"


def test_classify_intent_help():
    from app.graph.nodes import classify_intent
    state = {
        "user_message": "help me please",
        "chat_id": 123,
        "user_name": "Test",
        "intent": None,
        "tickers": None,
        "company_names": None,
        "stock_data": None,
        "report": None,
        "error": None,
        "step": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "help"


# ──────────────────────────────────────────────
# Entity Extraction Tests
# ──────────────────────────────────────────────

def test_extract_entities_apple():
    from app.graph.nodes import extract_entities
    state = {
        "user_message": "Analyze Apple",
        "chat_id": 123,
        "user_name": "Test",
        "intent": "analyze",
        "tickers": None,
        "company_names": None,
        "stock_data": None,
        "report": None,
        "error": None,
        "step": None,
    }
    result = extract_entities(state)
    assert "AAPL" in result["tickers"]


def test_extract_entities_compare():
    from app.graph.nodes import extract_entities
    state = {
        "user_message": "Compare Tesla and Ford",
        "chat_id": 123,
        "user_name": "Test",
        "intent": "compare",
        "tickers": None,
        "company_names": None,
        "stock_data": None,
        "report": None,
        "error": None,
        "step": None,
    }
    result = extract_entities(state)
    assert len(result["tickers"]) == 2
    assert "TSLA" in result["tickers"]
    assert "F" in result["tickers"]


# ──────────────────────────────────────────────
# Prompt Template Tests
# ──────────────────────────────────────────────

def test_help_message_content():
    from app.prompts.templates import get_help_message
    msg = get_help_message()
    assert "/start" in msg
    assert "/help" in msg
    assert "/analyze" in msg


def test_welcome_message_content():
    from app.prompts.templates import get_welcome_message
    msg = get_welcome_message()
    assert "StockWise AI" in msg


# ──────────────────────────────────────────────
# StockData Model Tests
# ──────────────────────────────────────────────

def test_stock_data_model():
    from app.models.schemas import StockData
    stock = StockData(
        ticker="AAPL",
        company_name="Apple Inc.",
        current_price=189.5,
        market_cap=3_000_000_000_000,
    )
    assert stock.ticker == "AAPL"
    assert stock.current_price == 189.5
    assert stock.error is None


def test_analysis_request_model():
    from app.models.schemas import AnalysisRequest
    req = AnalysisRequest(user_message="Analyze Tesla", chat_id=12345)
    assert req.user_message == "Analyze Tesla"
    assert req.chat_id == 12345
