from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.logger import setup_logger, logger
from app.core.redis_client import init_redis
from app.api.webhooks import router as webhooks_router
from app.api.reviews import router as reviews_router
from fastapi.middleware.cors import CORSMiddleware

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
    version="0.7.1",
    lifespan=lifespan
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allowed domains list
    allow_credentials=True,          # Allow cookies and authentication headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all request headers
)

app.include_router(webhooks_router, tags=["Webhooks"])
app.include_router(reviews_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-review-saas", "phase": 7}