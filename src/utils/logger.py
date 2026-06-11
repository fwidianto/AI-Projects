"""Logging configuration."""

import logging
import os
from pathlib import Path
from typing import Optional

from src.config.settings import settings


def setup_logger(
    name: str = "app",
    log_file: Optional[str] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger
    """
    # Get log level
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file provided or in settings)
    log_path = log_file or settings.log_file
    if log_path:
        log_dir = Path(log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get or create a logger.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Pre-configured loggers
app_logger = setup_logger("app")
scraper_logger = setup_logger("scraper")
ml_logger = setup_logger("ml")
api_logger = setup_logger("api")