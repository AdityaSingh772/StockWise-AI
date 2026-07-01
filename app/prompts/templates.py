def get_welcome_message() -> str:
    return """🤖 *Welcome to StockWise AI!*

I'm your AI-powered financial analyst. I provide real-time stock analysis, company insights, and AI-generated reports — all through natural language.

*What I can do:*
• 📊 Analyze any stock or company
• 📈 Compare two stocks side-by-side
• 💡 Provide AI insights using Llama 3
• 📉 Show key financial metrics & trends

*Try asking:*
• `Analyze Apple`
• `What is Tesla's PE ratio?`
• `Compare Google vs Microsoft`
• `Show me Amazon's performance`
• `Is Reliance overvalued?`

Type /help for the full command list.

_Powered by yfinance + Groq (Llama 3) + LangGraph_ 🚀"""


def get_help_message() -> str:
    return """📖 *StockWise AI — Help Guide*

━━━━━━━━━━━━━━━━━━━━━━
*📌 Commands*
━━━━━━━━━━━━━━━━━━━━━━
• /start — Start the bot & welcome message
• /help — Show this help guide
• /analyze <stock> — Analyze a specific stock

━━━━━━━━━━━━━━━━━━━━━━
*💬 Natural Language Examples*
━━━━━━━━━━━━━━━━━━━━━━
• `Analyze Tesla`
• `What is the PE ratio of TCS?`
• `Compare Apple and Microsoft`
• `Show me today's movement of Amazon`
• `Is Reliance overvalued?`
• `NVDA` _(just the ticker symbol)_

━━━━━━━━━━━━━━━━━━━━━━
*📊 Report Includes*
━━━━━━━━━━━━━━━━━━━━━━
✅ Company Overview
✅ Key Financial Metrics
✅ Growth Analysis
✅ Valuation (P/E, P/B, P/S)
✅ Risk Factors
✅ Recent Price Performance
✅ AI Summary & Outlook

━━━━━━━━━━━━━━━━━━━━━━
*🌍 Supported Markets*
━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 US Stocks (NASDAQ, NYSE)
🇮🇳 Indian Stocks (NSE — add .NS suffix)
🌐 Global stocks via ticker symbols

_⚠️ Disclaimer: This is not financial advice. Always do your own research._"""


def get_analyzing_message(query: str) -> str:
    return f"""🔍 *Analyzing:* `{query}`

⏳ Fetching real-time data and generating AI report...
_This may take a few seconds._"""


def get_error_message(error: str) -> str:
    return f"""❌ *Analysis Failed*

{error}

Please try again or use /help for guidance."""


def get_fetch_error_message(ticker: str) -> str:
    return f"""❌ Could not fetch data for `{ticker}`.

Possible reasons:
• Invalid ticker symbol
• Stock market is closed (data may be delayed)
• Network issue

Try:
• Using the official ticker symbol (e.g., `AAPL` for Apple)
• Indian stocks: add `.NS` suffix (e.g., `TCS.NS`)
• Use /help for supported formats"""
