# Project: Epic Games Notifier | Author: github.com/waterk
import json
import logging
from datetime import datetime, timezone
import httpx
import os
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import asyncio
import aiofiles
import re
from dotenv import load_dotenv

# Load variables from .env file at startup
load_dotenv()

def escape_markdown(text: str) -> str:
    """Escapes markdown v2 special characters."""
    if not text: return ""
    escape_chars = r"_*[]()~`>#+=|{}.!"
    return re.sub(r"([_*\[\]()~`>#+=|{}.!])", r"\\\1", text).replace("-", r"\-")

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

async def fetch_free_games():
    """Fetches currently free games from the Epic Games API."""
    free_games = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(EPIC_API_URL)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"Error fetching data from Epic Games API: {e}")
        return free_games

    try:
        elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
    except Exception as e:
        logger.error(f"Error parsing Epic Games API response structure: {e}")
        return free_games

    now_utc = datetime.now(timezone.utc)

    for item in elements:
        promotions = item.get("promotions")
        if not promotions:
            continue

        promo_offers = promotions.get("promotionalOffers")
        if not promo_offers:
            continue

        is_free = False
        for offer in promo_offers:
            for promo in offer.get("promotionalOffers", []):
                discount_setting = promo.get("discountSetting", {})
                if discount_setting.get("discountPercentage") == 0:
                    try:
                        start_date = datetime.fromisoformat(promo.get("startDate").replace("Z", "+00:00"))
                        end_date = datetime.fromisoformat(promo.get("endDate").replace("Z", "+00:00"))
                        if start_date <= now_utc <= end_date:
                            is_free = True
                            break
                    except Exception as e:
                        logger.warning(f"Error parsing dates for game {item.get('title')}: {e}")
            if is_free:
                break

        if is_free:
            game_data = {
                "id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("description"),
            }

            # Extract Image (prefer Thumbnail or OfferImageWide)
            image_url = None
            for img in item.get("keyImages", []):
                if img.get("type") == "Thumbnail":
                    image_url = img.get("url")
                    break
            if not image_url:
                for img in item.get("keyImages", []):
                    if img.get("type") == "OfferImageWide":
                        image_url = img.get("url")
                        break
            if not image_url and item.get("keyImages"):
                image_url = item.get("keyImages")[0].get("url")
            game_data["image"] = image_url

            # Construct link
            slug = item.get("productSlug")
            if not slug:
                offer_mappings = item.get("offerMappings", [])
                if offer_mappings:
                    slug = offer_mappings[0].get("pageSlug")
            if not slug:
                catalog_ns = item.get("catalogNs", {}).get("mappings", [])
                if catalog_ns:
                    slug = catalog_ns[0].get("pageSlug")
            if not slug:
                slug = item.get("urlSlug")

            if slug:
                game_data["url"] = f"https://store.epicgames.com/en-US/p/{slug}"
            else:
                game_data["url"] = "https://store.epicgames.com/en-US/free-games"

            free_games.append(game_data)

    return free_games


SUBSCRIBERS_FILE = "subscribers.json"
SENT_GAMES_FILE = "sent_games.json"

async def load_json_file(filename: str) -> List:
    if not os.path.exists(filename):
        async with aiofiles.open(filename, "w") as f:
            await f.write("[]")
        return []
    try:
        async with aiofiles.open(filename, "r") as f:
            content = await f.read()
            return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {filename}. Returning empty list.")
        return []
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return []

async def save_json_file(filename: str, data: List):
    try:
        async with aiofiles.open(filename, "w") as f:
            await f.write(json.dumps(data, indent=2))
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")

async def get_subscribers() -> List[int]:
    return await load_json_file(SUBSCRIBERS_FILE)

async def add_subscriber(chat_id: int):
    subs = await get_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        await save_json_file(SUBSCRIBERS_FILE, subs)

async def get_sent_games() -> List[str]:
    return await load_json_file(SENT_GAMES_FILE)

async def add_sent_game(game_id: str):
    games = await get_sent_games()
    if game_id not in games:
        games.append(game_id)
        await save_json_file(SENT_GAMES_FILE, games)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds user to subscribers and sends welcome message."""
    chat_id = update.effective_chat.id
    await add_subscriber(chat_id)

    welcome_text = (
        "🎮 *Welcome to the Epic Games Free Notifier\\!*\n\n"
        "I will notify you automatically every Thursday when new free games are available\\.\n\n"
        "You can also use /fetch at any time to see the currently free games\\.\n\n"
        "🚀 Developed by [github\\.com/waterk](https://github.com/waterk)"
    )

    await update.message.reply_text(
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )

async def fetch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually fetch and send currently free games."""
    chat_id = update.effective_chat.id
    await add_subscriber(chat_id)

    await update.message.reply_text("Fetching currently free games\\.\\.\\.", parse_mode=ParseMode.MARKDOWN_V2)

    games = await fetch_free_games()

    if not games:
        await update.message.reply_text("No free games are currently available\\.\\.\\.🚀 Developed by [github\\.com/waterk](https://github.com/waterk)", parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        return

    for game in games:
        await send_game_message(context.bot, chat_id, game)

async def send_game_message(bot, chat_id: int, game: dict):
    """Formats and sends a rich-media message for a game."""
    caption = (
        f"🎮 *{escape_markdown(game['title'])}*\n\n"
        f"{escape_markdown(game['description'])}\n\n"
        f"🚀 Developed by [github\\.com/waterk](https://github.com/waterk)"
    )

    keyboard = [[InlineKeyboardButton("Claim Game", url=game['url'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if game.get('image'):
            await bot.send_photo(
                chat_id=chat_id,
                photo=game['image'],
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

async def auto_broadcast(context: ContextTypes.DEFAULT_TYPE):
    """Fetches free games and broadcasts new ones to subscribers."""
    logger.info("Starting auto-broadcast task...")
    games = await fetch_free_games()
    sent_games = await get_sent_games()
    subscribers = await get_subscribers()

    new_games = [g for g in games if g["id"] not in sent_games]

    if not new_games:
        logger.info("No new free games to broadcast.")
        return

    for game in new_games:
        for chat_id in subscribers:
            try:
                await send_game_message(context.bot, chat_id, game)
            except Exception as e:
                logger.error(f"Failed to broadcast to {chat_id}: {e}")

        # After broadcasting, add to sent log
        await add_sent_game(game["id"])

    logger.info("Broadcast complete.")

def main():
    """Main execution function."""
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable is not set.")
        return

    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fetch", fetch_command))

    # Scheduler: run every Thursday at 21:35 IST
    import datetime
    import pytz

    timezone = pytz.timezone("Asia/Kolkata")
    # JobQueue runs in UTC by default, but we can provide timezone info to run_daily
    # run_daily takes datetime.time, and a tuple of days (0=Mon, ..., 3=Thu, ...)
    target_time = datetime.time(hour=21, minute=35, tzinfo=timezone)
    application.job_queue.run_daily(
        auto_broadcast,
        time=target_time,
        days=(3,)  # 3 = Thursday
    )

    logger.info("Bot started and scheduler initialized.")
    application.run_polling()

if __name__ == "__main__":
    main()
