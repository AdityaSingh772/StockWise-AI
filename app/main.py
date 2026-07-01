import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config.settings import settings
from app.utils.helpers import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Lifespan (startup / shutdown events)
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("🚀 StockWise AI starting up...")

    # Validate required config
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("⚠️  TELEGRAM_BOT_TOKEN not set. Bot will not function.")
    if not settings.GROQ_API_KEY:
        logger.warning("⚠️  GROQ_API_KEY not set. AI analysis will not function.")

    # In production with webhook: just start FastAPI
    # In development with polling: start the bot in polling mode
    polling_task = None
    if settings.ENV == "development" and settings.TELEGRAM_BOT_TOKEN:
        polling_task = asyncio.create_task(_run_polling())
        logger.info("🤖 Starting Telegram bot in polling mode...")

    logger.info(f"✅ StockWise AI ready on port {settings.PORT}")
    yield

    # Shutdown
    logger.info("🛑 StockWise AI shutting down...")
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass


async def _run_polling():
    """Run Telegram bot in long-polling mode (for local development)."""
    from app.telegram.bot import build_telegram_app
    try:
        app = build_telegram_app()
        await app.initialize()
        await app.start()
        logger.info("🤖 Telegram bot polling started.")
        await app.updater.start_polling(drop_pending_updates=True)
        # Keep running until cancelled
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Polling task cancelled.")
        raise
    except Exception as e:
        logger.error(f"Polling error: {e}")


# ──────────────────────────────────────────────
# FastAPI Application
# ──────────────────────────────────────────────

app = FastAPI(
    title="StockWise AI",
    description=(
        "An AI-powered Telegram bot that provides real-time stock analysis, "
        "company insights, and financial reports using natural language.\n\n"
        "Powered by **yfinance** + **Groq (Llama 3)** + **LangGraph**."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1")


# ──────────────────────────────────────────────
# Root endpoint
# ──────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "StockWise AI",
        "version": "1.0.0",
        "description": "AI-powered stock analysis Telegram bot",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
