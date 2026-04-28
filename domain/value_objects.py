"""
Value objects for the raffle domain.

Value objects are immutable objects that are defined by their attributes.
They have no identity and are compared by value, not by reference.
"""
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Optional, List, TypeVar, Generic
import uuid


T = TypeVar('T')


class ValueObject(Generic[T], ABC):
    """
    Base class for all value objects.
    
    Value objects are immutable objects that are defined by their attributes.
    They have no identity and are compared by value, not by reference.
    """
    value: T
    
    def __init__(self, value: T):
        """Initialize with a value."""
        self.value = value
    
    def __eq__(self, other):
        """Compare value objects by their value."""
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value
    
    def __hash__(self):
        """Hash value objects by their value."""
        return hash(self.value)


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    value: str

    def __post_init__(self):
        """Validate the email address and normalize to lowercase."""
        if not self.value:
            raise ValueError("Email cannot be empty")
            
        # Normalize email to lowercase
        normalized_email = self.value.lower()
        if self.value != normalized_email:
            object.__setattr__(self, 'value', normalized_email)
            
        if not self.is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate if the string is a valid email address.
        
        Args:
            email: The email address to validate
            
        Returns:
            True if the email is valid, False otherwise
        """
        if not email:
            return False
            
        # Simple regex pattern for email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
        
    def __eq__(self, other):
        """Compare emails case-insensitively."""
        if not isinstance(other, self.__class__):
            return False
        return self.value.lower() == other.value.lower()
        
    def __hash__(self):
        """Hash emails by their lowercase value."""
        return hash(self.value.lower())


@dataclass(frozen=True)
class PersonName:
    """Person name value object."""
    first_name: str
    last_name: str

    def __post_init__(self):
        """Validate the name and capitalize properly."""
        if not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
            
        # Capitalize first and last names properly
        capitalized_first = self.first_name[0].upper() + self.first_name[1:].lower() if self.first_name else ""
        capitalized_last = self.last_name[0].upper() + self.last_name[1:].lower() if self.last_name else ""
        
        if self.first_name != capitalized_first:
            object.__setattr__(self, 'first_name', capitalized_first)
        
        if self.last_name != capitalized_last:
            object.__setattr__(self, 'last_name', capitalized_last)

    @property
    def full_name(self) -> str:
        """Get the full name."""
        return f"{self.first_name} {self.last_name}"
        
    def __eq__(self, other):
        """Compare names case-insensitively."""
        if not isinstance(other, self.__class__):
            return False
        return (self.first_name.lower() == other.first_name.lower() and 
                self.last_name.lower() == other.last_name.lower())
    
    def __hash__(self):
        """Hash names by their lowercase values."""
        return hash((self.first_name.lower(), self.last_name.lower()))


@dataclass(frozen=True)
class SessionId:
    """Session ID value object."""
    value: str

    def __post_init__(self):
        """Validate the session ID."""
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {self.value}")

    @staticmethod
    def generate() -> 'SessionId':
        """Generate a new session ID."""
        return SessionId(str(uuid.uuid4()))


@dataclass(frozen=True)
class CheckInDate(ValueObject[str]):
    """Check-in date value object."""
    value: str
    _parsed_datetime: Optional[datetime] = None

    def __post_init__(self):
        """Parse and validate the check-in date."""
        if not self.value:
            return
            
        parsed_dt = None
        try:
            # Try to parse the date in ISO format
            parsed_dt = datetime.fromisoformat(self.value.replace('Z', '+00:00'))
        except ValueError:
            # Try common datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
            ]
            
            for fmt in formats:
                try:
                    parsed_dt = datetime.strptime(self.value, fmt)
                    break
                except ValueError:
                    continue
        
        if parsed_dt is None:
            raise ValueError(f"Could not parse check-in date: {self.value}")
            
        # Use object.__setattr__ since this is a frozen dataclass
        object.__setattr__(self, '_parsed_datetime', parsed_dt)

    @property
    def parsed_datetime(self) -> Optional[datetime]:
        """Get the parsed datetime."""
        return self._parsed_datetime

    @property
    def is_checked_in(self) -> bool:
        """Check if the participant has checked in."""
        return bool(self.value.strip())


@dataclass(frozen=True)
class RoundId(ValueObject[int]):
    """Round ID value object."""
    value: int
    
    def __post_init__(self):
        """Validate the round ID."""
        if self.value <= 0:
            raise ValueError(f"Round ID must be a positive integer: {self.value}")


@dataclass(frozen=True)
class PrizeId(ValueObject[int]):
    """Prize ID value object."""
    value: int
    
    def __post_init__(self):
        """Validate the prize ID."""
        if self.value <= 0:
            raise ValueError(f"Prize ID must be a positive integer: {self.value}")


@dataclass(frozen=True)
class PrizeName(ValueObject[str]):
    """Prize name value object."""
    value: str
    
    def __post_init__(self):
        """Validate the prize name."""
        if not self.value.strip():
            raise ValueError("Prize name cannot be empty")


@dataclass(frozen=True)
class WinnerSelection(ValueObject[List[str]]):
    """Winner selection value object."""
    participant_emails: List[str]
    round_id: int
    selection_timestamp: datetime = datetime.now()
    
    def __post_init__(self):
        """Validate the winner selection."""
        if not self.participant_emails:
            raise ValueError("Winner selection must have at least one participant")
        if self.round_id <= 0:
            raise ValueError(f"Round ID must be a positive integer: {self.round_id}")
            
    @property
    def winner_count(self) -> int:
        """Get the number of winners."""
        return len(self.participant_emails)