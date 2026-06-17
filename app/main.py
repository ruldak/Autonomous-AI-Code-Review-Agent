from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.logger import setup_logger, logger
from app.core.redis_client import init_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logger()
    logger.info("Starting Autonomous Code Review Agent...")
    await init_redis()
    yield
    # Shutdown
    logger.info("Shutting down Code Review Agent...")

app = FastAPI(
    title="Autonomous Code Review Agent",
    description="AI-powered code review using Groq and LangChain",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-review-agent", "phase": 1}