"""Logging configuration"""
import logging
import sys

from app.core.config import settings


def setup_logger(name: str = "ai_workflow_builder") -> logging.Logger:
    """Setup application logger"""
    logger = logging.getLogger(name)
    
    # Set level based on DEBUG setting
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Default logger instance
logger = setup_logger()
