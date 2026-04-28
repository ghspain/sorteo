"""
Unit tests for the domain events.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from domain.events import (
    DomainEvent, DomainEventPublisher, DomainEventSubscriber,
    ParticipantAdded, ParticipantsImported, WinnersDrawn, SessionReset
)
from domain.value_objects import Email, PersonName, CheckInDate


class TestDomainEvent:
    """Test suite for the DomainEvent class."""
    
    def test_domain_event_creation(self):
        """Test that a domain event can be created."""
        # Arrange
        class TestEvent(DomainEvent):
            def __init__(self, data):
                super().__init__()
                self.data = data
        
        # Act
        event = TestEvent("test_data")
        
        # Assert
        assert event.data == "test_data"
        assert isinstance(event.timestamp, datetime)
        assert event.event_id is not None
        assert event.event_type == "TestEvent"


class TestDomainEventPublisher:
    """Test suite for the DomainEventPublisher class."""
    
    def test_subscribe_and_publish(self):
        """Test that subscribers receive published events."""
        # Arrange
        publisher = DomainEventPublisher()
        mock_subscriber = Mock(spec=DomainEventSubscriber)
        mock_subscriber.handle_event = Mock()
        mock_subscriber.get_subscribed_event_types.return_value = ["TestEvent"]
        
        class TestEvent(DomainEvent):
            pass
        
        event = TestEvent()
        
        # Act
        publisher.subscribe(mock_subscriber)
        publisher.publish(event)
        
        # Assert
        mock_subscriber.handle_event.assert_called_once_with(event)
    
    def test_unsubscribe(self):
        """Test that unsubscribed subscribers don't receive events."""
        # Arrange
        publisher = DomainEventPublisher()
        mock_subscriber = Mock(spec=DomainEventSubscriber)
        mock_subscriber.get_subscribed_event_types.return_value = ["TestEvent"]
        
        class TestEvent(DomainEvent):
            pass
        
        event = TestEvent()
        
        # Act
        publisher.subscribe(mock_subscriber)
        publisher.unsubscribe(mock_subscriber)
        publisher.publish(event)
        
        # Assert
        mock_subscriber.handle_event.assert_not_called()
    
    def test_singleton(self):
        """Test that DomainEventPublisher is a singleton."""
        # Act
        publisher1 = DomainEventPublisher()
        publisher2 = DomainEventPublisher()
        
        # Assert
        assert publisher1 is publisher2


class TestParticipantEvents:
    """Test suite for the participant related events."""
    
    def test_participant_added(self):
        """Test that a ParticipantAdded event can be created."""
        # Arrange
        email = Email("test@example.com")
        name = PersonName("Test", "User")
        check_in_date = CheckInDate("2023-05-01T10:30:00Z")
        
        # Act
        event = ParticipantAdded(email, name, check_in_date)
        
        # Assert
        assert event.email.value == "test@example.com"
        assert event.name.first_name == "Test"
        assert event.name.last_name == "User"
        assert event.checked_in_at.value == "2023-05-01T10:30:00Z"
        assert event.event_type == "ParticipantAdded"
    
    def test_participants_imported(self):
        """Test that a ParticipantsImported event can be created."""
        # Arrange
        count = 5
        source = "test_file.csv"
        
        # Act
        event = ParticipantsImported(count, source)
        
        # Assert
        assert event.count == 5
        assert event.source == "test_file.csv"
        assert event.event_type == "ParticipantsImported"


class TestDrawEvents:
    """Test suite for the draw related events."""
    
    def test_winners_drawn(self):
        """Test that a WinnersDrawn event can be created."""
        # Arrange
        round_id = 1
        winner_emails = ["test1@example.com", "test2@example.com"]
        
        # Act
        event = WinnersDrawn(round_id, winner_emails)
        
        # Assert
        assert event.round_id == 1
        assert event.winner_emails == ["test1@example.com", "test2@example.com"]
        assert event.event_type == "WinnersDrawn"


class TestSessionEvents:
    """Test suite for the session related events."""
    
    def test_session_reset(self):
        """Test that a SessionReset event can be created."""
        # Arrange
        session_id = "test-session-id"
        
        # Act
        event = SessionReset(session_id)
        
        # Assert
        assert event.session_id == "test-session-id"
        assert event.event_type == "SessionReset"


class TestDomainEventSubscriber:
    """Test suite for the DomainEventSubscriber class."""
    
    def test_domain_event_subscriber(self):
        """Test that a DomainEventSubscriber can subscribe to events."""
        # Arrange
        class TestSubscriber(DomainEventSubscriber):
            def get_subscribed_event_types(self):
                return ["TestEvent"]
            
            def handle_event(self, event):
                pass
        
        subscriber = TestSubscriber()
        
        # Act & Assert
        assert subscriber.get_subscribed_event_types() == ["TestEvent"]