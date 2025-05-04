"""
Participant service for the raffle application.
Implements application layer in DDD, orchestrating domain objects and infrastructure.
"""
from typing import List, Dict, Any, Optional
import io
import pandas as pd

import streamlit as st

from domain.events import DomainEventPublisher, ParticipantsLoaded
from infrastructure.csv_repository import ParticipantRepository, CsvRepository
from infrastructure.error_handling import error_handler, BusinessRuleError


class ParticipantService:
    """
    Service for participant management.
    Follows SOLID principles, especially dependency inversion by depending on abstractions.
    """

    def __init__(self, repository: Optional[ParticipantRepository] = None):
        """
        Initialize the participant service.

        Args:
            repository: Optional repository implementation, uses default if not provided
        """
        self.repository = repository if repository is not None else CsvRepository()
        # Define standard column mappings for various input formats
        self._column_mappings = {
            'email': ['Email', 'email', 'email_address', 'mail'],
            'first_name': ['First Name', 'first_name', 'firstname', 'name'],
            'last_name': ['Last Name', 'last_name', 'lastname', 'surname'],
            'checked_in_at': ['Check-in Date (UTC)', 'checked_in_at', 'checkin_date', 'checkin_time']
        }

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to a standardized format

        Args:
            df: DataFrame with original column names

        Returns:
            DataFrame with normalized column names
        """
        normalized_df = df.copy()

        # Implement column name normalization
        for standard_name, variations in self._column_mappings.items():
            for column in df.columns:
                if column in variations:
                    normalized_df = normalized_df.rename(columns={column: standard_name})
                    break

        return normalized_df

    @error_handler
    def process_participants_file(self, file_content: bytes, only_checked_in: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Process uploaded participant file and return valid participants

        Args:
            file_content: Raw bytes of the uploaded CSV file
            only_checked_in: Flag to filter only checked-in participants

        Returns:
            List of participant dictionaries or None if processing fails
        """
        try:
            # Parse CSV data
            df = pd.read_csv(io.BytesIO(file_content))

            # Normalize column names
            df = self.normalize_column_names(df)

            # Validate required columns
            required_columns = ['email', 'first_name', 'last_name']
            if only_checked_in:
                required_columns.append('checked_in_at')

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Filter checked-in participants if requested
            if only_checked_in and 'checked_in_at' in df.columns:
                df = df[df['checked_in_at'].notna() & (df['checked_in_at'] != '')]

            # Convert to list of dictionaries
            participants = self.repository.convert_to_participants(df)

            # Store the participants in the session state
            st.session_state.participants = participants

            # Publish an event
            self._publish_participants_loaded_event(len(participants), only_checked_in)

            return participants
        except Exception as e:
            # Log the error (in a real app, use a proper logging framework)
            print(f"Error processing participants file: {e}")
            return None

    def _publish_participants_loaded_event(self, count: int, only_checked_in: bool) -> None:
        """
        Publish a participants loaded event.

        Args:
            count: Number of participants loaded
            only_checked_in: Whether only checked in participants were loaded
        """
        event_publisher = DomainEventPublisher()
        event_publisher.publish(
            ParticipantsLoaded(
                count=count,
                only_checked_in=only_checked_in
            )
        )

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

        return {
            "count": len(participants),
            "checked_in": self._count_checked_in_participants(participants),
            "domains": self._get_domain_distribution(participants)
        }

    def _count_checked_in_participants(self, participants: List[Dict[str, str]]) -> int:
        """
        Count participants with check-in data.

        Args:
            participants: List of participant dictionaries

        Returns:
            Count of checked in participants
        """
        return sum(
            1 for p in participants
            if p.get("checked_in_at", "").strip()
        )

    def _get_domain_distribution(self, participants: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Get distribution of email domains among participants.

        Args:
            participants: List of participant dictionaries

        Returns:
            Dictionary with domain counts, sorted by frequency
        """
        domains = {}
        for p in participants:
            email = p.get("email", "")
            if email and "@" in email:
                domain = email.split("@")[1]
                domains[domain] = domains.get(domain, 0) + 1

        # Sort domains by count (descending)
        return {
            k: v for k, v in sorted(
                domains.items(), key=lambda item: item[1], reverse=True
            )
        }