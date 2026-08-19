import logging
import re

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database import init_db, save_lookup, get_stats


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

USERNAME_PATTERN = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")


def normalize_username(value: str) -> str:
    value = value.strip()

    if not value.startswith("@"):
        value = "@" + value

    return value


def valid_username(value: str) -> bool:
    return bool(USERNAME_PATTERN.fullmatch(value))


def format_number(value):
    if value is None:
        return "Unavailable"

    return f"{value:,}"


# --------------------------------------------------
# /start
# --------------------------------------------------

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        "📢 CHANNEL INFO BOT\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "I can retrieve channel information available "
        "through Telegram's Bot API.\n\n"
        "🔎 Example:\n"
        "/info @telegram\n\n"
        "📚 Commands:\n"
        "/start - Start the bot\n"
        "/info @channel - Channel information\n"
        "/stats - Your lookup statistics\n"
        "/help - Show help"
    )

    await update.message.reply_text(text)


# --------------------------------------------------
# /help
# --------------------------------------------------

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        "📚 HELP\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Use the following command:\n\n"
        "/info @channelusername\n\n"
        "Example:\n"
        "/info @telegram\n\n"
        "The bot only returns information that Telegram's "
        "Bot API allows it to access.\n\n"
        "It cannot reveal private owner information, "
        "hidden administrator information, phone numbers, "
        "IP addresses, or other protected data."
    )

    await update.message.reply_text(text)


# --------------------------------------------------
# /info
# --------------------------------------------------

async def info_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a public channel username.\n\n"
            "Example:\n"
            "/info @telegram"
        )
        return

    raw_username = context.args[0]
    username = normalize_username(raw_username)

    if not valid_username(username):
        await update.message.reply_text(
            "❌ Invalid Telegram username.\n\n"
            "Example:\n"
            "/info @telegram"
        )
        return

    waiting_message = await update.message.reply_text(
        "🔎 Getting channel information..."
    )

    try:
        chat = await context.bot.get_chat(username)

        # Only channels
        if chat.type != ChatType.CHANNEL:
            await waiting_message.edit_text(
                "❌ This username does not belong to a Telegram channel."
            )
            return

        # Subscriber/member count
        member_count = None

        try:
            member_count = await context.bot.get_chat_member_count(
                chat.id
            )
        except Exception as error:
            logger.warning(
                "Could not get member count: %s",
                error,
            )

        title = chat.title or "Unavailable"

        if chat.username:
            public_username = f"@{chat.username}"
        else:
            public_username = "Unavailable"

        description = chat.description or "No description"

        # Protect message length
        if len(description) > 700:
            description = description[:700] + "..."

        invite_link = "Unavailable"

        if chat.username:
            invite_link = f"https://t.me/{chat.username}"

        text = (
            "📢 CHANNEL INFORMATION\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"📛 Name: {title}\n"
            f"🔗 Username: {public_username}\n"
            f"🆔 ID: <code>{chat.id}</code>\n"
            f"📂 Type: {chat.type}\n"
            f"👥 Subscribers: {format_number(member_count)}\n\n"
            "📝 Description:\n"
            f"{description}\n\n"
            f"🌐 Link: {invite_link}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "ℹ️ Source: Telegram Bot API"
        )

        await waiting_message.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        # Save lookup
        user = update.effective_user

        if user:
            save_lookup(
                telegram_user_id=user.id,
                username=user.username,
                channel_id=chat.id,
                channel_username=chat.username,
                channel_title=chat.title,
            )

    except Exception as error:
        logger.warning(
            "Channel lookup failed for %s: %s",
            username,
            error,
        )

        await waiting_message.edit_text(
            "❌ Could not access this channel.\n\n"
            "Possible reasons:\n"
            "• The username is incorrect\n"
            "• The channel does not exist\n"
            "• The channel is private\n"
            "• Telegram does not allow the requested information\n"
            "• Telegram temporarily rejected the request\n\n"
            "Try a public channel, for example:\n"
            "/info @telegram"
        )


# --------------------------------------------------
# /stats
# --------------------------------------------------

async def stats_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    user = update.effective_user

    if not user:
        return

    total = get_stats(user.id)

    await update.message.reply_text(
        "📊 YOUR STATISTICS\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔎 Channel lookups: {total}\n\n"
        "Database: SQLite"
    )


# --------------------------------------------------
# Error handler
# --------------------------------------------------

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Unhandled exception: %s",
        context.error,
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not configured."
        )

    # Create database
    init_db()

    # Build Telegram application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler("start", start_command)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("info", info_command)
    )

    application.add_handler(
        CommandHandler("stats", stats_command)
    )

    # Errors
    application.add_error_handler(error_handler)

    logger.info("Channel Info Bot started.")

    # Long polling
    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
