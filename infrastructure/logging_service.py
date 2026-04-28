"""
Structured logging service for the application.
"""
import os
import sys
import logging
import structlog
from typing import Optional


class LoggingService:
    """Service for structured logging throughout the application."""
    
    def __init__(self):
        """Initialize the logging service with proper configuration."""
        self._configure_logging()
        self.logger = structlog.get_logger()
    
    def _configure_logging(self) -> None:
        """Configure the structured logging system."""
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        
        # Configure standard Python logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level),
        )
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def bind(self, **kwargs) -> 'LoggingService':
        """
        Create a new logger with the bound context data.
        
        Args:
            **kwargs: The context data to bind to the logger
            
        Returns:
            A new logging service instance with bound context
        """
        new_service = LoggingService()
        new_service.logger = self.logger.bind(**kwargs)
        return new_service
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self.logger.error(message, **kwargs)
    
    def exception(self, message: str, exc_info: Optional[Exception] = None, **kwargs) -> None:
        """
        Log an exception.
        
        Args:
            message: The message to log
            exc_info: The exception info
            **kwargs: Additional context data
        """
        self.logger.exception(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            **kwargs: Additional context data
        """
        self.logger.critical(message, **kwargs)