#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot Listener for Canvas Automation
Listens for commands like TEST and triggers the pipeline.
Uses python-telegram-bot library with token filtering for security.
"""

import os
import sys
import re
import logging
import subprocess
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from Secrets
env_path = Path(__file__).parent / "Secrets" / ".env"
load_dotenv(env_path)

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configure logging with token filter
class TokenFilter(logging.Filter):
    """Filter to hide sensitive tokens from logs."""
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Hide Telegram bot tokens (format: 123456789:ABC...)
            record.msg = re.sub(r'bot\d+:[A-Za-z0-9_-]+', 'bot***TOKEN_HIDDEN***', record.msg)
            record.msg = re.sub(r'\d{10}:[A-Za-z0-9_-]{35}', '***TOKEN_HIDDEN***', record.msg)
            if record.args:
                new_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        arg = re.sub(r'bot\d+:[A-Za-z0-9_-]+', 'bot***TOKEN_HIDDEN***', arg)
                        arg = re.sub(r'\d{10}:[A-Za-z0-9_-]{35}', '***TOKEN_HIDDEN***', arg)
                    new_args.append(arg)
                record.args = tuple(new_args)
        return True

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Apply token filter to all loggers
for handler in logging.root.handlers:
    handler.addFilter(TokenFilter())

# Suppress verbose HTTP logs that might show tokens
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Paths
AUTOMATIONS_ROOT = Path(__file__).resolve().parents[1]
PLANNER_SCRIPT = AUTOMATIONS_ROOT / "planners" / "daily-canvas-planner.py"

# Get credentials from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def run_pipeline():
    """Run the daily canvas planner pipeline with live output."""
    script_path = PLANNER_SCRIPT
    try:
        # Run with output streaming to terminal
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1  # Line buffered
        )

        output_lines = []
        # Stream output in real-time
        for line in process.stdout:
            print(line, end='', flush=True)
            output_lines.append(line)

        process.wait(timeout=300)
        return process.returncode == 0, ''.join(output_lines), ""
    except subprocess.TimeoutExpired:
        process.kill()
        return False, "", "Pipeline timed out after 5 minutes"
    except Exception as e:
        return False, "", str(e)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Canvas Automation Bot\n\n"
        "Commands:\n"
        "• TEST - Run the Canvas pipeline\n"
        "• /status - Check bot status\n"
        "• /help - Show this message"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await start_command(update, context)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    await update.message.reply_text(
        "[OK] Bot Status: Online\n\n"
        "Available Commands:\n"
        "• TEST - Run Canvas pipeline\n"
        "• /status - This message\n"
        "• /help - Show help\n\n"
        "All systems operational."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    # Only respond to authorized chat
    if str(update.effective_chat.id) != str(TELEGRAM_CHAT_ID):
        logger.warning(f"Unauthorized chat ID: {update.effective_chat.id}")
        return

    text = update.message.text.strip().upper()

    if text == "TEST":
        await update.message.reply_text("Running Canvas pipeline...")
        logger.info("Running pipeline...")

        success, stdout, stderr = run_pipeline()

        if success:
            await update.message.reply_text("[OK] Pipeline completed!")
        else:
            error_msg = stderr[:500] if stderr else "Unknown error"
            await update.message.reply_text(f"[ERROR] Pipeline failed:\n{error_msg}")
            logger.error(f"Pipeline failed: {stderr}")

    elif text == "STATUS":
        await status_command(update, context)

    elif text == "HELP":
        await start_command(update, context)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("[ERROR] An error occurred. Please try again.")


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in Secrets/.env")
        sys.exit(1)

    if not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_CHAT_ID not set in Secrets/.env")
        sys.exit(1)

    logger.info("Starting Canvas Automation Bot...")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    print("\n" + "=" * 50)
    print("Canvas Automation Bot is running!")
    print("Send TEST to run the pipeline")
    print("=" * 50 + "\n")

    # Python 3.14+ requires explicit event loop setup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
