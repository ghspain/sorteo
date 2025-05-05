import os
import sys
import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from domain.models import Participant, Round, Prize
from domain.value_objects import Email, PersonName, CheckInDate
from application.draw_service import DrawService
from infrastructure.csv_repository import CSVRepository


class TestDrawService:
    
    def setup_method(self):
        """Set up test data before each test."""
        # Create test participants using proper value objects
        self.participants = [
            Participant(
                email=Email("p1@example.com"), 
                name=PersonName("P1", "Test"),
                checked_in_at=CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                email=Email("p2@example.com"), 
                name=PersonName("P2", "Test"),
                checked_in_at=CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                email=Email("p3@example.com"), 
                name=PersonName("P3", "Test"),
                checked_in_at=CheckInDate("2023-05-01T10:30:00Z")
            ),
            Participant(
                email=Email("p4@example.com"), 
                name=PersonName("P4", "Test"),
                checked_in_at=CheckInDate("")  # Not checked in
            ),
            Participant(
                email=Email("p5@example.com"), 
                name=PersonName("P5", "Test"),
                checked_in_at=CheckInDate("2023-05-01T10:30:00Z")
            )
        ]
        
        # Create rounds correctly - create rounds first then add prizes
        self.round1 = Round(id=1, name="Round 1", num_winners=1)
        self.round1.add_prize(Prize(id=1, name="Prize A"))
        
        self.round2 = Round(id=2, name="Round 2", num_winners=2)
        self.round2.add_prize(Prize(id=2, name="Prize B"))
        self.round2.add_prize(Prize(id=3, name="Prize C"))
        
        self.rounds = [self.round1, self.round2]
        
        # Set up mock repository with our test data
        self.repository = CSVRepository()
        
        # Initialize the draw service
        self.draw_service = DrawService(repository=self.repository)
        
        # Override the repository's get_all_participants method to return our test data
        self.draw_service.repository.get_all_participants = lambda: self.participants
        
    def test_draw_winners_one_round(self):
        """Test drawing winners for a single round."""
        # Perform the draw
        winners = self.draw_service.draw_winners(
            num_winners=1,
            only_checked_in=True,
            exclude_emails=[]
        )
        
        # Assertions
        assert len(winners) == 1
        assert winners[0].checked_in_at.is_checked_in
    
    def test_draw_winners_multiple_rounds_unique(self):
        """Test that winners are unique across multiple rounds."""
        # Draw for the first round
        winners_round1 = self.draw_service.draw_winners(
            num_winners=1,
            only_checked_in=True,
            exclude_emails=[]
        )
        
        # Get emails of first round winners
        emails_round1 = [w.email.value for w in winners_round1]
        
        # Draw for the second round, ensuring first round winners are excluded
        winners_round2 = self.draw_service.draw_winners(
            num_winners=2,
            only_checked_in=True,
            exclude_emails=emails_round1
        )
        
        # Assertions
        assert len(winners_round2) == 2
        # Check that no winner from round 1 is in round 2
        for winner in winners_round1:
            assert winner not in winners_round2
    
    def test_draw_winners_checked_in_only(self):
        """Test that only checked-in participants are selected."""
        # Perform the draw with only_checked_in=True
        winners = self.draw_service.draw_winners(
            num_winners=2,
            only_checked_in=True,
            exclude_emails=[]
        )
        
        # Assertions
        assert len(winners) == 2
        for winner in winners:
            assert winner.checked_in_at.is_checked_in