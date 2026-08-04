"""
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000
or:
    bash scripts/run_server.sh
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.automation.scheduler import start_scheduler, stop_scheduler
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Workflow Automation Platform...")
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("Shutting down AI Workflow Automation Platform.")


app = FastAPI(
    title="AI Workflow Automation Platform",
    description="Multi-agent workflow automation powered by LangGraph, FastAPI, Ollama, and MCP.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve the dashboard as static files at /dashboard
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


@app.get("/")
async def root():
    return {
        "message": "AI Workflow Automation Platform is running.",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "env": settings.app_env,
    }
