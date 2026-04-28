"""
Unit tests for the draw service.
"""
import pytest
import streamlit as st
import copy
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
        service = DrawService(mock_repository)
        # Replace the event publisher with our mock
        service.event_publisher = mock_publisher
        return service

    @pytest.fixture
    def mock_session_state(self):
        """Create a properly mocked session state that behaves like an object with attributes."""
        mock = MagicMock()
        return mock
    
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

    def test_draw_winners_without_repository(self, draw_service, mock_publisher):
        """Test that winners can be drawn when no repository is provided but session state is available."""
        # Arrange
        count = 1
        checked_in_only = True
        exclude_emails = []
        
        # Create a participant
        participant = Participant(
            Email("test1@example.com"), 
            PersonName("Test1", "User1"),
            CheckInDate("2023-05-01T10:30:00Z")
        )
        
        # Mock session state with get method that returns our participants
        mock_session = MagicMock()
        # This is the key fix - properly mock the get method to return participants
        mock_session.get = lambda key, default: [participant] if key == "participants" else default
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Remove the repository from draw service
            draw_service.repository = None
            
            # Act
            winners = draw_service.draw_winners(count, checked_in_only, exclude_emails)
            
            # Assert
            assert len(winners) == count
            assert winners[0].email.value == "test1@example.com"
            mock_publisher.publish.assert_called_once()
            
    def test_register_winners(self, draw_service, mock_publisher, mock_session_state):
        """Test registering winners for a round."""
        # Arrange
        round_id = 1
        winners = [
            {"Email": "winner1@example.com", "Name": "Winner 1"},
            {"Email": "winner2@example.com", "Name": "Winner 2"}
        ]
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session_state):
            # Act
            draw_service.register_winners(round_id, winners)
            
            # Assert
            assert mock_session_state.drawn_winners[round_id] == winners
            assert mock_session_state.all_winners == ["winner1@example.com", "winner2@example.com"]
            mock_publisher.publish.assert_called_once()
            
    def test_register_winners_with_existing_winners(self, draw_service, mock_publisher):
        """Test registering winners when previous winners exist."""
        # Arrange
        round_id = 2
        winners = [
            {"Email": "winner3@example.com", "Name": "Winner 3"}
        ]
        
        # Set up existing data with a dictionary we control
        existing_winners = {1: [{"Email": "winner1@example.com", "Name": "Winner 1"}]}
        existing_emails = ["winner1@example.com"]
        
        # Create a new MagicMock for session state
        mock_session = MagicMock()
        mock_session.__contains__ = lambda self, item: item in ["drawn_winners", "all_winners"]
        mock_session.drawn_winners = existing_winners
        mock_session.all_winners = existing_emails
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            draw_service.register_winners(round_id, winners)
            
            # Assert
            # Now verify the state in the mock_session
            assert 1 in mock_session.drawn_winners
            assert 2 in mock_session.drawn_winners
            assert mock_session.drawn_winners[2] == winners
            assert "winner1@example.com" in mock_session.all_winners
            assert "winner3@example.com" in mock_session.all_winners
            mock_publisher.publish.assert_called_once()
            
    def test_get_winners_for_round_existing(self, draw_service):
        """Test getting winners for a specific round when they exist."""
        # Arrange
        round_id = 1
        winners = [{"Email": "winner1@example.com", "Name": "Winner 1"}]
        
        # Create a custom mock that behaves like a dictionary for session state
        class MockSessionState:
            def __init__(self):
                self._data = {"drawn_winners": {round_id: winners}}
            
            def __contains__(self, item):
                return item in self._data
            
            def __getattr__(self, name):
                return self._data.get(name)
        
        mock_session = MockSessionState()
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            result = draw_service.get_winners_for_round(round_id)
            
            # Assert
            assert result == winners
            
    def test_get_winners_for_round_nonexistent(self, draw_service):
        """Test getting winners for a round that doesn't exist."""
        # Arrange
        round_id = 999
        existing_round = 1
        
        # Create a custom mock that behaves like a dictionary for session state
        class MockSessionState:
            def __init__(self):
                self._data = {"drawn_winners": {existing_round: []}}
            
            def __contains__(self, item):
                return item in self._data
            
            def __getattr__(self, name):
                return self._data.get(name)
        
        mock_session = MockSessionState()
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            result = draw_service.get_winners_for_round(round_id)
            
            # Assert
            assert result == []
            
    def test_get_winners_for_round_no_session_state(self, draw_service):
        """Test getting winners when session state doesn't have drawn winners."""
        # Arrange
        round_id = 1
        
        # Create a custom mock that behaves like a dictionary for session state
        class MockSessionState:
            def __init__(self):
                self._data = {}
            
            def __contains__(self, item):
                return item in self._data
            
            def __getattr__(self, name):
                return self._data.get(name)
        
        mock_session = MockSessionState()
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            result = draw_service.get_winners_for_round(round_id)
            
            # Assert
            assert result == []
            
    def test_get_all_winner_emails_existing(self, draw_service):
        """Test getting all winner emails when they exist."""
        # Arrange
        emails = ["winner1@example.com", "winner2@example.com"]
        
        # Create a custom mock that behaves like a dictionary for session state
        class MockSessionState:
            def __init__(self):
                self._data = {"all_winners": emails}
            
            def __contains__(self, item):
                return item in self._data
            
            def __getattr__(self, name):
                return self._data.get(name)
        
        mock_session = MockSessionState()
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            result = draw_service.get_all_winner_emails()
            
            # Assert
            assert result == emails
            
    def test_get_all_winner_emails_no_session_state(self, draw_service):
        """Test getting all winner emails when session state doesn't have winners."""
        # Arrange
        # Create a custom mock that behaves like a dictionary for session state
        class MockSessionState:
            def __init__(self):
                self._data = {}
            
            def __contains__(self, item):
                return item in self._data
            
            def __getattr__(self, name):
                return self._data.get(name)
        
        mock_session = MockSessionState()
        
        # Mock session state properly
        with patch.object(st, 'session_state', mock_session):
            # Act
            result = draw_service.get_all_winner_emails()
            
            # Assert
            assert result == []