"""
Gestor del estado de la sesión para la aplicación Streamlit.
"""
import streamlit as st
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from domain.models import Participant
from domain.constants import PiiMode


class SessionStateManager:
    """Manager for handling session state in Streamlit."""

    def initialize_session_state(self) -> None:
        """Initialize the session state with default values."""
        if "participants" not in st.session_state:
            st.session_state.participants = []
        if "rounds" not in st.session_state:
            st.session_state.rounds = []
        if "winners" not in st.session_state:
            st.session_state.winners = []
        if "pii_mode" not in st.session_state:
            st.session_state.pii_mode = PiiMode.MASKED
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        if 'drawn_winners' not in st.session_state:
            st.session_state.drawn_winners = {}

    def reset_session(self) -> None:
        """Reset the session state."""
        st.session_state.participants = []
        st.session_state.rounds = []
        st.session_state.winners = []
        # Generate new session ID
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.drawn_winners = {}

    def set_participants(self, participants: List[Participant]) -> None:
        """Set the list of participants.

        Args:
            participants: List of participants
        """
        st.session_state.participants = participants

    def get_participants(self) -> Optional[List[Participant]]:
        """Get the list of participants.

        Returns:
            List of participants
        """
        return st.session_state.get("participants", [])

    def get_rounds(self) -> List[Dict[str, Any]]:
        """Get the list of rounds.

        Returns:
            List of rounds
        """
        return st.session_state.get("rounds", [])

    def get_winners(self, round_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de ganadores para una ronda específica.

        Args:
            round_id: ID de la ronda

        Returns:
            Lista de ganadores para esa ronda o lista vacía si no hay ganadores
        """
        if 'drawn_winners' in st.session_state and round_id in st.session_state.drawn_winners:
            return st.session_state.drawn_winners[round_id]
        return []

    def get_all_winners_emails(self) -> List[str]:
        """
        Obtiene la lista de emails de todos los ganadores.

        Returns:
            Lista de emails de todos los ganadores
        """
        return st.session_state.all_winners if 'all_winners' in st.session_state else []

    def get_session_info(self) -> Dict[str, Any]:
        """
        Obtiene información general sobre la sesión actual.

        Returns:
            Diccionario con información de la sesión
        """
        session_info = {
            'session_id': st.session_state.session_id if 'session_id' in st.session_state else '',
            'participants': st.session_state.participants,
            'total_participants': len(st.session_state.participants) if st.session_state.participants is not None else 0,
            'total_winners': len(st.session_state.all_winners) if 'all_winners' in st.session_state else 0,
            'total_rounds': len(st.session_state.rounds) if 'rounds' in st.session_state else 0
        }
        return session_info

    def get_all_winners_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de todos los ganadores con información de ronda y premio.

        Returns:
            Lista de diccionarios con información detallada de cada ganador
        """
        all_winners_data = []

        if 'drawn_winners' not in st.session_state or not st.session_state.drawn_winners:
            return all_winners_data

        for round_id, winners in st.session_state.drawn_winners.items():
            # Obtener nombre de la ronda
            round_name = next(
                (r['name'] for r in st.session_state.rounds if r['id'] == round_id),
                f"Ronda {round_id}"
            )

            # Obtener configuración de la ronda para los premios
            round_config = next(
                (r for r in st.session_state.rounds if r['id'] == round_id),
                None
            )

            for i, winner in enumerate(winners):
                winner_data = {
                    'Ronda': round_name,
                    'Nombre': f"{winner['First Name']} {winner['Last Name']}",
                    'Email': winner['Email']
                }

                # Añadir información del premio si está disponible
                if round_config and i < len(round_config['prizes']):
                    winner_data['Premio'] = round_config['prizes'][i]['name']
                else:
                    winner_data['Premio'] = '-'

                all_winners_data.append(winner_data)

        return all_winners_data

    def set_pii_mode(self, mode: str) -> None:
        """Set the PII mode.

        Args:
            mode: PII mode
        """
        if mode in (
            PiiMode.ORIGINAL,
            PiiMode.MASKED,
            PiiMode.PSEUDONYMIZED
        ):
            st.session_state.pii_mode = mode

    def get_pii_mode(self) -> str:
        """Get the PII mode.

        Returns:
            PII mode
        """
        return st.session_state.get("pii_mode", PiiMode.MASKED)

    def get_session_id(self) -> str:
        """Get the session ID.

        Returns:
            Session ID
        """
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id

    def get_all_winners(self) -> List[Dict[str, Any]]:
        """
        Gets the list of all winners for UI display.

        Returns:
            List of all winners
        """
        return st.session_state.winners if 'winners' in st.session_state else []