from groq import Groq
from app.config.settings import settings
from app.models.schemas import StockData
from app.services.stock_service import format_number, format_percentage
import logging

logger = logging.getLogger(__name__)


def get_groq_client() -> Groq:
    """Initialize and return a Groq client."""
    return Groq(api_key=settings.GROQ_API_KEY)


def build_stock_context(stock: StockData) -> str:
    """Build a structured context string from StockData for the LLM."""
    currency = stock.currency or "USD"
    lines = [
        f"=== STOCK DATA FOR {stock.company_name} ({stock.ticker}) ===",
        f"Current Price: {format_number(stock.current_price, prefix=currency+' ')}",
        f"Market Cap: {format_number(stock.market_cap, prefix=currency+' ')}",
        f"P/E Ratio (Trailing): {round(stock.pe_ratio, 2) if stock.pe_ratio else 'N/A'}",
        f"EPS (Trailing): {format_number(stock.eps, prefix=currency+' ')}",
        f"Revenue (TTM): {format_number(stock.revenue, prefix=currency+' ')}",
        f"Net Income (TTM): {format_number(stock.net_income, prefix=currency+' ')}",
        f"Gross Profit: {format_number(stock.gross_profit, prefix=currency+' ')}",
        f"Free Cash Flow: {format_number(stock.free_cashflow, prefix=currency+' ')}",
        f"52-Week High: {format_number(stock.week_52_high, prefix=currency+' ')}",
        f"52-Week Low: {format_number(stock.week_52_low, prefix=currency+' ')}",
        f"Volume: {format_number(stock.volume)}",
        f"Avg Volume: {format_number(stock.avg_volume)}",
        f"Sector: {stock.sector or 'N/A'}",
        f"Industry: {stock.industry or 'N/A'}",
        f"Country: {stock.country or 'N/A'}",
        f"Employees: {format_number(stock.employees)}",
        f"Dividend Yield: {format_percentage(stock.dividend_yield)}",
        f"Beta: {round(stock.beta, 2) if stock.beta else 'N/A'}",
        f"Price-to-Book Ratio: {round(stock.pb_ratio, 2) if stock.pb_ratio else 'N/A'}",
        f"Price-to-Sales Ratio: {round(stock.ps_ratio, 2) if stock.ps_ratio else 'N/A'}",
        f"Debt-to-Equity: {round(stock.debt_to_equity, 2) if stock.debt_to_equity else 'N/A'}",
        f"Return on Equity: {format_percentage(stock.return_on_equity)}",
        f"Profit Margin: {format_percentage(stock.profit_margin)}",
        f"Operating Margin: {format_percentage(stock.operating_margin)}",
        f"Website: {stock.website or 'N/A'}",
    ]
    if stock.description:
        lines.append(f"\nBusiness Summary: {stock.description[:500]}...")
    if stock.price_history:
        recent = stock.price_history[-5:] if len(stock.price_history) >= 5 else stock.price_history
        lines.append(f"\nRecent Closing Prices (last 5 days): {recent}")
        # Simple trend
        if len(stock.price_history) >= 2:
            change = stock.price_history[-1] - stock.price_history[0]
            pct = (change / stock.price_history[0]) * 100
            direction = "UP" if change > 0 else "DOWN"
            lines.append(f"30-Day Trend: {direction} {abs(pct):.2f}%")
    return "\n".join(lines)


def generate_analysis(stock: StockData, user_query: str) -> str:
    """
    Use Groq (Llama 3) to generate a comprehensive AI analysis report
    for the given stock data and user query.
    """
    try:
        client = get_groq_client()
        context = build_stock_context(stock)
        currency = stock.currency or "USD"

        system_prompt = """You are StockWise AI, an expert financial analyst assistant. 
You provide clear, insightful, and balanced stock analysis to retail investors.
Your reports are well-structured, easy to understand, and include appropriate financial disclaimers.
You analyze real data and give honest assessments — you do not make up data.
Format your response using Telegram-compatible markdown (bold with *, italic with _, code with `).
Keep your analysis concise yet comprehensive — aim for 400-600 words."""

        user_prompt = f"""Based on the following real-time stock data, provide a comprehensive analysis report.

USER QUERY: {user_query}

STOCK DATA:
{context}

Please provide a structured report with these sections:
1. 📊 *Company Overview* - Brief intro to the company and sector
2. 💰 *Key Financial Metrics* - Analyze the most important numbers (price, market cap, P/E, EPS, revenue, margins)
3. 📈 *Growth Analysis* - Revenue and profit trends, cash flow health
4. 🎯 *Valuation* - Is the stock cheap or expensive compared to industry standards? Use P/E, P/B, P/S ratios.
5. ⚠️ *Risk Factors* - Key risks based on the data (high debt, low margins, high beta, etc.)
6. 📉 *Recent Performance* - Price trend analysis (52-week range, recent movement)
7. 🤖 *AI Summary & Outlook* - A balanced summary with outlook (Bullish/Neutral/Bearish) and key takeaways
8. ⚖️ *Disclaimer* - Short standard disclaimer

Use {currency} for currency values. Be specific with numbers from the data provided.
Do NOT make up data. If data is missing (N/A), acknowledge it.
Use Telegram-compatible formatting: *bold*, _italic_, bullet points with •."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1500,
            temperature=0.4,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return (
            f"⚠️ AI analysis unavailable at the moment: {str(e)}\n\n"
            "Please try again later."
        )


def generate_comparison(stock1: StockData, stock2: StockData, user_query: str) -> str:
    """
    Generate a side-by-side comparison of two stocks using Groq.
    """
    try:
        client = get_groq_client()
        context1 = build_stock_context(stock1)
        context2 = build_stock_context(stock2)

        system_prompt = """You are StockWise AI, an expert financial analyst. 
You provide clear, comparative stock analysis using real data.
Format using Telegram markdown: *bold*, _italic_, bullet points with •."""

        user_prompt = f"""Compare these two stocks side by side based on the data below.

USER QUERY: {user_query}

--- STOCK 1 ---
{context1}

--- STOCK 2 ---
{context2}

Provide a structured comparison:
1. 📊 *Overview Comparison*
2. 💰 *Financial Metrics Comparison* (Price, Market Cap, P/E, EPS, Revenue, Margins)
3. 📈 *Growth & Profitability*
4. 🎯 *Valuation Comparison*
5. ⚠️ *Risk Comparison*
6. 🏆 *Verdict* - Which is better and why (with caveats)
7. ⚖️ *Disclaimer*

Be specific with numbers. Use bullet points for clarity."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1800,
            temperature=0.4,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq comparison error: {e}")
        return f"⚠️ Comparison analysis unavailable: {str(e)}"
