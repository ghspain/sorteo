"""
Unit tests for the Participant Service.
"""
import os
import pytest
from typing import List, Dict, Any
from pathlib import Path
from unittest.mock import MagicMock, patch

import streamlit as st
from domain.models import Participant
from infrastructure.csv_repository import CsvRepository
from application.participant_service import ParticipantService


class TestParticipantService:
    """Tests for the ParticipantService class."""

    @pytest.fixture
    def sample_csv_path(self) -> str:
        """Get the path to the sample CSV file."""
        root_dir = Path(__file__).parent.parent.parent.parent
        return os.path.join(root_dir, "sample_data.csv")

    @pytest.fixture
    def sample_csv_content(self, sample_csv_path: str) -> bytes:
        """Get the content of the sample CSV file."""
        with open(sample_csv_path, "rb") as f:
            return f.read()

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Create a mock repository for testing."""
        return MagicMock(spec=CsvRepository)

    @pytest.fixture
    def participant_service(self, mock_repository) -> ParticipantService:
        """Create a ParticipantService with a mock repository for testing."""
        return ParticipantService(repository=mock_repository)

    @pytest.fixture
    def real_repository(self) -> CsvRepository:
        """Create a real CSV repository for integration tests."""
        # Temporarily disable blacklisting example.com for these tests
        repo = CsvRepository()
        repo.EMAIL_BLACKLIST.discard("example.com")
        return repo

    @pytest.fixture
    def real_participant_service(self, real_repository) -> ParticipantService:
        """Create a ParticipantService with a real repository for integration tests."""
        return ParticipantService(repository=real_repository)

    def test_process_participants_file_with_mock(
        self, participant_service: ParticipantService, mock_repository: MagicMock, sample_csv_content: bytes
    ):
        """Test processing participants file with mocked repository."""
        # Arrange
        mock_participants = [
            MagicMock(spec=Participant),
            MagicMock(spec=Participant),
        ]
        mock_repository.load_participants.return_value = mock_participants
        
        # Act
        with patch("application.participant_service.st.session_state", {}):
            result = participant_service.process_participants_file(
                file_content=sample_csv_content, only_checked_in=True
            )
        
        # Assert
        mock_repository.load_participants.assert_called_once_with(
            file_content=sample_csv_content, only_checked_in=True
        )
        assert result == mock_participants
        
    def test_process_participants_file_integration(
        self, real_participant_service: ParticipantService, sample_csv_content: bytes
    ):
        """Integration test for processing participants file with real repository."""
        # Arrange
        # Use a patch for session_state to avoid modifying the real one
        with patch("application.participant_service.st.session_state", {}):
            # Act
            result = real_participant_service.process_participants_file(
                file_content=sample_csv_content, only_checked_in=False
            )
        
        # Assert
        assert result is not None
        assert len(result) == 10
        
        # Check that the first participant matches expected data
        first_participant = result[0]
        assert first_participant.email.value == "john.doe@example.com"
        assert first_participant.name.first_name == "John"
        assert first_participant.name.last_name == "Doe"
        assert first_participant.checked_in_at is not None
    
    def test_process_participants_file_only_checked_in(
        self, real_participant_service: ParticipantService, sample_csv_content: bytes
    ):
        """Test filtering of checked-in participants."""
        # Arrange
        with patch("application.participant_service.st.session_state", {}):
            # Act
            result = real_participant_service.process_participants_file(
                file_content=sample_csv_content, only_checked_in=True
            )
        
        # Assert
        assert result is not None
        assert len(result) == 10  # All participants in the sample are checked in
    
    def test_get_participant_statistics(
        self, real_participant_service: ParticipantService, sample_csv_content: bytes
    ):
        """Test getting participant statistics after processing participants."""
        # Arrange
        session_state_mock = {}
        
        # Process participants and store in session state
        with patch("application.participant_service.st.session_state", session_state_mock):
            real_participant_service.process_participants_file(
                file_content=sample_csv_content, only_checked_in=False
            )
            
            # Act
            stats = real_participant_service.get_participant_statistics()
        
        # Assert
        assert stats["total_count"] == 10
        assert stats["checked_in_count"] == 10  # All participants are checked in
        assert "example.com" in stats["domains"]
        assert stats["domains"]["example.com"] == 10  # All emails are from example.com
        assert len(stats["top_domains"]) > 0
        assert stats["top_domains"][0]["domain"] == "example.com"