"""
Draw service for the raffle application.
"""
import random
from typing import List, Dict, Any, Optional

import streamlit as st

from domain.models import Participant, DrawResult, Round
from domain.value_objects import Email
from domain.events import DomainEventPublisher, WinnersDrawn
from infrastructure.error_handling import (
    error_handler, BusinessRuleError, ValidationError
)


class DrawService:
    """Service for drawing winners in the raffle."""
    
    def __init__(self, repository=None):
        """
        Initialize the draw service.
        
        Args:
            repository: Optional repository for persistence
        """
        self.repository = repository
        # Initialize the event publisher
        # This will be patched in tests
        from domain.events import DomainEventPublisher
        self.event_publisher = DomainEventPublisher()
    
    @error_handler
    def draw_winners(
        self,
        num_winners: int,
        only_checked_in: bool = True,
        exclude_emails: List[str] = None
    ) -> List[Participant]:
        """
        Draw winners from the participants list.
        
        Args:
            num_winners: Number of winners to draw
            only_checked_in: Only consider checked-in participants
            exclude_emails: List of emails to exclude from the draw
            
        Returns:
            List of winner participant objects
            
        Raises:
            ValidationError: If the parameters are invalid
            BusinessRuleError: If there are not enough participants
        """
        # Default empty list for exclude_emails if None
        exclude_emails = exclude_emails or []
        
        # Validate parameters
        if num_winners <= 0:
            raise ValidationError(
                "Number of winners must be at least 1",
                details={"num_winners": num_winners}
            )
        
        # Get participants from repository if available
        if self.repository:
            participants = self.repository.get_all_participants()
        else:
            # Fallback to session state if no repository provided
            participants = st.session_state.get("participants", [])
        
        if not participants:
            raise BusinessRuleError("No participants available for the draw")
            
        # Filter participants as needed
        eligible_participants = []
        for p in participants:
            # Skip if email is in exclude list
            if p.email.value in exclude_emails:
                continue
                
            # Skip if not checked in and only_checked_in is True
            if only_checked_in and not p.is_checked_in:
                continue
                
            eligible_participants.append(p)
        
        # Check if we have enough eligible participants
        if len(eligible_participants) < num_winners:
            raise ValidationError(
                f"Not enough eligible participants. Requested: {num_winners}, Available: {len(eligible_participants)}",
                details={"available": len(eligible_participants), "requested": num_winners}
            )
        
        # Randomly select winners
        winners = random.sample(eligible_participants, num_winners)
        
        # Publish domain event
        round_id = getattr(st.session_state, "current_round_id", 1)
        self.event_publisher.publish(
            WinnersDrawn(
                round_id=round_id,
                winner_emails=[winner.email.value for winner in winners]
            )
        )
        
        return winners
    
    @error_handler
    def register_winners(self, round_id: int, winners: List[Dict[str, str]]) -> None:
        """
        Register winners for a round in the session state.
        
        Args:
            round_id: The ID of the round
            winners: List of winner dictionaries
        """
        # Initialize the session state if needed
        if "drawn_winners" not in st.session_state:
            st.session_state.drawn_winners = {}
        
        if "all_winners" not in st.session_state:
            st.session_state.all_winners = []
        
        # Save the winners for this round
        st.session_state.drawn_winners[round_id] = winners
        
        # Add all winner emails to the global list
        winner_emails = [winner["Email"] for winner in winners]
        st.session_state.all_winners.extend(winner_emails)
        
        # Publish domain event
        self.event_publisher.publish(
            WinnersDrawn(
                round_id=round_id,
                winner_emails=winner_emails
            )
        )
    
    @error_handler
    def get_winners_for_round(self, round_id: int) -> List[Dict[str, str]]:
        """
        Get the winners for a specific round.
        
        Args:
            round_id: The ID of the round
            
        Returns:
            List of winner dictionaries
        """
        if "drawn_winners" not in st.session_state:
            return []
        
        return st.session_state.drawn_winners.get(round_id, [])
    
    @error_handler
    def get_all_winner_emails(self) -> List[str]:
        """
        Get all winner emails across all rounds.
        
        Returns:
            List of winner email strings
        """
        if "all_winners" not in st.session_state:
            return []
        
        return st.session_state.all_winners