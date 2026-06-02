from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from backend.api.routes import router as api_router
from backend.services.scheduler import setup_scheduler

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = setup_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="WhatsApp Automation API", lifespan=lifespan)

app.include_router(api_router, prefix="/api")

@app.post("/api/trigger")
async def trigger_now(background_tasks: BackgroundTasks):
    """Dispara el envío inmediatamente."""
    from backend.services.scheduler import send_daily_exchange_rate
    background_tasks.add_task(send_daily_exchange_rate)
    return {"message": "Enviando..."}

@app.post("/api/config")
async def update_config(chat_id: str = None, hour: int = None, minute: int = None):
    """Actualiza chat ID y/o hora del scheduler en caliente."""
    from apscheduler.triggers.cron import CronTrigger
    from backend.core.config import settings

    if chat_id:
        settings.test_chat_id = chat_id

    if hour is not None:
        job = scheduler.get_job("daily_exchange_rate_job")
        m = minute if minute is not None else 0
        job.reschedule(CronTrigger(hour=hour, minute=m, timezone="America/Bogota"))
        next_run = str(job.next_run_time)
    else:
        next_run = str(scheduler.get_job("daily_exchange_rate_job").next_run_time)

    return {
        "chat_id": settings.test_chat_id,
        "next_run": next_run
    }

@app.get("/")
def read_root():
    return {"message": "WhatsApp Automation Backend is running"}
