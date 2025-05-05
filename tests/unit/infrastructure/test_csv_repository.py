"""
Unit tests for the CSV repository.
"""
import os
import pytest
from typing import List
from pathlib import Path

from domain.models import Participant
from infrastructure.csv_repository import CsvRepository


class TestCsvRepository:
    """Tests for the CsvRepository class."""

    @pytest.fixture
    def sample_csv_path(self) -> str:
        """Get the path to the sample CSV file."""
        # Use the sample data in the root directory
        root_dir = Path(__file__).parent.parent.parent.parent
        return os.path.join(root_dir, "sample_data.csv")

    @pytest.fixture
    def sample_csv_content(self, sample_csv_path: str) -> bytes:
        """Get the content of the sample CSV file."""
        with open(sample_csv_path, "rb") as f:
            return f.read()

    @pytest.fixture
    def csv_repository(self) -> CsvRepository:
        """Create a CsvRepository for testing with example.com allowed."""
        repo = CsvRepository()
        # Clear the email blacklist for testing
        repo.set_email_blacklist(set())
        return repo

    def test_load_participants_from_sample_data(
        self, csv_repository: CsvRepository, sample_csv_content: bytes
    ):
        """Test loading participants from the sample CSV file."""
        # When loading participants from the sample CSV
        participants = csv_repository.load_participants(
            file_content=sample_csv_content, only_checked_in=False
        )

        # Then we should have the expected number of participants
        assert participants is not None
        assert len(participants) == 10

        # Check content of the first participant
        first_participant = participants[0]
        assert first_participant.email.value == "john.doe@example.com"
        assert first_participant.name.first_name == "John"
        assert first_participant.name.last_name == "Doe"
        assert first_participant.checked_in_at is not None
        assert str(first_participant.checked_in_at.value).startswith("2024-03-20")

    def test_load_participants_with_only_checked_in(
        self, csv_repository: CsvRepository, sample_csv_content: bytes
    ):
        """Test loading only checked-in participants."""
        # When loading participants from the sample CSV with only_checked_in=True
        participants = csv_repository.load_participants(
            file_content=sample_csv_content, only_checked_in=True
        )

        # Then we should have the expected number of participants (all are checked in)
        assert participants is not None
        assert len(participants) == 10  # All participants are checked in

    def test_column_normalization(
        self, csv_repository: CsvRepository, sample_csv_content: bytes
    ):
        """Test that column names are properly normalized."""
        # Use direct access to _read_csv_content for testing
        df = csv_repository._read_csv_content(sample_csv_content)
        
        # Check original columns
        orig_columns = list(df.columns)
        assert "Checkin Date (UTC)" in orig_columns
        
        # Normalize columns
        normalized_df = csv_repository._normalize_column_names(df)
        
        # Check normalized columns
        normalized_columns = list(normalized_df.columns)
        assert "checked_in_at" in normalized_columns
        assert "email" in normalized_columns
        assert "first_name" in normalized_columns
        assert "last_name" in normalized_columns

    def test_blacklisted_emails_filtering(
        self, csv_repository: CsvRepository, sample_csv_content: bytes
    ):
        """Test that blacklisted emails are filtered out."""
        # Store the original blacklist state
        original_blacklist = csv_repository.EMAIL_BLACKLIST.copy()
        
        try:
            # First ensure example.com is NOT in the blacklist
            csv_repository.set_email_blacklist(set())
            
            # Load participants - should get all participants
            participants = csv_repository.load_participants(
                file_content=sample_csv_content, only_checked_in=False
            )
            
            assert participants is not None
            assert len(participants) == 10
            
            # Now add example.com to the blacklist
            csv_repository.set_email_blacklist({"example.com"})
            
            # When all emails are blacklisted, the repository might either:
            # 1. Return an empty list (if ValidationError is caught internally)
            # 2. Return None (if validation fails but doesn't raise)
            # 3. Raise a ValidationError (if validation fails and propagates)
            
            # Let's handle all possible outcomes
            try:
                result = csv_repository.load_participants(
                    file_content=sample_csv_content, only_checked_in=False
                )
                # If we get here, no exception was raised
                # The result should be empty since all emails are blacklisted
                assert result is None or result == [], "Expected empty result when all emails are blacklisted"
                
            except Exception as e:
                # If an exception was raised, it should be a ValidationError with the expected message
                assert "No valid participants found" in str(e), f"Expected ValidationError, got: {type(e).__name__}: {str(e)}"
            
        finally:
            # Restore the blacklist
            csv_repository.set_email_blacklist(original_blacklist)