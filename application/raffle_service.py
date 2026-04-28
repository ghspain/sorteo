#!/usr/bin/env python3

"""
Service handling raffle functionality including winner selection.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

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

    def _ensure_winner_state(self) -> None:
        """Ensure winner-related session state collections exist."""
        if 'winners' not in st.session_state:
            st.session_state.winners = []
        if 'drawn_winners' not in st.session_state:
            st.session_state.drawn_winners = {}
        if 'all_winners' not in st.session_state:
            st.session_state.all_winners = []
        if 'absent_participants' not in st.session_state:
            st.session_state.absent_participants = []

    def _eligible_participants(
        self,
        participants: List[Participant],
        extra_excluded_emails: Optional[List[str]] = None
    ) -> List[Participant]:
        """Return participants who can still be drawn."""
        self._ensure_winner_state()
        excluded_emails = set(st.session_state.all_winners)
        excluded_emails.update(st.session_state.absent_participants)
        excluded_emails.update(extra_excluded_emails or [])
        return [
            participant
            for participant in participants
            if participant.email.value not in excluded_emails
        ]

    def _winner_to_session_data(
        self,
        winner: Participant,
        round_id: int,
        is_replacement: bool = False,
        replaced_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert a participant winner into session-state metadata."""
        winner_data = winner.to_dict()
        winner_data['round_id'] = round_id
        winner_data['selected_at'] = datetime.now().isoformat()
        winner_data['is_absent'] = False
        winner_data['is_replacement'] = is_replacement
        if replaced_email:
            winner_data['replaced'] = replaced_email
        return winner_data

    def _register_winner_data(self, round_id: int, winner_data: Dict[str, Any]) -> None:
        """Register winner metadata in all winner-related session collections."""
        self._ensure_winner_state()
        st.session_state.winners.append(winner_data)
        if round_id not in st.session_state.drawn_winners:
            st.session_state.drawn_winners[round_id] = []
        st.session_state.drawn_winners[round_id].append(winner_data)
        if winner_data['Email'] not in st.session_state.all_winners:
            st.session_state.all_winners.append(winner_data['Email'])

        for round_data in st.session_state.get('rounds', []):
            if round_data['id'] == round_id:
                if 'winners' not in round_data:
                    round_data['winners'] = []
                round_data['winners'].append(winner_data)
                break
        
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

        eligible_participants = self._eligible_participants(participants)
        if not eligible_participants:
            return []

        # Ensure we don't try to select more winners than participants
        num_winners = min(num_winners, len(eligible_participants))
        
        # Select random winners
        winners = random.sample(eligible_participants, num_winners)

        # Add winners to the session state
        for winner in winners:
            winner_data = self._winner_to_session_data(winner, round_id)
            self._register_winner_data(round_id, winner_data)
                
        return winners

    def mark_winner_absent(
        self,
        round_id: int,
        winner_index: int,
        participants: Optional[List[Participant]] = None
    ) -> bool:
        """Mark a winner as absent and draw a replacement when possible.

        Args:
            round_id: The round containing the winner
            winner_index: Position of the winner inside that round's winner list
            participants: Optional participant pool. Defaults to session participants.

        Returns:
            True when a replacement was drawn, False otherwise.
        """
        self._ensure_winner_state()
        round_winners = st.session_state.drawn_winners.get(round_id, [])
        if winner_index < 0 or winner_index >= len(round_winners):
            return False

        original_winner = round_winners[winner_index]
        if original_winner.get('is_absent'):
            return False

        original_email = original_winner.get('Email')
        if not original_email:
            return False

        if original_email not in st.session_state.absent_participants:
            st.session_state.absent_participants.append(original_email)
        original_winner['is_absent'] = True

        for winner_data in st.session_state.winners:
            if (
                winner_data.get('round_id') == round_id
                and winner_data.get('Email') == original_email
            ):
                winner_data['is_absent'] = True

        participant_pool = participants if participants is not None else st.session_state.get('participants', [])
        eligible_participants = self._eligible_participants(participant_pool)
        if not eligible_participants:
            return False

        replacement = random.choice(eligible_participants)
        replacement_data = self._winner_to_session_data(
            replacement,
            round_id,
            is_replacement=True,
            replaced_email=original_email
        )
        self._register_winner_data(round_id, replacement_data)
        return True

    def get_prize_for_winner_index(self, index: int, round_config: Dict[str, Any]) -> str:
        """Return the prize name assigned to a winner index."""
        prizes = round_config.get('prizes', []) if round_config else []
        if index < len(prizes):
            prize = prizes[index]
            if isinstance(prize, dict):
                return prize.get('name', '-')
            return getattr(prize, 'name', '-')
        return '-'

    def assign_prize(
        self,
        winner: Dict[str, Any],
        winners: List[Dict[str, Any]],
        round_config: Dict[str, Any]
    ) -> str:
        """Assign the original winner prize to originals and replacements."""
        original_winners = [w for w in winners if not w.get('is_replacement')]
        if winner.get('is_replacement'):
            replaced_email = winner.get('replaced')
            for index, original_winner in enumerate(original_winners):
                if original_winner.get('Email') == replaced_email:
                    return self.get_prize_for_winner_index(index, round_config)
            return '-'

        for index, original_winner in enumerate(original_winners):
            if original_winner.get('Email') == winner.get('Email'):
                return self.get_prize_for_winner_index(index, round_config)
        return '-'

    def get_absent_winner_count(self) -> int:
        """Get the number of winners marked absent."""
        return len(st.session_state.get('absent_participants', []))

    def get_present_winner_count(self) -> int:
        """Get the number of currently valid winners."""
        return len([
            winner
            for winner in self.get_all_winners()
            if not winner.get('is_absent')
        ])
     
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