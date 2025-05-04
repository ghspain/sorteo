"""
CSV repository for the raffle application following DDD principles.
Implements the repository pattern to abstract data access mechanisms.
"""
import csv
import io
import os
from typing import List, Dict, Any, Optional, Set, Protocol

import pandas as pd
import streamlit as st

from domain.models import Participant
from domain.value_objects import Email, PersonName, CheckInDate
from infrastructure.error_handling import ValidationError, DataProcessingError, error_handler


class ParticipantRepository(Protocol):
    """Interface for participant repositories (DDD Repository Pattern)."""

    def load_participants(
        self,
        file_content: bytes,
        only_checked_in: bool = False
    ) -> List[Participant]:
        """Load participants from a data source."""
        ...


class CsvRepository:
    """
    Repository for loading participants from CSV files.
    Follows SOLID principles by:
    - Single Responsibility: Focuses only on CSV data access
    - Open/Closed: Extensible for different filtering options
    - Liskov Substitution: Implements ParticipantRepository interface
    - Interface Segregation: Provides focused interface methods
    - Dependency Inversion: Depends on domain abstractions
    """

    # PII handling mode constants
    PII_MODE_ORIGINAL = "original"  # Keep PII as is
    PII_MODE_MASKED = "masked"      # Mask PII in display outputs
    PII_MODE_PSEUDONYMIZED = "pseudonymized"  # Replace PII with pseudonyms

    # Required columns in the CSV file (either set is acceptable)
    REQUIRED_COLUMN_SETS = [
        {'Email', 'First Name', 'Last Name', 'Check-in Date (UTC)'},
        {'email', 'first_name', 'last_name', 'checked_in_at'}
    ]

    # Email validation blacklist (domains to exclude)
    EMAIL_BLACKLIST = {'bevylabs.com', 'example.com', 'test.com'}

    def __init__(self, pii_mode: str = PII_MODE_MASKED):
        """
        Initialize the CSV repository.
        
        Args:
            pii_mode: How to handle PII in the repository
        """
        self.pii_mode = pii_mode
        
    @staticmethod
    def check_gdpr_compliance(file_path: str) -> Dict[str, Any]:
        """
        Check if a CSV file complies with GDPR requirements.
        
        Args:
            file_path: Path to the CSV file to check
            
        Returns:
            Dictionary with compliance information
        """
        try:
            df = pd.read_csv(file_path, keep_default_na=False)
            pii_columns = []
            issues = []
            recommendations = []
            
            # Scan for potential PII columns
            for column in df.columns:
                col_lower = column.lower()
                if any(term in col_lower for term in ['email', 'name', 'phone', 'address', 'birth', 'passport', 'dni', 'nif', 'id']):
                    pii_columns.append(column)
            
            # Check if PII columns are present
            if pii_columns:
                recommendations.append(f"Consider anonymizing or pseudonymizing these PII columns: {', '.join(pii_columns)}")
            
            # Check for consent column
            consent_column = None
            for column in df.columns:
                if 'consent' in column.lower() or 'gdpr' in column.lower() or 'opt' in column.lower():
                    consent_column = column
                    break
            
            if not consent_column:
                issues.append("No consent column found - GDPR requires demonstrable consent for PII processing")
            else:
                # Check if all participants have given consent
                if df[consent_column].isnull().any() or (df[consent_column] == '').any():
                    issues.append("Some participants may not have given explicit consent (empty consent values)")
                
                false_values = ['false', 'no', 'n', '0', 'f']
                if any(str(val).lower() in false_values for val in df[consent_column]):
                    issues.append("Some participants have explicitly NOT given consent")
            
            # Sample recommendations
            recommendations.append("Include timestamp of consent to demonstrate when consent was given")
            recommendations.append("Include clear purpose for data collection and processing")
            
            return {
                'compliant': len(issues) == 0,
                'issues': issues,
                'pii_columns': pii_columns,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'compliant': False,
                'issues': [f"Error analyzing file: {str(e)}"],
                'pii_columns': [],
                'recommendations': ["Ensure the file is a valid CSV file with proper headers"]
            }
            
    @error_handler
    def load_participants(
        self,
        file_content: bytes,
        only_checked_in: bool = False
    ) -> List[Participant]:
        """
        Load participants from a CSV file.

        Args:
            file_content: The content of the CSV file
            only_checked_in: Whether to only include participants who have checked in

        Returns:
            A list of Participant objects

        Raises:
            ValidationError: If the CSV file is invalid
            DataProcessingError: If there's an error processing the CSV file
        """
        try:
            # Read the CSV file
            df = self._read_csv_content(file_content)

            # Validate the CSV file
            self._validate_csv_columns(df.columns)

            # Process and filter participants
            participants = self._process_participant_data(df, only_checked_in)

            if not participants:
                raise ValidationError(
                    message="No valid participants found in the CSV file",
                    details={"file_rows": len(df)}
                )

            return participants

        except pd.errors.EmptyDataError:
            raise ValidationError("The CSV file is empty")
        except pd.errors.ParserError as e:
            raise DataProcessingError(
                message="Error parsing CSV file",
                details={"parser_error": str(e)},
                original_exception=e
            )
        except Exception as e:
            if isinstance(e, (ValidationError, DataProcessingError)):
                raise
            raise DataProcessingError(
                message="Error processing CSV file",
                details={"error": str(e)},
                original_exception=e
            )

    def _read_csv_content(self, file_content: bytes) -> pd.DataFrame:
        """
        Read and parse CSV content into a DataFrame.

        Args:
            file_content: The raw bytes of the CSV file

        Returns:
            A pandas DataFrame
        """
        return pd.read_csv(io.BytesIO(file_content), keep_default_na=False)

    def _validate_csv_columns(self, columns: List[str]) -> None:
        """
        Validate that the CSV file has the required columns.

        Args:
            columns: The columns in the CSV file

        Raises:
            ValidationError: If the CSV file doesn't have the required columns
        """
        columns_set = set(columns)

        # Check if any required column set is a subset of the actual columns
        valid_columns = any(
            required_set.issubset(columns_set)
            for required_set in self.REQUIRED_COLUMN_SETS
        )

        if not valid_columns:
            raise ValidationError(
                message="Required columns not found in CSV file",
                details={
                    "available_columns": list(columns),
                    "required_column_sets": [list(s) for s in self.REQUIRED_COLUMN_SETS]
                }
            )

    def _process_participant_data(self, df: pd.DataFrame, only_checked_in: bool) -> List[Participant]:
        """
        Process participant data from DataFrame to domain objects with filtering.

        Args:
            df: The DataFrame with participant data
            only_checked_in: Whether to only include participants who have checked in

        Returns:
            List of Participant domain objects
        """
        participants = []
        for _, row in df.iterrows():
            try:
                # Create a dictionary from the row
                data = row.to_dict()

                # Skip if email is in blacklist
                email = data.get('Email') or data.get('email', '')
                if self._is_blacklisted_email(email):
                    continue

                # Skip if checked_in filter is active and participant hasn't checked in
                checked_in = data.get('Checkin Date (UTC)') or data.get('checked_in_at', '')
                if only_checked_in and not checked_in.strip():
                    continue

                # Create participant
                participant = Participant.from_dict(data)
                participants.append(participant)

            except (ValueError, AttributeError) as e:
                # Log but continue processing other rows
                st.warning(f"Skipping invalid participant data: {str(e)}")

        return participants

    def _is_blacklisted_email(self, email: str) -> bool:
        """
        Check if an email is blacklisted.

        Args:
            email: The email to check

        Returns:
            True if the email is blacklisted, False otherwise
        """
        if not email:
            return True

        try:
            domain = email.split('@')[-1].lower()
            return domain in self.EMAIL_BLACKLIST
        except (IndexError, AttributeError):
            # Invalid email format
            return True

# Alias for backward compatibility
CSVRepository = CsvRepository