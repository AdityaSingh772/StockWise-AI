# 📈 StockWise AI

> An AI-powered Telegram bot that provides **real-time stock analysis**, company insights, and financial reports using natural language.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-Llama%203-purple)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🚀 Overview

StockWise AI is a production-ready Telegram bot powered by:
- **FastAPI** — REST API server and webhook handler
- **LangGraph** — Multi-step agentic workflow (intent → extraction → fetch → analyze → report)
- **Groq (Llama 3.3-70B)** — AI-generated financial insights
- **yfinance** — Real-time & historical stock data
- **python-telegram-bot** — Telegram integration

Users can ask about any stock in **natural language** and receive a comprehensive AI-generated report.

---

## 🏗️ Project Structure

```
stockwise-ai/
├── app/
│   ├── api/            # FastAPI routes
│   ├── graph/          # LangGraph workflow & nodes
│   ├── services/       # yfinance & Groq data services
│   ├── agents/         # AI agent logic
│   ├── prompts/        # LLM prompt templates
│   ├── models/         # Pydantic models
│   ├── telegram/       # Telegram bot logic
│   ├── utils/          # Helpers & logging
│   ├── config/         # Settings & env config
│   └── main.py         # FastAPI app entrypoint
├── tests/              # Unit tests
├── .env.example        # Environment template
├── Dockerfile
├── docker-compose.yml
├── render.yaml         # Render deployment config
├── requirements.txt
└── main.py             # Run script
```

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| API Server | FastAPI + Uvicorn |
| AI Workflow | LangGraph |
| LLM | Groq API (Llama 3.3-70B) |
| Stock Data | yfinance |
| Telegram | python-telegram-bot |
| Deployment | Docker + Render |

---

## 🔄 Workflow (LangGraph)

```
1. Receive Message
       ↓
2. Intent Classification  (analyze / compare / help)
       ↓
3. Entity Extraction      (company name → ticker symbol)
       ↓
4. Fetch Live Data        (yfinance: price, P/E, revenue, etc.)
       ↓
5. Generate AI Analysis   (Groq Llama 3)
       ↓
6. Create Report
       ↓
7. Send via Telegram
```

---

## 📋 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/stockwise-ai.git
cd stockwise-ai
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
PORT=8000
ENV=development
```

**Get your keys:**
- Telegram token: [@BotFather](https://t.me/BotFather) → `/newbot`
- Groq API key: [console.groq.com](https://console.groq.com)

### 3. Run Locally

```bash
python main.py
```

The bot will start in **polling mode** automatically in `development` env.
API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker

```bash
# Build & run
docker-compose up --build

# Run in background
docker-compose up -d
```

---

## ☁️ Deploy to Render

1. Push to GitHub
2. Connect repo to [render.com](https://render.com)
3. Select `render.yaml` for auto-configuration
4. Add env vars in Render dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `GROQ_API_KEY`
   - `WEBHOOK_URL` = `https://your-app.onrender.com`
5. After deploy, register webhook:
   ```
   GET https://your-app.onrender.com/api/v1/set-webhook
   ```

---

## 💬 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help guide |
| `/analyze <stock>` | Analyze a stock |

### Natural Language Examples
- `Analyze Apple`
- `What is Tesla's PE ratio?`
- `Compare Google vs Microsoft`
- `Is Reliance overvalued?`
- `Show me Amazon's performance`
- `NVDA` _(just the ticker)_

---

## 📊 Report Includes

- 📊 Company Overview
- 💰 Key Financial Metrics (Price, Market Cap, P/E, EPS, Revenue)
- 📈 Growth Analysis
- 🎯 Valuation (P/E, P/B, P/S ratios)
- ⚠️ Risk Factors
- 📉 Recent Price Performance (52-week range)
- 🤖 AI Summary & Outlook (Bullish/Neutral/Bearish)
- ⚖️ Disclaimer

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🌍 Supported Markets

- 🇺🇸 **US Stocks**: NASDAQ, NYSE (AAPL, TSLA, GOOGL, etc.)
- 🇮🇳 **Indian Stocks**: NSE (TCS.NS, RELIANCE.NS, INFY.NS, etc.)
- 🌐 **Global**: Any valid Yahoo Finance ticker symbol

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

This bot provides AI-generated financial information for **educational purposes only**. It is **not financial advice**. Always conduct your own research before making investment decisions.

---

*Built with ❤️ using Python, FastAPI, LangGraph & Groq*
