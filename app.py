#!/usr/bin/env python3

# Set page configuration
"""
Punto de entrada principal de la aplicación Streamlit de sorteos.
Este archivo solo maneja la interfaz de usuario y delega la lógica
a las capas de aplicación y dominio.
"""
import streamlit as st
import pandas as pd
import csv
import random
import io
import uuid
import os
from datetime import datetime

# Importamos las clases de las diferentes capas
from domain.models import Participant, Round, Prize
from application.session_service import SessionService
from application.participant_service import ParticipantService  
from application.draw_service import DrawService
from infrastructure.csv_repository import CSVRepository
from presentation.ui_components import UIComponents
from presentation.session_state_manager import SessionStateManager
from utils.csv_privacy import anonymize_csv, check_gdpr_compliance

# Configuración de la página
st.set_page_config(
    page_title="Sorteo de Eventos",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS for making it look nicer
st.markdown("""
<style>
.main {
    padding: 2rem;
}
.winner-card {
    padding: 1rem;
    background-color: rgba(var(--primary-color-rgb), 0.1);
    border: 1px solid var(--primary-color);
    border-radius: 10px;
    margin-bottom: 1rem;
}
.winner-card h4, .winner-card p {
    color: var(--text-color) !important;
}
.stButton button {
    width: 100%;
}
.round-header {
    background-color: var(--primary-color);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

def mask_email(email):
    """Mask email to protect privacy (e.g., j***e@d***n.com)"""
    if not email or '@' not in email:
        return email

    local_part, domain_part = email.split('@')

    # Handle the local part (username)
    if len(local_part) > 2:
        masked_local = local_part[0] + '*' * (len(local_part) - 2) + local_part[-1]
    else:
        masked_local = local_part[0] + '*' * (len(local_part) - 1) if len(local_part) > 0 else ''

    # Handle the domain part
    domain_name, *ext_parts = domain_part.split('.')
    domain_ext = '.'.join(ext_parts)

    if len(domain_name) > 1:
        masked_domain = domain_name[0] + '*' * (len(domain_name) - 1)
    else:
        masked_domain = domain_name

    return f"{masked_local}@{masked_domain}.{domain_ext}"

# Inicializar servicios
ui = UIComponents()
state_manager = SessionStateManager()
csv_repo = CSVRepository()
participant_service = ParticipantService(csv_repo)
session_service = SessionService()
draw_service = DrawService()

# Inicializar el estado de la sesión si no existe
state_manager.initialize_session_state()

# Sidebar para configuración
with st.sidebar:
    st.title("🎲 Configuración del Sorteo")
    
    # File upload section
    st.subheader("Subir lista de participantes")
    uploaded_file = st.file_uploader("Subir CSV con los datos de los participantes", type=['csv'])
    
    only_checkin = st.checkbox("Solo participantes con check-in", value=True)
    
    # Privacy settings
    st.subheader("Configuración de privacidad")
    pii_mode = st.radio(
        "Modo de manejo de datos personales",
        [
            CSVRepository.PII_MODE_ORIGINAL,
            CSVRepository.PII_MODE_MASKED,
            CSVRepository.PII_MODE_PSEUDONYMIZED
        ],
        format_func=lambda x: {
            CSVRepository.PII_MODE_ORIGINAL: "Original (sin protección)",
            CSVRepository.PII_MODE_MASKED: "Enmascarado (protección básica)",
            CSVRepository.PII_MODE_PSEUDONYMIZED: "Pseudonimizado (protección avanzada)"
        }.get(x)
    )
    
    # Update PII mode if changed
    if st.session_state.pii_mode != pii_mode:
        st.session_state.pii_mode = pii_mode
        st.experimental_rerun()
    
    if uploaded_file is not None:
        if st.button("Procesar lista de participantes"):
            participants = participant_service.process_csv(uploaded_file, only_checkin)
            if participants is not None:
                state_manager.set_participants(participants)
                st.success(f"Se han cargado {len(participants)} participantes válidos")
        
        # GDPR compliance check
        if st.button("Verificar cumplimiento GDPR"):
            try:
                # Save the uploaded file temporarily
                temp_file = "temp_upload.csv"
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Check GDPR compliance
                report = check_gdpr_compliance(temp_file)
                
                # Display report
                if report['compliant']:
                    st.success("El archivo parece cumplir con GDPR")
                else:
                    st.warning("El archivo tiene problemas de cumplimiento GDPR:")
                    for issue in report['issues']:
                        st.warning(f"- {issue}")
                
                if report['recommendations']:
                    st.info("Recomendaciones:")
                    for rec in report['recommendations']:
                        st.info(f"- {rec}")
                
                # Remove temp file
                os.remove(temp_file)
            except Exception as e:
                st.error(f"Error al verificar el cumplimiento GDPR: {e}")
    
    # Round management section
    st.subheader("Gestión de rondas")
    if st.button("Añadir ronda de sorteo"):
        session_service.add_round()

    # Reset button at the bottom
    if st.button("Reiniciar sesión de sorteo"):
        state_manager.reset_session()
        st.success("Sesión reiniciada correctamente")
    
    # Session info
    st.subheader("Información de sesión")
    session_info = state_manager.get_session_info()
    st.text(f"ID de sesión: {session_info['session_id'][:8]}")
    st.text(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if session_info['participants'] is not None:
        st.text(f"Participantes: {session_info['total_participants']}")
    st.text(f"Ganadores totales: {session_info['total_winners']}")
    st.text(f"Modo PII: {st.session_state.pii_mode}")

# Main content area
st.title("🎉 Sorteo de Eventos")

# Welcome message if no file is uploaded yet
if state_manager.get_participants() is None:
    ui.show_welcome_message()
    
    with st.expander("Formato de archivo esperado"):
        st.write("""
        El archivo CSV debe contener al menos las siguientes columnas:
        - 'Checkin Date (UTC)' o 'checked_in_at': Fecha de check-in del participante
        - 'Email' o 'email': Correo electrónico del participante
        - 'First Name' o 'first_name': Nombre del participante
        - 'Last Name' o 'last_name': Apellido del participante
        """)
else:
    # Show participants summary
    with st.expander("Resumen de Participantes"):
        ui.show_participants_summary(state_manager.get_participants())
    
    # Display and configure rounds
    rounds = state_manager.get_rounds()
    if not rounds:
        st.warning("No hay rondas configuradas. Añade al menos una ronda para realizar el sorteo.")
    
    for i, round_config in enumerate(rounds):
        ui.render_round_section(
            i, 
            round_config, 
            state_manager, 
            session_service,
            draw_service
        )
    
    # Summary of all winners
    ui.render_winners_summary(state_manager)
