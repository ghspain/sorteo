"""
Unit tests for raffle winner absence handling.
"""
from unittest.mock import patch

from application.raffle_service import RaffleService
from domain.models import Participant
from domain.value_objects import CheckInDate, Email, PersonName


class SessionState(dict):
    """Dictionary with attribute access to mimic Streamlit session state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def make_participant(email: str, first_name: str = "Test") -> Participant:
    """Create a checked-in participant for tests."""
    return Participant(
        email=Email(email),
        name=PersonName(first_name, "User"),
        checked_in_at=CheckInDate("2024-05-04 10:00:00"),
    )


def make_winner(participant: Participant, round_id: int = 1) -> dict:
    """Create winner session data from a participant."""
    winner = participant.to_dict()
    winner.update({
        "round_id": round_id,
        "selected_at": "2024-05-04T10:00:00",
        "is_absent": False,
        "is_replacement": False,
    })
    return winner


class TestRaffleService:
    """Tests for RaffleService absent winner behavior."""

    def test_select_winners_excludes_previous_and_absent_winners(self):
        """Selecting winners ignores previous winners and absent participants."""
        participants = [
            make_participant("winner@example.org", "Winner"),
            make_participant("absent@example.org", "Absent"),
            make_participant("eligible@example.org", "Eligible"),
        ]
        session_state = SessionState({
            "winners": [],
            "drawn_winners": {},
            "all_winners": ["winner@example.org"],
            "absent_participants": ["absent@example.org"],
            "rounds": [{"id": 1, "name": "Round 1", "num_winners": 1, "prizes": []}],
        })

        with patch("application.raffle_service.st.session_state", session_state):
            winners = RaffleService().select_winners(1, participants, 1)

        assert [winner.email.value for winner in winners] == ["eligible@example.org"]
        assert session_state.all_winners == ["winner@example.org", "eligible@example.org"]
        assert session_state.drawn_winners[1][0]["Email"] == "eligible@example.org"

    def test_mark_winner_absent_draws_replacement(self):
        """Marking an absent winner appends a replacement and links it to the original."""
        original = make_participant("original@example.org", "Original")
        replacement = make_participant("replacement@example.org", "Replacement")
        original_winner = make_winner(original)
        session_state = SessionState({
            "participants": [original, replacement],
            "winners": [original_winner],
            "drawn_winners": {1: [original_winner]},
            "all_winners": ["original@example.org"],
            "absent_participants": [],
            "rounds": [{"id": 1, "name": "Round 1", "num_winners": 1, "prizes": []}],
        })

        with patch("application.raffle_service.st.session_state", session_state):
            with patch("application.raffle_service.random.choice", return_value=replacement):
                replacement_drawn = RaffleService().mark_winner_absent(1, 0)

        assert replacement_drawn is True
        assert session_state.drawn_winners[1][0]["is_absent"] is True
        assert session_state.absent_participants == ["original@example.org"]
        assert session_state.drawn_winners[1][1]["Email"] == "replacement@example.org"
        assert session_state.drawn_winners[1][1]["is_replacement"] is True
        assert session_state.drawn_winners[1][1]["replaced"] == "original@example.org"
        assert "replacement@example.org" in session_state.all_winners

    def test_mark_winner_absent_without_replacement_keeps_absent_status(self):
        """An absent winner remains marked absent when no replacement is available."""
        original = make_participant("original@example.org", "Original")
        original_winner = make_winner(original)
        session_state = SessionState({
            "participants": [original],
            "winners": [original_winner],
            "drawn_winners": {1: [original_winner]},
            "all_winners": ["original@example.org"],
            "absent_participants": [],
            "rounds": [{"id": 1, "name": "Round 1", "num_winners": 1, "prizes": []}],
        })

        with patch("application.raffle_service.st.session_state", session_state):
            replacement_drawn = RaffleService().mark_winner_absent(1, 0)

        assert replacement_drawn is False
        assert session_state.drawn_winners[1][0]["is_absent"] is True
        assert session_state.absent_participants == ["original@example.org"]
        assert len(session_state.drawn_winners[1]) == 1

    def test_assign_prize_uses_replaced_winner_index(self):
        """A replacement inherits the prize assigned to the winner it replaces."""
        service = RaffleService()
        winners = [
            {"Email": "first@example.org", "is_replacement": False},
            {"Email": "second@example.org", "is_replacement": False},
            {
                "Email": "replacement@example.org",
                "is_replacement": True,
                "replaced": "second@example.org",
            },
        ]
        round_config = {
            "prizes": [
                {"name": "First prize"},
                {"name": "Second prize"},
            ]
        }

        assert service.assign_prize(winners[2], winners, round_config) == "Second prize"