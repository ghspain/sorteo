"""
Participant service for the raffle application.
"""
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st

from domain.models import Participant
from domain.events import DomainEventPublisher, ParticipantsLoaded
from infrastructure.csv_repository import CsvRepository
from infrastructure.error_handling import error_handler, BusinessRuleError


class ParticipantService:
    """Service for participant management."""
    
    def __init__(self):
        """Initialize the participant service."""
        self.csv_repository = CsvRepository()
    
    @error_handler
    def process_participants_file(self, file_content: bytes, only_checked_in: bool = False) -> List[Dict[str, str]]:
        """
        Process a CSV file with participant data.
        
        Args:
            file_content: The content of the CSV file
            only_checked_in: Whether to only include participants who have checked in
            
        Returns:
            A list of participant dictionaries
        """
        # Load participants from the CSV file
        participants_domain = self.csv_repository.load_participants(
            file_content, only_checked_in
        )
        
        # Convert domain objects to dictionaries for the UI
        participants = [p.to_dict() for p in participants_domain]
        
        # Store the participants in the session state
        st.session_state.participants = participants
        
        # Publish an event
        event_publisher = DomainEventPublisher()
        event_publisher.publish(
            ParticipantsLoaded(
                count=len(participants),
                only_checked_in=only_checked_in
            )
        )
        
        return participants
    
    @error_handler
    def get_participants(self) -> List[Dict[str, str]]:
        """
        Get the list of participants from the session state.
        
        Returns:
            A list of participant dictionaries
        
        Raises:
            BusinessRuleError: If no participants have been loaded yet
        """
        if "participants" not in st.session_state:
            raise BusinessRuleError("No participants have been loaded")
        
        return st.session_state.participants
    
    @error_handler
    def get_participant_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the participants.
        
        Returns:
            A dictionary with participant statistics
        """
        if "participants" not in st.session_state:
            return {
                "count": 0,
                "checked_in": 0,
                "domains": {}
            }
        
        participants = st.session_state.participants
        
        # Count participants with check-in
        checked_in = sum(
            1 for p in participants 
            if p.get("Checkin Date (UTC)", "").strip() or p.get("checked_in_at", "").strip()
        )
        
        # Count email domains
        domains = {}
        for p in participants:
            email = p.get("Email") or p.get("email", "")
            if email and "@" in email:
                domain = email.split("@")[1]
                domains[domain] = domains.get(domain, 0) + 1
        
        # Sort domains by count (descending)
        sorted_domains = {
            k: v for k, v in sorted(
                domains.items(), key=lambda item: item[1], reverse=True
            )
        }
        
        return {
            "count": len(participants),
            "checked_in": checked_in,
            "domains": sorted_domains
        }