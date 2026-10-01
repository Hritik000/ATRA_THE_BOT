"""Logging configuration for ATRA backend."""

import logging
import sys
from typing import Optional

from atra_backend.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = settings.LOG_LEVEL.upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set specific loggers to avoid noisy output
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if log_level != "DEBUG" else logging.INFO
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
