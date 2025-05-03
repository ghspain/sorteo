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
    
    @error_handler
    def draw_winners(
        self,
        participants: List[Dict[str, str]],
        num_winners: int,
        exclude_emails: List[str]
    ) -> List[Dict[str, str]]:
        """
        Draw winners from the participants list.
        
        Args:
            participants: List of participant dictionaries
            num_winners: Number of winners to draw
            exclude_emails: List of emails to exclude from the draw
            
        Returns:
            List of winner dictionaries
            
        Raises:
            BusinessRuleError: If there are not enough participants for the draw
        """
        # Validate parameters
        if not participants:
            raise BusinessRuleError("No participants available for the draw")
        
        if num_winners <= 0:
            raise ValidationError(
                "Number of winners must be positive",
                details={"num_winners": num_winners}
            )
        
        # Filter out excluded participants
        eligible_participants = [
            p for p in participants 
            if p.get('Email') not in exclude_emails
        ]
        
        # Check if we have enough eligible participants
        if len(eligible_participants) < num_winners:
            st.error(
                f"Not enough participants available. "
                f"Requested: {num_winners}, Available: {len(eligible_participants)}"
            )
            return []
        
        # Randomly select winners
        winners = random.sample(eligible_participants, num_winners)
        
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
        event_publisher = DomainEventPublisher()
        event_publisher.publish(
            WinnersDrawn(
                round_id=round_id,
                num_winners=len(winners),
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