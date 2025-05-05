"""
Centralized error handling framework for the application.
"""
import functools
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Callable, TypeVar, cast

import streamlit as st

from infrastructure.logging_service import LoggingService

# Type variables for function typing
F = TypeVar('F', bound=Callable[..., Any])


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "error"  # Maps to Streamlit's error


class ErrorCategory(Enum):
    """Categories of errors in the application."""
    VALIDATION = "Validation Error"
    DATA_PROCESSING = "Data Processing Error"
    BUSINESS_RULE = "Business Rule Error"
    SYSTEM = "System Error"
    UI = "UI Error"
    UNKNOWN = "Unknown Error"


class AppError(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize an application error.
        
        Args:
            message: Human-readable error message
            category: Error category
            severity: Error severity
            details: Additional error details
            original_exception: Original exception that caused this error
        """
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_exception = original_exception
        
        # Add the original traceback if available
        if original_exception:
            self.details["original_traceback"] = traceback.format_exception(
                type(original_exception),
                original_exception,
                original_exception.__traceback__
            )
        
        super().__init__(self.message)


class ValidationError(AppError):
    """Exception raised when data validation fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a validation error."""
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            details=details,
            original_exception=original_exception
        )


class BusinessRuleError(AppError):
    """Exception raised when a business rule is violated."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a business rule error."""
        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_RULE,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_exception=original_exception
        )


class DataProcessingError(AppError):
    """Exception raised when there's an error processing data."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a data processing error."""
        super().__init__(
            message=message,
            category=ErrorCategory.DATA_PROCESSING,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_exception=original_exception
        )


class SystemError(AppError):
    """Exception raised for system-level errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize a system error."""
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            original_exception=original_exception
        )


class ErrorHandler:
    """
    Centralized error handler for the application.
    
    This is a singleton class that handles exceptions raised by the application.
    """
    _instance = None
    _logger = None
    
    def __new__(cls):
        """Create a new singleton instance if needed."""
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._logger = LoggingService()
        return cls._instance
    
    def handle(self, error: AppError) -> None:
        """
        Handle an application error.
        
        Args:
            error: The error to handle
        """
        # Log the error
        log_method = getattr(self._logger, error.severity.name.lower())
        log_method(
            f"{error.category.value}: {error.message}",
            error_details=error.details,
            exception_type=type(error).__name__,
            original_exception=error.original_exception.__class__.__name__ if error.original_exception else None
        )
        
        # Display the error in the UI
        ui_method = getattr(st, error.severity.value)
        ui_method(f"{error.category.value}: {error.message}")
    
    def handle_exception(
        self,
        exception: Exception,
        default_message: str = "An unexpected error occurred"
    ) -> None:
        """
        Handle any exception.
        
        Args:
            exception: The exception to handle
            default_message: Default message to display if the exception is not an AppError
        """
        if isinstance(exception, AppError):
            self.handle(exception)
        else:
            # Convert to an AppError
            error = SystemError(
                message=default_message,
                original_exception=exception,
                details={"exception_message": str(exception)}
            )
            self.handle(error)


def error_handler(func: F) -> F:
    """
    Decorator to add error handling to functions.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Check if we're in a test environment
            # (simplified check - if we're running pytest)
            import sys
            in_test = any('pytest' in arg for arg in sys.argv)
            
            # Log the error regardless
            ErrorHandler().handle_exception(e)
            
            # In test environment, re-raise to allow tests to catch exceptions
            if in_test:
                raise
                
            # In production, return None to allow the calling function to continue
            return None
    
    return cast(F, wrapper)