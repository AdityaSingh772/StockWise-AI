import logging
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models.schemas import AnalysisRequest, AnalysisResponse, WebhookPayload
from app.agents.stock_agent import StockAnalysisAgent
from app.telegram.bot import process_update_from_webhook
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()
agent = StockAnalysisAgent()


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment platforms."""
    return {
        "status": "healthy",
        "service": "StockWise AI",
        "version": "1.0.0",
    }


# ──────────────────────────────────────────────
# Stock Analysis REST API
# ──────────────────────────────────────────────

@router.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock via REST API.
    Accepts a user message in natural language and returns an AI-generated report.
    """
    if not request.user_message.strip():
        raise HTTPException(status_code=400, detail="user_message cannot be empty.")

    logger.info(f"REST /analyze | query='{request.user_message}'")
    response = await agent.analyze(request)
    return response


@router.get("/analyze/{ticker}", tags=["Analysis"])
async def analyze_stock_by_ticker(ticker: str, chat_id: int = 0):
    """
    Quick analysis endpoint by ticker symbol via GET request.
    Useful for testing or simple integrations.
    """
    request = AnalysisRequest(
        user_message=f"Analyze {ticker.upper()}",
        chat_id=chat_id,
    )
    logger.info(f"REST GET /analyze/{ticker}")
    response = await agent.analyze(request)
    return response


# ──────────────────────────────────────────────
# Telegram Webhook
# ──────────────────────────────────────────────

@router.post("/webhook", tags=["Telegram Webhook"])
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telegram webhook endpoint. Receives updates from Telegram and
    processes them asynchronously in the background.
    """
    try:
        update_data = await request.json()
        logger.info(f"Webhook received update_id: {update_data.get('update_id')}")
        # Process in background to return 200 quickly to Telegram
        background_tasks.add_task(process_update_from_webhook, update_data)
        return JSONResponse(content={"ok": True}, status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(content={"ok": False, "error": str(e)}, status_code=200)


@router.get("/set-webhook", tags=["Telegram Webhook"])
async def set_webhook():
    """
    Register the webhook URL with Telegram.
    Call this once after deployment.
    """
    from telegram import Bot
    webhook_url = settings.WEBHOOK_URL
    if not webhook_url:
        raise HTTPException(
            status_code=400,
            detail="WEBHOOK_URL is not configured in environment variables."
        )

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    full_url = f"{webhook_url.rstrip('/')}/webhook"
    result = await bot.set_webhook(url=full_url)

    return {
        "success": result,
        "webhook_url": full_url,
        "message": "Webhook registered successfully!" if result else "Failed to set webhook.",
    }


@router.get("/delete-webhook", tags=["Telegram Webhook"])
async def delete_webhook():
    """Remove the registered webhook (useful for switching to polling mode)."""
    from telegram import Bot
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    result = await bot.delete_webhook()
    return {"success": result, "message": "Webhook deleted." if result else "Failed."}
