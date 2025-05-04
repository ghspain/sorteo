"""
Gestor del estado de la sesión para la aplicación Streamlit.
"""
import streamlit as st
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class SessionStateManager:
    """Gestiona el estado de la sesión de la aplicación."""

    # PII handling mode constants to avoid magic strings
    PII_MODE_ORIGINAL = "original"      # Keep PII as is
    PII_MODE_MASKED = "masked"          # Mask PII in display outputs
    PII_MODE_PSEUDONYMIZED = "pseudonymized"  # Replace PII with pseudonyms

    def initialize_session_state(self) -> None:
        """Initializes all necessary state variables."""
        if 'participants' not in st.session_state:
            st.session_state.participants = None
        if 'all_winners' not in st.session_state:
            st.session_state.all_winners = []  # List to store all winners
        if 'rounds' not in st.session_state:
            st.session_state.rounds = []  # List to store round configurations
        if 'winners' not in st.session_state:
            st.session_state.winners = []  # For UI display
        if 'session_id' not in st.session_state:
            # Use UUID instead of timestamp for better uniqueness guarantees
            st.session_state.session_id = str(uuid.uuid4())
        if 'drawn_winners' not in st.session_state:
            st.session_state.drawn_winners = {}  # Dictionary to store winners by round
        if 'pii_mode' not in st.session_state:
            st.session_state.pii_mode = self.PII_MODE_MASKED

    def reset_session(self) -> None:
        """Reinicia completamente el estado de la sesión."""
        st.session_state.participants = None
        st.session_state.all_winners = []
        st.session_state.rounds = []
        st.session_state.winners = []
        # Generate a new UUID when resetting the session
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.drawn_winners = {}
        # Keep PII mode as it's a user preference

    def set_participants(self, participants: List[Dict[str, Any]]) -> None:
        """
        Establece la lista de participantes en el estado de la sesión.

        Args:
            participants: Lista de diccionarios con los datos de los participantes
        """
        st.session_state.participants = participants

    def get_participants(self) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene la lista de participantes del estado de la sesión.

        Returns:
            Lista de participantes o None si no hay participantes
        """
        return st.session_state.participants if 'participants' in st.session_state else None

    def get_rounds(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de rondas del estado de la sesión.

        Returns:
            Lista de configuraciones de rondas
        """
        return st.session_state.rounds if 'rounds' in st.session_state else []

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

    def set_pii_mode(self, pii_mode: str) -> bool:
        """
        Sets the PII handling mode.

        Args:
            pii_mode: The PII handling mode to use

        Returns:
            True if the mode was changed, False otherwise
        """
        if pii_mode not in (
            self.PII_MODE_ORIGINAL,
            self.PII_MODE_MASKED,
            self.PII_MODE_PSEUDONYMIZED
        ):
            return False

        if st.session_state.pii_mode != pii_mode:
            st.session_state.pii_mode = pii_mode
            return True
        return False

    def get_pii_mode(self) -> str:
        """
        Gets the current PII handling mode.

        Returns:
            The current PII handling mode
        """
        return st.session_state.pii_mode if 'pii_mode' in st.session_state else self.PII_MODE_MASKED

    def get_session_id(self) -> str:
        """
        Gets the current session ID.

        Returns:
            The current session ID
        """
        return st.session_state.session_id if 'session_id' in st.session_state else ""

    def get_all_winners(self) -> List[Dict[str, Any]]:
        """
        Gets the list of all winners for UI display.

        Returns:
            List of all winners
        """
        return st.session_state.winners if 'winners' in st.session_state else []