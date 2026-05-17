from fastapi import FastAPI
from backend.api.routes import router as api_router

app = FastAPI(title="WhatsApp Automation API")

# Include the API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "WhatsApp Automation Backend is running"}
