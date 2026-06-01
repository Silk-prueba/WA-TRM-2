import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.core.config import settings
from backend.services.waha import WahaClient
from backend.services.exchange_rate import get_exchange_rate_message
from backend.services.holidays import is_colombian_holiday

logger = logging.getLogger(__name__)


async def send_daily_exchange_rate():
    """
    Async job: fetches all indicators and sends via WhatsApp.
    Skips on Colombian public holidays.
    Supports multiple chat IDs via WHATSAPP_CHAT_IDS (comma-separated).
    """
    logger.info("Executing daily exchange rate job...")

    if is_colombian_holiday():
        logger.info("Today is a Colombian public holiday — skipping message.")
        return

    # Support multiple chat IDs: "573001234567@c.us,120363xxx@g.us"
    raw = getattr(settings, "whatsapp_chat_ids", None) or settings.test_chat_id or ""
    chat_ids = [cid.strip() for cid in raw.split(",") if cid.strip()]

    if not chat_ids:
        logger.warning("No chat IDs configured. Set WHATSAPP_CHAT_IDS in .env")
        return

    try:
        message = get_exchange_rate_message()
        client = WahaClient()
        for chat_id in chat_ids:
            try:
                response = await client.send_message(chat_id=chat_id, text=message)
                logger.info(f"Sent to {chat_id}: {response}")
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error building message: {e}")


def setup_scheduler():
    """
    Initializes and starts the APScheduler with timezone set to Bogotá.
    """
    scheduler = AsyncIOScheduler(timezone="America/Bogota")

    try:
        hour, minute = map(int, settings.schedule_time.split(":"))
    except ValueError:
        logger.error(f"Invalid SCHEDULE_TIME: '{settings.schedule_time}'. Using 08:00.")
        hour, minute = 8, 0

    scheduler.add_job(
        send_daily_exchange_rate,
        CronTrigger(hour=hour, minute=minute, timezone="America/Bogota"),
        id="daily_exchange_rate_job",
        replace_existing=True,
        misfire_grace_time=300,  # 5 min tolerance (server reboots, etc.)
    )

    scheduler.start()
    logger.info(f"Scheduler started. Job fires daily at {hour:02d}:{minute:02d} Bogotá time.")
    return scheduler
