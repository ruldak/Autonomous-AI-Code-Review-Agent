import logging
import structlog
from app.config import settings

def setup_logger():
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            # Gunakan ConsoleRenderer untuk dev, JSONRenderer untuk production
            structlog.dev.ConsoleRenderer() if settings.APP_ENV == "development" else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.LOG_LEVEL)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )

logger = structlog.get_logger()