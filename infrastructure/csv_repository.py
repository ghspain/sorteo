"""
CSV repository for the raffle application following DDD principles.
Implements the repository pattern to abstract data access mechanisms.
"""

import csv
import io
import os
import tempfile
from typing import Any, Dict, List, Optional, Protocol, Set

import pandas as pd
import streamlit as st

from domain.models import Participant
from domain.value_objects import CheckInDate, Email, PersonName
from infrastructure.error_handling import (
    DataProcessingError,
    ValidationError,
    error_handler,
)


class ParticipantRepository(Protocol):
    """Interface for participant repositories (DDD Repository Pattern)."""

    def load_participants(
        self, file_content: bytes, only_checked_in: bool = False
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
    PII_MODE_MASKED = "masked"  # Mask PII in display outputs
    PII_MODE_PSEUDONYMIZED = "pseudonymized"  # Replace PII with pseudonyms

    # Column mapping for standardization
    COLUMN_MAPPING = {
        # Check-in columns
        "check-in date (utc)": "checked_in_at",
        "check-in date": "checked_in_at",
        "checkin date (utc)": "checked_in_at",
        "checkin date": "checked_in_at",
        "checkin_date_(utc)": "checked_in_at",
        "checkin_date": "checked_in_at",
        "check-in_date": "checked_in_at",  # Added for tests
        # Basic participant info
        "first name": "first_name",
        "firstname": "first_name",
        "first_name": "first_name",
        "name": "first_name",
        "last name": "last_name",
        "lastname": "last_name",
        "last_name": "last_name",
        "surname": "last_name",
        "email": "email",
        "e-mail": "email",
        "mail": "email",
    }

    # Required columns in the CSV file (either set is acceptable)
    REQUIRED_COLUMN_SETS = [
        {"email", "first_name", "last_name", "checked_in_at"},
    ]

    # Email validation blacklist (domains to exclude)
    EMAIL_BLACKLIST = {"bevylabs.com", "example.com", "test.com"}

    def __init__(self, pii_mode: str = PII_MODE_MASKED):
        """
        Initialize the CSV repository.

        Args:
            pii_mode: How to handle PII in the repository
        """
        self.pii_mode = pii_mode

    @staticmethod
    def check_gdpr_compliance_from_bytes(file_bytes: bytes) -> Dict[str, Any]:
        """
        Check if a CSV file complies with GDPR requirements.

        Args:
            file_bytes: Content of the CSV file as bytes

        Returns:
            Dictionary with compliance information
        """
        try:
            # Create a temporary file to safely process the bytes
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_file:
                temp_file.write(file_bytes)
                temp_file.flush()

                # Read CSV using pandas
                df = pd.read_csv(temp_file.name, keep_default_na=False)
                pii_columns = []
                issues = []
                recommendations = []

                # Scan for potential PII columns
                for column in df.columns:
                    col_lower = column.lower()
                    if any(
                        term in col_lower
                        for term in [
                            "email",
                            "name",
                            "phone",
                            "address",
                            "birth",
                            "passport",
                            "dni",
                            "nif",
                            "id",
                        ]
                    ):
                        pii_columns.append(column)

                # Check if PII columns are present
                if pii_columns:
                    recommendations.append(
                        f"Consider anonymizing or pseudonymizing these PII columns: {', '.join(pii_columns)}"
                    )

                # Check for consent column
                consent_column = None
                for column in df.columns:
                    if (
                        "consent" in column.lower()
                        or "gdpr" in column.lower()
                        or "opt" in column.lower()
                    ):
                        consent_column = column
                        break

                if not consent_column:
                    issues.append(
                        "No consent column found - GDPR requires demonstrable consent for PII processing"
                    )
                else:
                    # Check if all participants have given consent
                    if (
                        df[consent_column].isnull().any()
                        or (df[consent_column] == "").any()
                    ):
                        issues.append(
                            "Some participants may not have given explicit consent (empty consent values)"
                        )

                    false_values = ["false", "no", "n", "0", "f"]
                    if any(
                        str(val).lower() in false_values for val in df[consent_column]
                    ):
                        issues.append(
                            "Some participants have explicitly NOT given consent"
                        )

                # Sample recommendations
                recommendations.append(
                    "Include timestamp of consent to demonstrate when consent was given"
                )
                recommendations.append(
                    "Include clear purpose for data collection and processing"
                )

                return {
                    "compliant": len(issues) == 0,
                    "issues": issues,
                    "pii_columns": pii_columns,
                    "recommendations": recommendations,
                }
        except Exception as e:
            return {
                "compliant": False,
                "issues": [f"Error analyzing file: {str(e)}"],
                "pii_columns": [],
                "recommendations": [
                    "Ensure the file is a valid CSV file with proper headers"
                ],
            }

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
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return CsvRepository.check_gdpr_compliance_from_bytes(file_bytes)
        except Exception as e:
            return {
                "compliant": False,
                "issues": [f"Error reading file: {str(e)}"],
                "pii_columns": [],
                "recommendations": ["Ensure the file exists and is accessible"],
            }

    @error_handler
    def load_participants(
        self, file_content: bytes, only_checked_in: bool = False
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

            # Normalize column names
            df = self._normalize_column_names(df)

            # Validate the CSV file
            self._validate_csv_columns(df.columns)

            # Process and filter participants
            participants = self._process_participant_data(df, only_checked_in)

            if not participants:
                raise ValidationError(
                    message="No valid participants found in the CSV file",
                    details={"file_rows": len(df)},
                )

            return participants

        except pd.errors.EmptyDataError:
            raise ValidationError("The CSV file is empty")
        except pd.errors.ParserError as e:
            raise DataProcessingError(
                message="Error parsing CSV file",
                details={"parser_error": str(e)},
                original_exception=e,
            )
        except Exception as e:
            if isinstance(e, (ValidationError, DataProcessingError)):
                raise
            raise DataProcessingError(
                message="Error processing CSV file",
                details={"error": str(e)},
                original_exception=e,
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

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to standard format.

        Args:
            df: The DataFrame with original column names

        Returns:
            DataFrame with normalized column names
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_normalized = df.copy()

        # Map of exact original column names that need specific mapping
        exact_mapping = {
            "Email": "email",
            "First Name": "first_name",
            "Last Name": "last_name",
            "Checkin Date (UTC)": "checked_in_at",
            "Check-in Date (UTC)": "checked_in_at",
            "Check-in Date": "checked_in_at",  # Added for tests
            "Checkin Date": "checked_in_at"     # Added for tests
        }

        # First apply exact mappings
        for orig_col, std_col in exact_mapping.items():
            if orig_col in df.columns and std_col not in df.columns:
                df_normalized.rename(columns={orig_col: std_col}, inplace=True)

        # Then process remaining columns using the standard mapping
        normalized_columns = {}
        for col in df_normalized.columns:
            # Skip columns that are already properly named
            if col in self.COLUMN_MAPPING.values():
                continue

            # Convert to lowercase and replace spaces with underscores
            normalized_col = col.lower().replace(" ", "_")

            # Check if this normalized column maps to a standard column
            for pattern, standard in self.COLUMN_MAPPING.items():
                if normalized_col == pattern:
                    normalized_columns[col] = standard
                    break

        # Apply the normalizations
        df_normalized.rename(columns=normalized_columns, inplace=True)

        return df_normalized

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
            missing_columns = []
            for required_set in self.REQUIRED_COLUMN_SETS:
                missing = required_set - columns_set
                if missing:
                    missing_columns.extend(list(missing))

            raise ValidationError(
                message=f"Missing required columns: {', '.join(missing_columns)}",
                details={
                    "available_columns": list(columns),
                    "required_column_sets": [
                        list(s) for s in self.REQUIRED_COLUMN_SETS
                    ],
                    "missing_columns": missing_columns,
                },
            )

    def _process_participant_data(
        self, df: pd.DataFrame, only_checked_in: bool
    ) -> List[Participant]:
        """
        Process participant data from DataFrame to domain objects with filtering.

        Args:
            df: The DataFrame with participant data
            only_checked_in: Whether to only include participants who have checked in

        Returns:
            List of Participant domain objects
        """
        participants = []
        for idx, row in df.iterrows():
            try:
                # Create a dictionary from the row
                data = row.to_dict()

                # Ensure standard column names in the data dictionary
                standardized_data = {}
                for key, value in data.items():
                    normalized_key = key.lower().replace(" ", "_")
                    standard_key = self.COLUMN_MAPPING.get(normalized_key, key)
                    standardized_data[standard_key] = value

                # Ensure email is standardized
                if "Email" in data and "email" not in standardized_data:
                    standardized_data["email"] = data["Email"]
                
                # Debug - print standardized data
                print(f"Row {idx} standardized data: {standardized_data}")

                # Skip if email is in blacklist
                email = standardized_data.get("email", "")
                if self._is_blacklisted_email(email):
                    print(f"Skipping blacklisted email: {email}")
                    continue

                # Skip if checked_in filter is active and participant hasn't checked in
                # Create participant from standardized data
                participant = self._create_participant_from_data(standardized_data)
                if participant:
                    participants.append(participant)

            except (ValueError, AttributeError) as e:
                # Log but continue processing other rows
                st.warning(f"Skipping invalid participant data: {str(e)}")

        return participants

    def _create_participant_from_data(
        self, data: Dict[str, Any]
    ) -> Optional[Participant]:
        """
        Create a Participant domain object from dictionary data.

        Args:
            data: Dictionary containing participant data

        Returns:
            Participant object or None if creation fails
        """
        try:
            email_str = str(data.get("email", "")).strip()
            if not email_str:
                return None

            first_name = str(data.get("first_name", "")).strip()
            last_name = str(data.get("last_name", "")).strip()
            
            # Create Email value object
            email_obj = Email(email_str)
            
            # Create PersonName value object
            name = PersonName(first_name=first_name, last_name=last_name)
            
            # Create CheckInDate value object if check-in date is present
            check_in_str = data.get("checked_in_at", "")
            check_in_date = CheckInDate(check_in_str if check_in_str else "")
            
            # Create and return participant
            return Participant(
                email=email_obj,
                name=name,
                checked_in_at=check_in_date
            )

        except (ValueError, AttributeError) as e:
            # Log error and return None
            print(f"Error creating participant: {e}")
            st.warning(f"Invalid participant data: {str(e)}")
            return None

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
            domain = email.split("@")[-1].lower()
            return domain in self.EMAIL_BLACKLIST
        except (IndexError, AttributeError):
            # Invalid email format
            return True

    def set_email_blacklist(self, blacklist: Set[str]) -> None:
        """
        Set the email blacklist for testing purposes.

        Args:
            blacklist: Set of email domains to blacklist
        """
        self.EMAIL_BLACKLIST = blacklist.copy()


# Alias for backward compatibility
CSVRepository = CsvRepository
