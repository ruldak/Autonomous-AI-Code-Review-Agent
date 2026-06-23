from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.logger import setup_logger, logger
from app.core.redis_client import init_redis
from app.api.webhooks import router as webhooks_router

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
    version="0.7.0",
    lifespan=lifespan
)

app.include_router(webhooks_router, tags=["Webhooks"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-review-saas", "phase": 7}