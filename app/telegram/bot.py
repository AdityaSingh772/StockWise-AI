import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction
from app.config.settings import settings
from app.graph.workflow import run_workflow
from app.prompts.templates import (
    get_welcome_message,
    get_help_message,
    get_analyzing_message,
    get_error_message,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Command Handlers
# ──────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    user_name = user.first_name if user else "Investor"
    welcome = get_welcome_message()
    await update.message.reply_text(
        f"👋 Hello, *{user_name}*!\n\n{welcome}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        get_help_message(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def analyze_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze <stock> command."""
    user = update.effective_user
    args = context.args

    if not args:
        await update.message.reply_text(
            "❓ Please provide a stock name or ticker.\n\nExample: `/analyze Apple` or `/analyze TSLA`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    query = " ".join(args)
    await _process_analysis(update, query, user)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all regular text messages."""
    user = update.effective_user
    message_text = update.message.text.strip()

    if not message_text:
        return

    await _process_analysis(update, message_text, user)


# ──────────────────────────────────────────────
# Core Analysis Processing
# ──────────────────────────────────────────────

async def _process_analysis(update: Update, query: str, user) -> None:
    """
    Core processing: sends typing indicator, runs workflow, sends report.
    """
    chat_id = update.effective_chat.id
    user_name = user.first_name if user else None

    # Send "analyzing..." message
    thinking_msg = await update.message.reply_text(
        get_analyzing_message(query),
        parse_mode=ParseMode.MARKDOWN,
    )

    # Send typing action
    await update.effective_chat.send_action(ChatAction.TYPING)

    try:
        # Run the full LangGraph workflow
        result = await run_workflow(
            user_message=query,
            chat_id=chat_id,
            user_name=user_name,
        )

        report = result.get("report", "")

        # Delete the "analyzing..." message
        try:
            await thinking_msg.delete()
        except Exception:
            pass

        # Send the report in chunks if too long (Telegram limit: 4096 chars)
        if report:
            await send_long_message(update, report)
        else:
            await update.message.reply_text(
                get_error_message("No report generated."),
                parse_mode=ParseMode.MARKDOWN,
            )

    except Exception as e:
        logger.error(f"Error processing analysis: {e}")
        try:
            await thinking_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(
            get_error_message(str(e)),
            parse_mode=ParseMode.MARKDOWN,
        )


async def send_long_message(update: Update, text: str, chunk_size: int = 4000) -> None:
    """Send a long message in chunks, respecting Telegram's 4096 char limit."""
    if len(text) <= chunk_size:
        try:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Fallback without markdown if parsing fails
            await update.message.reply_text(text)
        return

    # Split by newlines to avoid breaking mid-sentence
    chunks = []
    current_chunk = ""
    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += ("\n" if current_chunk else "") + line

    if current_chunk:
        chunks.append(current_chunk)

    for i, chunk in enumerate(chunks):
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text(chunk)
        if i < len(chunks) - 1:
            await asyncio.sleep(0.3)  # Small delay between chunks


# ──────────────────────────────────────────────
# Build the Telegram Application
# ──────────────────────────────────────────────

def build_telegram_app() -> Application:
    """Build and configure the Telegram bot application."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

    app = Application.builder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("analyze", analyze_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Telegram bot application built successfully.")
    return app


async def process_update_from_webhook(update_data: dict) -> None:
    """Process a single update received from webhook."""
    app = build_telegram_app()
    await app.initialize()
    update = Update.de_json(update_data, app.bot)
    await app.process_update(update)
    await app.shutdown()
