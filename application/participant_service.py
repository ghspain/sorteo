"""
Participant service for the raffle application.
"""

from typing import Any, Dict, List, Optional

import streamlit as st

from domain.events import DomainEventPublisher, ParticipantsLoaded
from domain.models import Participant
from infrastructure.csv_repository import CsvRepository
from infrastructure.error_handling import (
    DataProcessingError,
    ValidationError,
    error_handler,
)


class ParticipantService:
    """Service for handling participant-related operations."""

    def __init__(self, repository: CsvRepository):
        """
        Initialize the participant service.

        Args:
            repository: Repository for participant data access
        """
        self.repository = repository
        self.event_publisher = DomainEventPublisher()

    @error_handler
    def process_participants_file(
        self, file_content: bytes, only_checked_in: bool = True
    ) -> List[Participant]:
        """
        Process a file containing participant data.

        Args:
            file_content: The file content as bytes
            only_checked_in: Whether to only include participants who have checked in

        Returns:
            A list of Participant objects

        Raises:
            ValidationError: If the file is invalid
            DataProcessingError: If there's an error processing the file
        """
        try:
            # Use repository to load participants
            participants = self.repository.load_participants(
                file_content=file_content, only_checked_in=only_checked_in
            )
            
            # Check if participants is None or empty before proceeding
            if participants is None:
                raise DataProcessingError(
                    message="No participant data was returned",
                    details={"error": "Repository returned None"}
                )

            # Publish domain event
            self.event_publisher.publish(
                ParticipantsLoaded(count=len(participants), only_checked_in=only_checked_in)
            )

            # Store participants in session state for convenience
            try:
                if isinstance(st.session_state, dict):
                    # When being mocked in tests
                    st.session_state["participants"] = participants
                else:
                    # Normal operation
                    st.session_state.participants = participants
            except Exception as e:
                # Log the error but don't fail the operation if session state fails
                print(f"Warning: Failed to update session state: {str(e)}")
            
            # Always return the participants
            return participants

        except ValidationError as e:
            # Enhance validation error with more context when it's a column mapping issue
            if "missing_columns" in getattr(e, "details", {}):
                missing = e.details.get("missing_columns", [])
                available = e.details.get("available_columns", [])
                
                # Add information about column mapping for better user guidance
                e.details["column_mapping_help"] = {
                    "message": "Column names might need to be standardized. Please check your CSV headers.",
                    "common_mappings": {
                        "checked_in_at": ["Check-in Date", "Checkin Date", "Check-in Date (UTC)", "Checkin Date (UTC)"],
                        "email": ["Email", "email", "E-mail", "e-mail"],
                        "first_name": ["First Name", "FirstName", "Name", "first_name"],
                        "last_name": ["Last Name", "LastName", "Surname", "last_name"]
                    }
                }
                
                # Pass through the enhanced error
                raise e
            else:
                raise e

        except DataProcessingError as e:
            # Handle data processing errors
            raise e

        except Exception as e:
            # Wrap other exceptions
            raise DataProcessingError(
                message="Error processing participants file",
                details={"error": str(e)},
                original_exception=e,
            )

    @error_handler
    def get_participant_count(self) -> int:
        """
        Get the number of participants.

        Returns:
            The number of participants
        """
        return len(st.session_state.get("participants", []))

    @error_handler
    def get_participants(self) -> List[Participant]:
        """
        Get all participants.

        Returns:
            A list of all participants
        """
        return st.session_state.get("participants", [])

    @error_handler
    def get_participant_by_email(self, email: str) -> Optional[Participant]:
        """
        Get a participant by their email.

        Args:
            email: The email of the participant to get

        Returns:
            The participant with the given email, or None if not found
        """
        participants = st.session_state.get("participants", [])
        for participant in participants:
            if participant.email.value.lower() == email.lower():
                return participant
        return None

    @error_handler
    def get_participant_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the participants.

        Returns:
            A dictionary with participant statistics
        """
        participants = st.session_state.get("participants", [])

        # Default statistics
        stats = {
            "total_count": len(participants),
            "checked_in_count": 0,
            "domains": {},
            "top_domains": [],
        }

        if not participants:
            return stats

        # Count checked-in participants
        for participant in participants:
            # Count checked in
            if participant.checked_in_at is not None:
                stats["checked_in_count"] += 1

            # Track email domains
            email = participant.email.value
            domain = email.split("@")[-1].lower()

            if domain in stats["domains"]:
                stats["domains"][domain] += 1
            else:
                stats["domains"][domain] = 1

        # Get top domains
        top_domains = sorted(
            stats["domains"].items(), key=lambda x: x[1], reverse=True
        )[
            :5
        ]  # Top 5 domains

        stats["top_domains"] = [
            {"domain": domain, "count": count} for domain, count in top_domains
        ]

        return stats
