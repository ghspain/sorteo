"""
Unit tests for the logging service.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from infrastructure.logging_service import LoggingService


class TestLoggingService(unittest.TestCase):
    """Test suite for the LoggingService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a logging service for testing
        self.logging_service = LoggingService()
    
    @patch('structlog.get_logger')
    def test_initialization(self, mock_get_logger):
        """Test that the logging service initializes correctly."""
        # Arrange
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Act
        service = LoggingService()
        
        # Assert
        mock_get_logger.assert_called_once()
        self.assertEqual(service.logger, mock_logger)
    
    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"})
    @patch('logging.basicConfig')
    def test_configure_logging_with_custom_log_level(self, mock_basicConfig):
        """Test that log level from environment variable is used."""
        # Act
        LoggingService()
        
        # Assert
        # Check that basicConfig was called with DEBUG level
        mock_basicConfig.assert_called_once()
        args, kwargs = mock_basicConfig.call_args
        self.assertEqual(kwargs['level'], 10)  # 10 = DEBUG level
    
    @patch('structlog.get_logger')
    def test_bind(self, mock_get_logger):
        """Test that bind creates a new logger with bound context."""
        # Arrange
        mock_logger = MagicMock()
        mock_bound_logger = MagicMock()
        mock_logger.bind.return_value = mock_bound_logger
        mock_get_logger.return_value = mock_logger
        
        service = LoggingService()
        
        # Act
        bound_service = service.bind(request_id="1234", user="test")
        
        # Assert
        mock_logger.bind.assert_called_once_with(request_id="1234", user="test")
        self.assertEqual(bound_service.logger, mock_bound_logger)
        
    def test_debug(self):
        """Test debug log level."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.debug("Debug message", extra="value")
        
        # Assert
        self.logging_service.logger.debug.assert_called_once_with("Debug message", extra="value")
    
    def test_info(self):
        """Test info log level."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.info("Info message", extra="value")
        
        # Assert
        self.logging_service.logger.info.assert_called_once_with("Info message", extra="value")
    
    def test_warning(self):
        """Test warning log level."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.warning("Warning message", extra="value")
        
        # Assert
        self.logging_service.logger.warning.assert_called_once_with("Warning message", extra="value")
    
    def test_error(self):
        """Test error log level."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.error("Error message", extra="value")
        
        # Assert
        self.logging_service.logger.error.assert_called_once_with("Error message", extra="value")
    
    def test_critical(self):
        """Test critical log level."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.critical("Critical message", extra="value")
        
        # Assert
        self.logging_service.logger.critical.assert_called_once_with("Critical message", extra="value")
    
    def test_exception(self):
        """Test exception logging."""
        # Arrange
        self.logging_service.logger = MagicMock()
        exception = ValueError("Test exception")
        
        # Act
        self.logging_service.exception("Exception message", exception, extra="value")
        
        # Assert
        self.logging_service.logger.exception.assert_called_once_with(
            "Exception message", 
            exc_info=exception,
            extra="value"
        )
        
    def test_exception_without_exc_info(self):
        """Test exception logging without explicit exception object."""
        # Arrange
        self.logging_service.logger = MagicMock()
        
        # Act
        self.logging_service.exception("Exception message", extra="value")
        
        # Assert
        self.logging_service.logger.exception.assert_called_once_with(
            "Exception message", 
            exc_info=None,
            extra="value"
        )


if __name__ == '__main__':
    unittest.main()