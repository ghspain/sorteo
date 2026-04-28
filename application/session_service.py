"""
Session service for the raffle application.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st

from domain.events import DomainEventPublisher, SessionReset
from domain.value_objects import SessionId
from infrastructure.error_handling import error_handler


class SessionService:
    """Service for session management."""
    
    @error_handler
    def initialize_session(self) -> None:
        """Initialize the raffle session if it doesn't exist."""
        if "session_id" not in st.session_state:
            session_id = SessionId.generate()
            st.session_state.session_id = session_id.value
            st.session_state.session_start_time = datetime.now().isoformat()
            st.session_state.participants = []
            st.session_state.rounds = []
            st.session_state.drawn_winners = {}
            st.session_state.all_winners = []
            st.session_state.absent_participants = []
    
    @error_handler
    def reset_session(self) -> None:
        """Reset the raffle session."""
        # Get the current session ID before resetting
        current_session_id = st.session_state.get("session_id", None)
        
        # Reset all session variables
        st.session_state.participants = []
        st.session_state.rounds = []
        st.session_state.drawn_winners = {}
        st.session_state.all_winners = []
        st.session_state.absent_participants = []
        
        # Generate a new session ID
        session_id = SessionId.generate()
        st.session_state.session_id = session_id.value
        st.session_state.session_start_time = datetime.now().isoformat()
        
        # Publish domain event
        if current_session_id:
            event_publisher = DomainEventPublisher()
            event_publisher.publish(SessionReset(session_id=current_session_id))
    
    @error_handler
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            A dictionary with session information
        """
        self.initialize_session()
        
        return {
            "session_id": st.session_state.session_id,
            "start_time": st.session_state.session_start_time,
            "participants_count": len(st.session_state.get("participants", [])),
            "rounds_count": len(st.session_state.get("rounds", [])),
            "total_winners_count": len(st.session_state.get("all_winners", [])),
            "absent_winners_count": len(st.session_state.get("absent_participants", [])),
        }
    
    @error_handler
    def add_round(self, name: str, num_winners: int = 1) -> Dict[str, Any]:
        """
        Add a new round to the session.
        
        Args:
            name: The name of the round
            num_winners: The number of winners for the round
            
        Returns:
            The created round
        """
        # Initialize the session if needed
        self.initialize_session()
        
        # Initialize the rounds list if needed
        if "rounds" not in st.session_state:
            st.session_state.rounds = []
        
        # Create the round
        round_id = len(st.session_state.rounds) + 1
        round_data = {
            "id": round_id,
            "name": name,
            "num_winners": num_winners,
            "prizes": []
        }
        
        # Add the round to the session
        st.session_state.rounds.append(round_data)
        
        return round_data
    
    @error_handler
    def update_round(self, round_id: int, name: str, num_winners: int) -> Dict[str, Any]:
        """
        Update an existing round.
        
        Args:
            round_id: The ID of the round to update
            name: The new name of the round
            num_winners: The new number of winners
            
        Returns:
            The updated round
        """
        # Find the round
        for i, round_data in enumerate(st.session_state.rounds):
            if round_data["id"] == round_id:
                # Update the round
                st.session_state.rounds[i]["name"] = name
                st.session_state.rounds[i]["num_winners"] = num_winners
                return st.session_state.rounds[i]
        
        return None
    
    @error_handler
    def delete_round(self, round_id: int) -> bool:
        """
        Delete a round from the session.
        
        Args:
            round_id: The ID of the round to delete
            
        Returns:
            True if the round was deleted, False otherwise
        """
        # Find the round
        for i, round_data in enumerate(st.session_state.rounds):
            if round_data["id"] == round_id:
                # Delete the round
                del st.session_state.rounds[i]
                
                # Delete any winners for this round
                if round_id in st.session_state.drawn_winners:
                    # Remove winner emails from the global list
                    winner_emails = [
                        w["Email"] for w in st.session_state.drawn_winners[round_id]
                    ]
                    for email in winner_emails:
                        if email in st.session_state.all_winners:
                            st.session_state.all_winners.remove(email)
                    
                    # Delete the winners for this round
                    del st.session_state.drawn_winners[round_id]
                
                return True
        
        return False
    
    @error_handler
    def get_rounds(self) -> list:
        """
        Get all rounds in the session.
        
        Returns:
            A list of rounds
        """
        # Initialize the session if needed
        self.initialize_session()
        
        return st.session_state.get("rounds", [])