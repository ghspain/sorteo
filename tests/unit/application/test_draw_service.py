"""
Unit tests for the draw service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from application.draw_service import DrawService
from domain.events import DomainEventPublisher, WinnersDrawn
from domain.models import Participant
from domain.value_objects import Email, PersonName, CheckInDate
from infrastructure.error_handling import ValidationError


class TestDrawService:
    """Test suite for the DrawService class."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock participant repository."""
        mock = Mock()
        return mock
    
    @pytest.fixture
    def mock_publisher(self):
        """Create a mock domain event publisher."""
        with patch('domain.events.DomainEventPublisher') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def draw_service(self, mock_repository, mock_publisher):
        """Create a draw service with mocked dependencies."""
        return DrawService(mock_repository)
    
    def test_draw_winners_with_valid_input(self, draw_service, mock_repository, mock_publisher):
        """Test that winners can be drawn with valid input."""
        # Arrange
        count = 2
        checked_in_only = True
        exclude_emails = ["excluded@example.com"]
        
        participants = [
            Participant(
                Email("test1@example.com"), 
                PersonName("Test1", "User1"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                Email("test2@example.com"), 
                PersonName("Test2", "User2"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                Email("test3@example.com"), 
                PersonName("Test3", "User3"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
        ]
        
        mock_repository.get_all_participants.return_value = participants
        
        # Act
        winners = draw_service.draw_winners(count, checked_in_only, exclude_emails)
        
        # Assert
        assert len(winners) == count
        mock_repository.get_all_participants.assert_called_once()
        # Check that a domain event was published
        mock_publisher.publish.assert_called_once()
        event = mock_publisher.publish.call_args[0][0]
        assert isinstance(event, WinnersDrawn)
        assert event.round_id is not None
        assert len(event.winner_emails) == count
    
    def test_draw_winners_with_insufficient_participants(self, draw_service, mock_repository):
        """Test that an error is raised when there are not enough participants."""
        # Arrange
        count = 3
        checked_in_only = True
        exclude_emails = []
        
        participants = [
            Participant(
                Email("test1@example.com"), 
                PersonName("Test1", "User1"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                Email("test2@example.com"), 
                PersonName("Test2", "User2"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
        ]
        
        mock_repository.get_all_participants.return_value = participants
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            draw_service.draw_winners(count, checked_in_only, exclude_emails)
        
        assert "Not enough eligible participants" in str(exc_info.value)
        mock_repository.get_all_participants.assert_called_once()
    
    def test_draw_winners_with_checked_in_only(self, draw_service, mock_repository, mock_publisher):
        """Test that only checked-in participants are considered when checked_in_only is True."""
        # Arrange
        count = 1
        checked_in_only = True
        exclude_emails = []
        
        participants = [
            Participant(
                Email("test1@example.com"), 
                PersonName("Test1", "User1"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                Email("test2@example.com"), 
                PersonName("Test2", "User2"),
                CheckInDate("")  # Not checked in
            ),
        ]
        
        mock_repository.get_all_participants.return_value = participants
        
        # Act
        winners = draw_service.draw_winners(count, checked_in_only, exclude_emails)
        
        # Assert
        assert len(winners) == count
        assert winners[0].email.value == "test1@example.com"
    
    def test_draw_winners_with_excluded_emails(self, draw_service, mock_repository, mock_publisher):
        """Test that excluded emails are not included in the winner pool."""
        # Arrange
        count = 1
        checked_in_only = False
        exclude_emails = ["test1@example.com"]
        
        participants = [
            Participant(
                Email("test1@example.com"), 
                PersonName("Test1", "User1"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                Email("test2@example.com"), 
                PersonName("Test2", "User2"),
                CheckInDate("2023-05-01T10:30:00Z")
            ),
        ]
        
        mock_repository.get_all_participants.return_value = participants
        
        # Act
        winners = draw_service.draw_winners(count, checked_in_only, exclude_emails)
        
        # Assert
        assert len(winners) == count
        assert winners[0].email.value == "test2@example.com"
    
    def test_draw_winners_with_invalid_count(self, draw_service):
        """Test that an error is raised when an invalid count is provided."""
        # Arrange
        count = 0
        checked_in_only = True
        exclude_emails = []
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            draw_service.draw_winners(count, checked_in_only, exclude_emails)
        
        assert "Number of winners must be at least 1" in str(exc_info.value)