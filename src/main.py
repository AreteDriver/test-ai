from fastapi import FastAPI
from src.api import router as api_router

app = FastAPI(title="AI Workflow Orchestrator", version="0.2.0")
app.include_router(api_router, prefix="/api")
