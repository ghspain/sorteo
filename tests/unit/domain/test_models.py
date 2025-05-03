"""
Unit tests for the domain models.
"""
import pytest
from datetime import datetime

from domain.models import Participant, Prize, Round, DrawResult, RaffleSession
from domain.value_objects import Email, PersonName, CheckInDate, SessionId


class TestParticipant:
    """Test suite for the Participant model."""
    
    def test_participant_creation(self):
        """Test that a participant can be created."""
        # Arrange
        email = Email("john.doe@example.com")
        name = PersonName("John", "Doe")
        checked_in_at = CheckInDate("2023-05-01T10:30:00Z")
        
        # Act
        participant = Participant(email, name, checked_in_at)
        
        # Assert
        assert participant.email.value == "john.doe@example.com"
        assert participant.name.first_name == "John"
        assert participant.name.last_name == "Doe"
        assert participant.checked_in_at.value == "2023-05-01T10:30:00Z"
    
    def test_from_dict(self):
        """Test that a participant can be created from a dictionary."""
        # Arrange
        data = {
            "Email": "jane.smith@example.com",
            "First Name": "Jane",
            "Last Name": "Smith",
            "Checkin Date (UTC)": "2023-05-02T11:45:00Z"
        }
        
        # Act
        participant = Participant.from_dict(data)
        
        # Assert
        assert participant.email.value == "jane.smith@example.com"
        assert participant.name.first_name == "Jane"
        assert participant.name.last_name == "Smith"
        assert participant.checked_in_at.value == "2023-05-02T11:45:00Z"
    
    def test_from_dict_alternate_keys(self):
        """Test that a participant can be created from a dictionary with alternate keys."""
        # Arrange
        data = {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "checked_in_at": "2023-05-02T11:45:00Z"
        }
        
        # Act
        participant = Participant.from_dict(data)
        
        # Assert
        assert participant.email.value == "jane.smith@example.com"
        assert participant.name.first_name == "Jane"
        assert participant.name.last_name == "Smith"
        assert participant.checked_in_at.value == "2023-05-02T11:45:00Z"
    
    def test_to_dict(self):
        """Test that a participant can be converted to a dictionary."""
        # Arrange
        email = Email("john.doe@example.com")
        name = PersonName("John", "Doe")
        checked_in_at = CheckInDate("2023-05-01T10:30:00Z")
        participant = Participant(email, name, checked_in_at)
        
        # Act
        result = participant.to_dict()
        
        # Assert
        assert result["Email"] == "john.doe@example.com"
        assert result["First Name"] == "John"
        assert result["Last Name"] == "Doe"
        assert result["Checkin Date (UTC)"] == "2023-05-01T10:30:00Z"
    
    def test_full_name(self):
        """Test that a participant's full name can be retrieved."""
        # Arrange
        email = Email("john.doe@example.com")
        name = PersonName("John", "Doe")
        checked_in_at = CheckInDate("2023-05-01T10:30:00Z")
        participant = Participant(email, name, checked_in_at)
        
        # Act & Assert
        assert participant.full_name == "John Doe"


class TestPrize:
    """Test suite for the Prize model."""
    
    def test_prize_creation(self):
        """Test that a prize can be created."""
        # Act
        prize = Prize(1, "Gift Card", "A $50 Amazon gift card")
        
        # Assert
        assert prize.id == 1
        assert prize.name == "Gift Card"
        assert prize.description == "A $50 Amazon gift card"
    
    def test_prize_default_description(self):
        """Test that a prize can be created with a default description."""
        # Act
        prize = Prize(1, "Gift Card")
        
        # Assert
        assert prize.id == 1
        assert prize.name == "Gift Card"
        assert prize.description == ""


class TestRound:
    """Test suite for the Round model."""
    
    def test_round_creation(self):
        """Test that a round can be created."""
        # Act
        round_obj = Round(1, "First Round", 3)
        
        # Assert
        assert round_obj.id == 1
        assert round_obj.name == "First Round"
        assert round_obj.num_winners == 3
        assert round_obj.prizes == []
    
    def test_create_new_with_defaults(self):
        """Test that a round can be created with default values."""
        # Act
        round_obj = Round.create_new(2)
        
        # Assert
        assert round_obj.id == 2
        assert round_obj.name == "Ronda 2"
        assert round_obj.num_winners == 1
        assert round_obj.prizes == []
    
    def test_create_new_with_custom_values(self):
        """Test that a round can be created with custom values."""
        # Act
        round_obj = Round.create_new(3, "Special Round", 5)
        
        # Assert
        assert round_obj.id == 3
        assert round_obj.name == "Special Round"
        assert round_obj.num_winners == 5
        assert round_obj.prizes == []


class TestDrawResult:
    """Test suite for the DrawResult model."""
    
    def test_draw_result_creation(self):
        """Test that a draw result can be created."""
        # Arrange
        round_id = 1
        p1 = Participant(
            Email("winner1@example.com"),
            PersonName("Winner", "One"),
            CheckInDate("2023-05-01T10:30:00Z")
        )
        p2 = Participant(
            Email("winner2@example.com"),
            PersonName("Winner", "Two"),
            CheckInDate("2023-05-01T10:35:00Z")
        )
        winners = [p1, p2]
        
        # Act
        result = DrawResult(round_id, winners)
        
        # Assert
        assert result.round_id == 1
        assert len(result.winners) == 2
        assert result.winners[0].email.value == "winner1@example.com"
        assert result.winners[1].email.value == "winner2@example.com"
        assert isinstance(result.timestamp, datetime)
    
    def test_to_dict(self):
        """Test that a draw result can be converted to a dictionary."""
        # Arrange
        round_id = 1
        p1 = Participant(
            Email("winner1@example.com"),
            PersonName("Winner", "One"),
            CheckInDate("2023-05-01T10:30:00Z")
        )
        winners = [p1]
        result = DrawResult(round_id, winners)
        
        # Act
        result_dict = result.to_dict()
        
        # Assert
        assert result_dict["round_id"] == 1
        assert len(result_dict["winners"]) == 1
        assert result_dict["winners"][0]["Email"] == "winner1@example.com"
        assert isinstance(result_dict["timestamp"], str)


class TestRaffleSession:
    """Test suite for the RaffleSession model."""
    
    def test_raffle_session_creation(self):
        """Test that a raffle session can be created."""
        # Arrange
        session_id = SessionId("123e4567-e89b-12d3-a456-426614174000")
        
        # Act
        session = RaffleSession(session_id)
        
        # Assert
        assert session.id.value == "123e4567-e89b-12d3-a456-426614174000"
        assert session.participants == []
        assert session.rounds == []
        assert session.all_winners == []
        assert session.drawn_winners == {}
    
    def test_create_new(self):
        """Test that a new raffle session can be created."""
        # Act
        session = RaffleSession.create_new()
        
        # Assert
        assert isinstance(session.id, SessionId)
        assert session.participants == []
        assert session.rounds == []
        assert session.all_winners == []
        assert session.drawn_winners == {}