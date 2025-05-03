"""
Domain models for the raffle application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

from domain.value_objects import (
    Email, PersonName, CheckInDate, SessionId, 
    RoundId, PrizeId, PrizeName, WinnerSelection
)
from domain.events import DomainEventPublisher, RoundCreated, WinnersDrawn


@dataclass
class Participant:
    """Participant entity."""
    email: Email
    name: PersonName
    checked_in_at: CheckInDate
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Participant':
        """
        Create a Participant instance from a dictionary.
        
        Args:
            data: Dictionary with participant data
            
        Returns:
            A Participant instance
            
        Raises:
            ValueError: If the data is invalid
        """
        try:
            email_value = data.get('Email') or data.get('email', '')
            first_name = data.get('First Name') or data.get('first_name', '')
            last_name = data.get('Last Name') or data.get('last_name', '')
            checked_in_at = data.get('Checkin Date (UTC)') or data.get('checked_in_at', '')
            
            return cls(
                email=Email(email_value),
                name=PersonName(first_name, last_name),
                checked_in_at=CheckInDate(checked_in_at)
            )
        except ValueError as e:
            raise ValueError(f"Invalid participant data: {e}")
        
    def to_dict(self) -> Dict[str, str]:
        """
        Convert the participant to a dictionary.
        
        Returns:
            A dictionary with the participant's data
        """
        return {
            'Email': self.email.value,
            'First Name': self.name.first_name,
            'Last Name': self.name.last_name,
            'Checkin Date (UTC)': self.checked_in_at.value,
            'Full Name': self.full_name,
            'Is Checked In': str(self.is_checked_in)
        }
    
    @property
    def full_name(self) -> str:
        """Get the participant's full name."""
        return self.name.full_name
    
    @property
    def is_checked_in(self) -> bool:
        """Check if the participant has checked in."""
        return self.checked_in_at.is_checked_in


@dataclass
class Prize:
    """Prize entity."""
    prize_id: PrizeId
    name: PrizeName
    description: str = ""
    
    @classmethod
    def create(cls, id: int, name: str, description: str = "") -> 'Prize':
        """
        Create a new prize.
        
        Args:
            id: The prize ID
            name: The prize name
            description: The prize description
            
        Returns:
            A new Prize instance
        """
        return cls(
            prize_id=PrizeId(id),
            name=PrizeName(name),
            description=description
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the prize to a dictionary.
        
        Returns:
            A dictionary with the prize's data
        """
        return {
            'id': self.prize_id.value,
            'name': self.name.value,
            'description': self.description
        }


@dataclass
class Round:
    """Round entity."""
    round_id: RoundId
    name: str
    num_winners: int
    prizes: List[Prize] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the round."""
        if not self.name.strip():
            raise ValueError("Round name cannot be empty")
        if self.num_winners <= 0:
            raise ValueError(f"Number of winners must be positive: {self.num_winners}")
    
    @staticmethod
    def create_new(round_id: int, name: Optional[str] = None, num_winners: int = 1) -> 'Round':
        """
        Create a new round with default values.
        
        Args:
            round_id: The round ID
            name: The round name (defaults to "Ronda {round_id}")
            num_winners: The number of winners (defaults to 1)
            
        Returns:
            A new Round instance
            
        Raises:
            ValueError: If the parameters are invalid
        """
        if name is None:
            name = f"Ronda {round_id}"
        
        if num_winners <= 0:
            raise ValueError(f"Number of winners must be positive: {num_winners}")
            
        round_obj = Round(
            round_id=RoundId(round_id),
            name=name,
            num_winners=num_winners
        )
        
        # Publish domain event
        event_publisher = DomainEventPublisher()
        event_publisher.publish(
            RoundCreated(
                round_id=round_id,
                name=name,
                num_winners=num_winners
            )
        )
        
        return round_obj
    
    def add_prize(self, prize: Prize) -> None:
        """
        Add a prize to the round.
        
        Args:
            prize: The prize to add
        """
        self.prizes.append(prize)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the round to a dictionary.
        
        Returns:
            A dictionary with the round's data
        """
        return {
            'id': self.round_id.value,
            'name': self.name,
            'num_winners': self.num_winners,
            'prizes': [prize.to_dict() for prize in self.prizes]
        }


@dataclass
class DrawResult:
    """Draw result value object."""
    round_id: RoundId
    winners: List[Participant]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate and publish domain event."""
        if not self.winners:
            raise ValueError("Draw result must have at least one winner")
        
        # Publish domain event
        event_publisher = DomainEventPublisher()
        event_publisher.publish(
            WinnersDrawn(
                round_id=self.round_id.value,
                num_winners=len(self.winners),
                winner_emails=[winner.email.value for winner in self.winners]
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the draw result to a dictionary.
        
        Returns:
            A dictionary with the draw result data
        """
        return {
            'round_id': self.round_id.value,
            'winners': [winner.to_dict() for winner in self.winners],
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class RaffleSession:
    """Raffle session entity."""
    id: SessionId
    participants: List[Participant] = field(default_factory=list)
    rounds: List[Round] = field(default_factory=list)
    all_winners: List[Email] = field(default_factory=list)
    drawn_winners: Dict[int, List[Participant]] = field(default_factory=dict)
    
    @classmethod
    def create_new(cls) -> 'RaffleSession':
        """
        Create a new raffle session.
        
        Returns:
            A new RaffleSession instance
        """
        return cls(id=SessionId.generate())
    
    def add_participant(self, participant: Participant) -> None:
        """
        Add a participant to the session.
        
        Args:
            participant: The participant to add
        """
        self.participants.append(participant)
    
    def add_round(self, round_obj: Round) -> None:
        """
        Add a round to the session.
        
        Args:
            round_obj: The round to add
        """
        self.rounds.append(round_obj)
    
    def record_winners(self, round_id: int, winners: List[Participant]) -> None:
        """
        Record the winners for a round.
        
        Args:
            round_id: The ID of the round
            winners: The list of winners
        """
        self.drawn_winners[round_id] = winners
        for winner in winners:
            if winner.email not in self.all_winners:
                self.all_winners.append(winner.email)
    
    def is_previous_winner(self, email: Email) -> bool:
        """
        Check if a participant has already won in a previous round.
        
        Args:
            email: The participant's email
            
        Returns:
            True if the participant has already won, False otherwise
        """
        return email in self.all_winners