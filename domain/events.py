"""
Domain events for the raffle application.

Domain events represent something that happened in the domain that domain experts care about.
They are used to decouple components and enable domain-driven design.
"""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class DomainEvent(ABC):
    """Base class for all domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)


@dataclass
class ParticipantsLoaded(DomainEvent):
    """Event triggered when participants are loaded from a CSV file."""
    count: int
    only_checked_in: bool


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
    num_winners: int
    winner_emails: List[str]


@dataclass
class SessionReset(DomainEvent):
    """Event triggered when the raffle session is reset."""
    session_id: str


class DomainEventPublisher:
    """
    Simple event publisher for domain events.
    
    This is a singleton class that stores and publishes domain events.
    """
    _instance = None
    _subscribers = {}
    _events_history = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainEventPublisher, cls).__new__(cls)
        return cls._instance
    
    def subscribe(self, event_type: type, subscriber):
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            subscriber: The function to call when the event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)
    
    def publish(self, event: DomainEvent):
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Store event in history
        self._events_history.append(event)
        
        # Get the event type
        event_type = type(event)
        
        # Call all subscribers
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                subscriber(event)
    
    def get_events_history(self) -> List[DomainEvent]:
        """Get the history of all events."""
        return self._events_history.copy()