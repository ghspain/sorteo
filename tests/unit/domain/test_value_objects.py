"""
Unit tests for the value objects.
"""
import pytest
import uuid
from datetime import datetime

from domain.value_objects import (
    ValueObject, Email, PersonName, CheckInDate, SessionId
)


class TestValueObject:
    """Test suite for the base ValueObject class."""
    
    def test_equality(self):
        """Test that value objects with the same value are equal."""
        # Arrange
        class TestVO(ValueObject[str]):
            pass
        
        # Act
        vo1 = TestVO("test")
        vo2 = TestVO("test")
        vo3 = TestVO("different")
        
        # Assert
        assert vo1 == vo2
        assert vo1 != vo3
        assert hash(vo1) == hash(vo2)
        assert hash(vo1) != hash(vo3)


class TestEmail:
    """Test suite for the Email value object."""
    
    def test_valid_email(self):
        """Test that a valid email can be created."""
        # Act
        email = Email("test@example.com")
        
        # Assert
        assert email.value == "test@example.com"
    
    def test_invalid_email_format(self):
        """Test that an invalid email format raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Email("not-an-email")
        
        assert "Invalid email format" in str(exc_info.value)
    
    def test_empty_email(self):
        """Test that an empty email raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Email("")
        
        assert "Email cannot be empty" in str(exc_info.value)
    
    def test_email_normalization(self):
        """Test that emails are normalized to lowercase."""
        # Act
        email = Email("Test.User@Example.COM")
        
        # Assert
        assert email.value == "test.user@example.com"
    
    def test_email_equality(self):
        """Test that email equality is case-insensitive."""
        # Act
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")
        email3 = Email("other@example.com")
        
        # Assert
        assert email1 == email2
        assert email1 != email3


class TestPersonName:
    """Test suite for the PersonName value object."""
    
    def test_valid_name(self):
        """Test that a valid name can be created."""
        # Act
        name = PersonName("John", "Doe")
        
        # Assert
        assert name.first_name == "John"
        assert name.last_name == "Doe"
    
    def test_empty_first_name(self):
        """Test that an empty first name raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            PersonName("", "Doe")
        
        assert "First name cannot be empty" in str(exc_info.value)
    
    def test_empty_last_name(self):
        """Test that an empty last name raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            PersonName("John", "")
        
        assert "Last name cannot be empty" in str(exc_info.value)
    
    def test_name_normalization(self):
        """Test that names are normalized with proper capitalization."""
        # Act
        name = PersonName("john", "DOE")
        
        # Assert
        assert name.first_name == "John"
        assert name.last_name == "Doe"
    
    def test_full_name(self):
        """Test that full name can be retrieved."""
        # Act
        name = PersonName("John", "Doe")
        
        # Assert
        assert name.full_name == "John Doe"
    
    def test_name_equality(self):
        """Test that names are equal if both first and last names are equal."""
        # Act
        name1 = PersonName("John", "Doe")
        name2 = PersonName("John", "Doe")
        name3 = PersonName("Jane", "Doe")
        
        # Assert
        assert name1 == name2
        assert name1 != name3


class TestCheckInDate:
    """Test suite for the CheckInDate value object."""
    
    def test_valid_date(self):
        """Test that a valid check-in date can be created."""
        # Act
        date = CheckInDate("2023-05-01T10:30:00Z")
        
        # Assert
        assert date.value == "2023-05-01T10:30:00Z"
    
    def test_empty_date(self):
        """Test that CheckInDate accepts an empty date."""
        # Act
        date = CheckInDate("")
        
        # Assert
        assert date.value == ""
        assert not date.is_checked_in
    
    def test_is_checked_in_with_date(self):
        """Test that is_checked_in returns True when there's a date."""
        # Act
        date = CheckInDate("2023-05-01T10:30:00Z")
        
        # Assert
        assert date.is_checked_in
    
    def test_is_checked_in_without_date(self):
        """Test that is_checked_in returns False when there's no date."""
        # Act
        date = CheckInDate("")
        
        # Assert
        assert not date.is_checked_in


class TestSessionId:
    """Test suite for the SessionId value object."""
    
    def test_valid_uuid(self):
        """Test that a valid UUID can be created."""
        # Arrange
        uuid_str = str(uuid.uuid4())
        
        # Act
        session_id = SessionId(uuid_str)
        
        # Assert
        assert session_id.value == uuid_str
    
    def test_invalid_uuid(self):
        """Test that an invalid UUID raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            SessionId("not-a-uuid")
        
        assert "Invalid UUID format" in str(exc_info.value)
    
    def test_generate(self):
        """Test that a new SessionId can be generated."""
        # Act
        session_id = SessionId.generate()
        
        # Assert
        assert isinstance(session_id, SessionId)
        # Verify that it's a valid UUID
        uuid.UUID(session_id.value)