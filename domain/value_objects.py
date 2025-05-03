"""
Value objects for the raffle domain.

Value objects are immutable objects that are defined by their attributes.
They have no identity and are compared by value, not by reference.
"""
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Optional, List
import uuid


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    value: str

    def __post_init__(self):
        """Validate the email address."""
        if not self.is_valid_email(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate if the string is a valid email address.
        
        Args:
            email: The email address to validate
            
        Returns:
            True if the email is valid, False otherwise
        """
        # Simple regex pattern for email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


@dataclass(frozen=True)
class PersonName:
    """Person name value object."""
    first_name: str
    last_name: str

    def __post_init__(self):
        """Validate the name."""
        if not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name.strip():
            raise ValueError("Last name cannot be empty")

    @property
    def full_name(self) -> str:
        """Get the full name."""
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class SessionId:
    """Session ID value object."""
    value: str

    def __post_init__(self):
        """Validate the session ID."""
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid session ID: {self.value}")

    @staticmethod
    def generate() -> 'SessionId':
        """Generate a new session ID."""
        return SessionId(str(uuid.uuid4()))


@dataclass(frozen=True)
class CheckInDate:
    """Check-in date value object."""
    value: str
    parsed_datetime: Optional[datetime] = None

    def __post_init__(self):
        """Parse and validate the check-in date."""
        if not self.value:
            return
            
        try:
            # Try to parse the date in ISO format
            self.parsed_datetime = datetime.fromisoformat(self.value.replace('Z', '+00:00'))
        except ValueError:
            try:
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
                        object.__setattr__(
                            self, 'parsed_datetime', datetime.strptime(self.value, fmt)
                        )
                        return
                    except ValueError:
                        continue
                        
                raise ValueError(f"Could not parse check-in date: {self.value}")
            except Exception as e:
                raise ValueError(f"Invalid check-in date: {self.value}. Error: {str(e)}")

    @property
    def is_checked_in(self) -> bool:
        """Check if the participant has checked in."""
        return bool(self.value.strip())


@dataclass(frozen=True)
class RoundId:
    """Round ID value object."""
    value: int
    
    def __post_init__(self):
        """Validate the round ID."""
        if self.value <= 0:
            raise ValueError(f"Round ID must be a positive integer: {self.value}")


@dataclass(frozen=True)
class PrizeId:
    """Prize ID value object."""
    value: int
    
    def __post_init__(self):
        """Validate the prize ID."""
        if self.value <= 0:
            raise ValueError(f"Prize ID must be a positive integer: {self.value}")


@dataclass(frozen=True)
class PrizeName:
    """Prize name value object."""
    value: str
    
    def __post_init__(self):
        """Validate the prize name."""
        if not self.value.strip():
            raise ValueError("Prize name cannot be empty")


@dataclass(frozen=True)
class WinnerSelection:
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