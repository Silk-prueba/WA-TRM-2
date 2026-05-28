import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.core.config import settings
from backend.services.waha import WahaClient
from backend.services.exchange_rate import get_exchange_rate_message
from backend.services.holidays import is_colombian_holiday

logger = logging.getLogger(__name__)

def send_daily_exchange_rate():
    """
    Job function to fetch the exchange rate and send it via WhatsApp.
    Skips execution on Colombian public holidays.
    """
    logger.info("Executing daily exchange rate job...")

    if is_colombian_holiday():
        logger.info("Today is a Colombian public holiday — skipping message.")
        return

    try:
        message = get_exchange_rate_message()
        client = WahaClient()

        # Send message to the configured test chat ID
        if settings.test_chat_id:
            response = client.send_message(chat_id=settings.test_chat_id, text=message)
            logger.info(f"Message sent successfully: {response}")
        else:
            logger.warning("TEST_CHAT_ID is not configured in environment variables.")
    except Exception as e:
        logger.error(f"Error in daily exchange rate job: {e}")

def setup_scheduler():
    """
    Initializes and starts the APScheduler.
    """
    scheduler = AsyncIOScheduler()
    
    # Parse the configured schedule_time (e.g., "08:00")
    try:
        hour, minute = map(int, settings.schedule_time.split(':'))
    except ValueError:
        logger.error(f"Invalid SCHEDULE_TIME format: {settings.schedule_time}. Using default 08:00.")
        hour, minute = 8, 0

    # Schedule the job to run daily at the specified time
    trigger = CronTrigger(hour=hour, minute=minute)
    
    scheduler.add_job(
        send_daily_exchange_rate,
        trigger=trigger,
        id="daily_exchange_rate_job",
        replace_existing=True,
        misfire_grace_time=60
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Daily job configured for {hour:02d}:{minute:02d}.")
    return scheduler
