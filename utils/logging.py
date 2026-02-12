"""Logging configuration for Math RAG system."""

import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger


class LoggerSetup:
    """Setup and configure logging for the application."""
    
    _initialized = False
    
    @classmethod
    def setup(
        cls,
        log_file: Optional[Path] = None,
        log_level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "7 days"
    ):
        """
        Setup logging configuration.
        
        Args:
            log_file: Path to log file
            log_level: Logging level
            rotation: Log rotation size
            retention: Log retention period
        """
        if cls._initialized:
            return
        
        # Remove default handler
        logger.remove()
        
        # Console handler with colors
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True
        )
        
        # File handler if log file provided
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=log_level,
                rotation=rotation,
                retention=retention,
                compression="zip"
            )
        
        cls._initialized = True
        logger.info("Logging initialized")
    
    @classmethod
    def get_logger(cls, name: str):
        """Get logger instance with specific name."""
        return logger.bind(name=name)


def get_logger(name: str):
    """Convenience function to get logger."""
    return LoggerSetup.get_logger(name)