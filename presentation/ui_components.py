"""
Componentes de la interfaz de usuario para la aplicación Streamlit.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

from application.session_service import SessionService
from application.draw_service import DrawService


class UIComponents:
    """Componentes de la interfaz de usuario reutilizables."""
    
    def apply_custom_css(self) -> None:
        """Aplica estilos CSS personalizados a la aplicación."""
        st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .winner-card {
            padding: 1rem;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .stButton button {
            width: 100%;
        }
        .round-header {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def show_welcome_message(self) -> None:
        """Muestra el mensaje de bienvenida e instrucciones iniciales."""
        st.info("Upload a CSV file with the participants list to start")
        
        with st.expander("Expected file format"):
            st.write("""
            The CSV file should contain at least the following columns:
            - 'Checkin Date (UTC)' or 'checked_in_at': Participant's check-in date
            - 'Email' or 'email': Participant's email address
            - 'First Name' or 'first_name': Participant's first name
            - 'Last Name' or 'last_name': Participant's last name
            """)
    
    def show_participants_summary(self, participants: List[Dict[str, Any]]) -> None:
        """
        Muestra un resumen de los participantes.
        
        Args:
            participants: Lista de participantes
        """
        if not participants:
            st.warning("No participants available")
            return
            
        # Crear DataFrame para mostrar
        df = pd.DataFrame(participants)
        st.dataframe(df[['First Name', 'Last Name', 'Email', 'Checkin Date (UTC)']])
    
    def render_round_section(
        self, 
        index: int, 
        round_config: Dict[str, Any], 
        state_manager,
        session_service: SessionService,
        draw_service: DrawService
    ) -> None:
        """
        Renderiza la sección de una ronda con sus configuraciones y opciones.
        
        Args:
            index: Índice de la ronda
            round_config: Configuración de la ronda
            state_manager: Gestor de estado de la sesión
            session_service: Servicio de sesión
            draw_service: Servicio de sorteo
        """
        round_id = round_config['id']
        
        # Título y botón de eliminación
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### Round {index+1}: {round_config['name']}")
        with col2:
            if st.button("Delete Round", key=f"del_round_{index}"):
                session_service.delete_round(index)
                st.experimental_rerun()
        
        # Configuración de la ronda
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input(
                "Round Name", 
                value=round_config['name'], 
                key=f"round_name_{index}"
            )
            session_service.update_round_name(index, new_name)
            
        with col2:
            new_winners = st.number_input(
                "Number of Winners", 
                min_value=1, 
                value=round_config['num_winners'], 
                key=f"num_winners_{index}"
            )
            session_service.update_round_winners(index, new_winners)
        
        # Configuración de premios
        st.subheader("Prizes")
        
        if not round_config['prizes']:
            if st.button("Add Prize", key=f"add_prize_{index}"):
                session_service.add_prize(index)
                st.experimental_rerun()
        
        for j, prize in enumerate(round_config['prizes']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"##### Prize {j+1}")
            with col2:
                if st.button("Delete", key=f"del_prize_{index}_{j}"):
                    session_service.delete_prize(index, j)
                    st.experimental_rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                prize_name = st.text_input(
                    "Prize Name", 
                    value=prize['name'], 
                    key=f"prize_name_{index}_{j}"
                )
                
            with col2:
                prize_desc = st.text_input(
                    "Description", 
                    value=prize['description'], 
                    key=f"prize_desc_{index}_{j}"
                )
                
            session_service.update_prize(index, j, prize_name, prize_desc)
        
        if round_config['prizes']:
            if st.button("Add Another Prize", key=f"add_another_prize_{index}"):
                session_service.add_prize(index)
                st.experimental_rerun()
        
        # Botón para sortear ganadores
        if st.button("Draw Winners", key=f"draw_{index}"):
            participants = state_manager.get_participants()
            
            if participants is None:
                st.error("You must upload a participants file first")
            else:
                exclude_emails = state_manager.get_all_winners_emails()
                num_winners = int(round_config['num_winners'])
                
                winners = draw_service.draw_winners(
                    participants,
                    num_winners,
                    exclude_emails=exclude_emails
                )
                
                if winners:
                    draw_service.register_winners(round_id, winners)
                    st.success(f"{len(winners)} winners were drawn")
                    st.experimental_rerun()
        
        # Mostrar ganadores de esta ronda
        self._render_round_winners(round_id, round_config, state_manager)
        
        st.markdown("---")
    
    def _render_round_winners(self, round_id: int, round_config: Dict[str, Any], state_manager) -> None:
        """
        Renderiza los ganadores de una ronda.
        
        Args:
            round_id: ID de la ronda
            round_config: Configuración de la ronda
            state_manager: Gestor de estado de la sesión
        """
        winners = state_manager.get_winners(round_id)
        
        if winners:
            st.subheader("Winners of this round")
            
            cols = st.columns(min(3, len(winners)))
            
            for j, winner in enumerate(winners):
                with cols[j % len(cols)]:
                    st.markdown(f"""
                    <div class="winner-card">
                        <h4>{winner['First Name']} {winner['Last Name']}</h4>
                        <p>{winner['Email']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Asignar premio si está disponible
                    if j < len(round_config['prizes']):
                        prize = round_config['prizes'][j]
                        st.info(f"Prize: {prize['name']}")
    
    def render_winners_summary(self, state_manager) -> None:
        """
        Renderiza un resumen de todos los ganadores.
        
        Args:
            state_manager: Gestor de estado de la sesión
        """
        all_winners_data = state_manager.get_all_winners_data()
        
        if all_winners_data:
            st.header("Summary of all winners")
            
            winners_df = pd.DataFrame(all_winners_data)
            st.dataframe(winners_df)
            
            # Exportar ganadores a CSV
            csv = winners_df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name=f"winners_{state_manager.get_session_info()['session_id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )