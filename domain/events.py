"""
Domain events for the raffle application.

Domain events represent something that happened in the domain that domain experts care about.
They are used to decouple components and enable domain-driven design.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class DomainEvent(ABC):
    """Base class for all domain events."""
    
    def __init__(self):
        """Initialize the domain event with default values."""
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.now()
    
    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__


class DomainEventSubscriber(ABC):
    """Interface for domain event subscribers."""
    
    @abstractmethod
    def get_subscribed_event_types(self) -> List[str]:
        """
        Get the list of event types this subscriber is interested in.
        
        Returns:
            List of event type names
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: DomainEvent) -> None:
        """
        Handle an event.
        
        Args:
            event: The event to handle
        """
        pass


@dataclass
class ParticipantsLoaded(DomainEvent):
    """Event triggered when participants are loaded from a CSV file."""
    count: int
    only_checked_in: bool = False
    source: str = "csv"
    
    def __init__(self, count, only_checked_in=False, source="csv"):
        """Initialize with count of participants loaded."""
        super().__init__()
        self.count = count
        self.only_checked_in = only_checked_in
        self.source = source


@dataclass
class RoundCreated(DomainEvent):
    """Event triggered when a new round is created."""
    round_id: int
    name: str
    num_winners: int


@dataclass
class RoundUpdated(DomainEvent):
    """Event triggered when a round is updated."""
    round_id: int
    name: str
    num_winners: int


@dataclass
class RoundDeleted(DomainEvent):
    """Event triggered when a round is deleted."""
    round_id: int


@dataclass
class PrizeAdded(DomainEvent):
    """Event triggered when a prize is added to a round."""
    round_id: int
    prize_id: int
    name: str
    description: str


@dataclass
class PrizeUpdated(DomainEvent):
    """Event triggered when a prize is updated."""
    round_id: int
    prize_id: int
    name: str
    description: str


@dataclass
class PrizeDeleted(DomainEvent):
    """Event triggered when a prize is deleted."""
    round_id: int
    prize_id: int


@dataclass
class WinnersDrawn(DomainEvent):
    """Event triggered when winners are drawn for a round."""
    round_id: int
    num_winners: int = None
    winner_emails: List[str] = None
    
    def __init__(self, round_id, winner_emails):
        """Initialize the WinnersDrawn event."""
        super().__init__()
        self.round_id = round_id
        self.winner_emails = winner_emails
        self.num_winners = len(winner_emails) if winner_emails else 0


@dataclass
class SessionReset(DomainEvent):
    """Event triggered when the raffle session is reset."""
    session_id: str


@dataclass
class ParticipantAdded(DomainEvent):
    """Event triggered when a participant is added."""
    email: Any  # Email value object
    name: Any   # PersonName value object
    checked_in_at: Any  # CheckInDate value object


@dataclass
class ParticipantsImported(DomainEvent):
    """Event triggered when participants are imported from a source."""
    count: int
    source: str


class DomainEventPublisher:
    """
    Simple event publisher for domain events.
    
    This is a singleton class that stores and publishes domain events.
    """
    _instance = None
    _subscribers = []
    _events_history = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainEventPublisher, cls).__new__(cls)
        return cls._instance
    
    def subscribe(self, subscriber: DomainEventSubscriber) -> None:
        """
        Subscribe to events.
        
        Args:
            subscriber: The subscriber to register
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
    
    def unsubscribe(self, subscriber: DomainEventSubscriber) -> None:
        """
        Unsubscribe from events.
        
        Args:
            subscriber: The subscriber to unregister
        """
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)
    
    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Store event in history
        self._events_history.append(event)
        
        # Notify subscribers interested in this event type
        event_type = event.event_type
        
        for subscriber in self._subscribers:
            if event_type in subscriber.get_subscribed_event_types():
                subscriber.handle_event(event)
    
    def get_events_history(self) -> List[DomainEvent]:
        """Get the history of all events."""
        return self._events_history.copy()