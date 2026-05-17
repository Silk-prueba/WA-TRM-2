from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.api.routes import router as api_router
from backend.services.scheduler import setup_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize and start the scheduler
    scheduler = setup_scheduler()
    yield
    # Shutdown: Stop the scheduler
    scheduler.shutdown()

app = FastAPI(title="WhatsApp Automation API", lifespan=lifespan)

# Include the API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "WhatsApp Automation Backend is running"}
