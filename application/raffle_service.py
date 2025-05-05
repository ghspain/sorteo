#!/usr/bin/env python3

"""
Service handling raffle functionality including winner selection.
"""
from typing import Dict, List, Any, Optional
import random
from datetime import datetime

import streamlit as st

from domain.models import Participant
from application.session_service import SessionService

class RaffleService:
    """Service class for handling raffles and winner selection."""
    
    def __init__(self, session_service: Optional[SessionService] = None):
        """Initialize the raffle service.
        
        Args:
            session_service: Optional SessionService for session management. 
                          If not provided, a new instance will be created.
        """
        self.session_service = session_service if session_service else SessionService()
        
    def select_winners(self, round_id: int, participants: List[Participant], num_winners: int = 1) -> List[Participant]:
        """Select random winners for a specific raffle round.
        
        Args:
            round_id: The ID of the raffle round
            participants: List of eligible participants
            num_winners: Number of winners to select
            
        Returns:
            List of selected winners
        """
        if not participants:
            return []
            
        # Ensure we don't try to select more winners than participants
        num_winners = min(num_winners, len(participants))
        
        # Select random winners
        winners = random.sample(participants, num_winners)
        
        # Initialize session state winners list if not exists
        if 'winners' not in st.session_state:
            st.session_state.winners = []
        
        # Initialize drawn winners dict if not exists
        if 'drawn_winners' not in st.session_state:
            st.session_state.drawn_winners = {}
        
        # Initialize all_winners list if not exists
        if 'all_winners' not in st.session_state:
            st.session_state.all_winners = []
            
        # Add winners to the session state
        round_winners = []
        for winner in winners:
            winner_data = winner.to_dict()
            winner_data['round_id'] = round_id
            winner_data['selected_at'] = datetime.now().isoformat()
            st.session_state.winners.append(winner_data)
            round_winners.append(winner_data)
            
            # Add email to all winners list (for duplicate checking)
            if winner_data['Email'] not in st.session_state.all_winners:
                st.session_state.all_winners.append(winner_data['Email'])
        
        # Store winners by round
        st.session_state.drawn_winners[round_id] = round_winners
            
        # Update the round with winners
        for round_data in st.session_state.rounds:
            if round_data['id'] == round_id:
                if 'winners' not in round_data:
                    round_data['winners'] = []
                round_data['winners'].extend([w.to_dict() for w in winners])
                break
                
        return winners
     
    def add_round(self) -> Dict[str, Any]:
        """Add a new raffle round using session service.
        
        Returns:
            The created round data
        """
        return self.session_service.add_round("Prize Round", num_winners=1)
        
    def get_round_by_id(self, round_id: int) -> Optional[Dict[str, Any]]:
        """Get a round by its ID.
        
        Args:
            round_id: The ID of the round to retrieve
            
        Returns:
            The round data or None if not found
        """
        rounds = self.session_service.get_rounds()
        for round_data in rounds:
            if round_data["id"] == round_id:
                return round_data
                
        return None
        
    def update_round(self, round_id: int, updates: Dict[str, Any]) -> bool:
        """Update a round's configuration.
        
        Args:
            round_id: The ID of the round to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        # Extract the common fields between our updates dict and SessionService's expectations
        name = updates.get("name", updates.get("prize", f"Prize {round_id}"))
        num_winners = updates.get("num_winners", 1)
        
        # Use the session service to update the round
        updated_round = self.session_service.update_round(round_id, name, num_winners)
        return updated_round is not None
        
    def get_winners_for_round(self, round_id: int) -> List[Dict[str, Any]]:
        """Get the winners for a specific round.
        
        Args:
            round_id: The ID of the round
            
        Returns:
            List of winners for the round
        """
        if 'drawn_winners' in st.session_state and round_id in st.session_state.drawn_winners:
            return st.session_state.drawn_winners[round_id]
        return []
        
    def get_all_winners(self) -> List[Dict[str, Any]]:
        """Get all winners from all rounds.
        
        Returns:
            List of all winners
        """
        return st.session_state.winners if 'winners' in st.session_state else []