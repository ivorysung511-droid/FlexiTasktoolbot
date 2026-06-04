import os
import logging
import sys
import asyncio
import time
from datetime import datetime
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Setup Stream Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 2. Tool Logic Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and presents the tool manual."""
    welcome = (
        "🧰 **Welcome to FlexiTask Tool Bot!**\n\n"
        "I am a standalone processing utility running 24/7 on a Render worker.\n"
        "Send me any text command below to format data instantly with no external APIs.\n\n"
        "⚙️ **Available Utilities:**\n"
        "/upper <text> - Convert text to UPPERCASE\n"
        "/lower <text> - Convert text to lowercase\n"
        "/time - Get current UTC time and Unix timestamp\n"
        "/hash <text> - Generate an instant SHA-256 string hash\n"
        "/length <text> - Count total characters and words"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def upper_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide text. Example: `/upper hello world`", parse_mode="Markdown")
        return
    await update.message.reply_text(f"🔠 **Result:**\n`{text.upper()}`", parse_mode="Markdown")

async def lower_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide text. Example: `/lower HELLO WORLD`", parse_mode="Markdown")
        return
    await update.message.reply_text(f"🔡 **Result:**\n`{text.lower()}`", parse_mode="Markdown")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.utcnow()
    unix_ts = int(time.time())
    response = (
        "🕒 **System Time Engine Update:**\n\n"
        f"📅 **UTC ISO:** `{now.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n"
        f"⏳ **Unix Epoch:** `{unix_ts}`"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide text to hash. Example: `/hash secret`", parse_mode="Markdown")
        return
    hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()
    await update.message.reply_text(f"🔒 **SHA-256 Hash:**\n`{hashed}`", parse_mode="Markdown")

async def length_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide text. Example: `/length contextual testing`", parse_mode="Markdown")
        return
    char_count = len(text)
    word_count = len(text.split())
    await update.message.reply_text(
        f"📊 **Text Analytics:**\n\n"
        f"• **Characters:** `{char_count}` (including spaces)\n"
        f"• **Words:** `{word_count}`", 
        parse_mode="Markdown"
    )

async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles stray text messages by reminding users of tool commands."""
    await update.message.reply_text(
        "💡 **Unrecognized Input.**\nUse commands like `/upper`, `/hash`, `/time`, or `/length` to process data."
    )

async def error_monitor(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Worker intercepted an update error:", exc_info=context.error)

# 3. Secure Production Execution Context (Bypassing Broken run_polling Engine)
async def run_worker_engine(token: str) -> None:
    """Builds application environment and handles custom low-level long polling safely."""
    logger.info("Assembling core application pipeline...")
    application = Application.builder().token(token).build()

    # Bind utilities
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("upper", upper_command))
    application.add_handler(CommandHandler("lower", lower_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("hash", hash_command))
    application.add_handler(CommandHandler("length", length_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message))
    application.add_error_handler(error_monitor)

    logger.info("Starting safe underlying network services...")
    await application.initialize()
    
    # Custom low-level polling to completely ignore get_event_loop errors inside Python 3.14
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await application.start()
    
    logger.info("FlexiTask Tool Bot is completely live and monitoring updates.")
    
    # Infinite background hold loop
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown instruction picked up. Terminating worker state...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main() -> None:
    """Explicitly generates and injects the global thread event loop."""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.critical("Fatal Configuration Missing: 'TELEGRAM_TOKEN' variable must be set in Render.")
        sys.exit(1)

    try:
        # Create a completely fresh processing loop manually
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run our server loop directly through our loop assignment
        loop.run_until_complete(run_worker_engine(TOKEN))
    except Exception as e:
        logger.critical(f"Global runtime exception caught: {e}", exc_info=True)
    finally:
        if 'loop' in locals() and loop.is_running():
            loop.close()
            logger.info("Event loop dropped smoothly.")

if __name__ == '__main__':
    main()
