#!/usr/bin/env python3

"""
Main Streamlit application for the GH Spain Raffles.
"""
from datetime import datetime

import streamlit as st

from application.participant_service import ParticipantService
from application.session_service import SessionService
from application.raffle_service import RaffleService
from infrastructure.csv_repository import CsvRepository
from presentation.session_state_manager import SessionStateManager

# Initialize session state using the manager (following SRP and DDD)
session_manager = SessionStateManager()
session_manager.initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="GH Spain Raffle App",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize services with proper dependency injection
participant_service = ParticipantService(CsvRepository(session_manager.get_pii_mode()))
session_service = SessionService()
raffle_service = RaffleService(session_service)

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

# Sidebar for configuration
with st.sidebar:
    st.title("🎲 Raffle Configuration")

    # File upload section
    st.subheader("Upload Participant List")
    uploaded_file = st.file_uploader("Upload CSV with participant data", type=['csv'])

    only_check_in = st.checkbox("Only participants with check-in", value=True)

    # Privacy settings
    st.subheader("Privacy Settings")
    pii_mode = st.radio(
        "Personal Data Handling Mode",
        [
            CsvRepository.PII_MODE_ORIGINAL,
            CsvRepository.PII_MODE_MASKED,
            CsvRepository.PII_MODE_PSEUDONYMIZED
        ],
        format_func=lambda x: {
            CsvRepository.PII_MODE_ORIGINAL: "Original (no protection)",
            CsvRepository.PII_MODE_MASKED: "Masked (basic protection)",
            CsvRepository.PII_MODE_PSEUDONYMIZED: "Pseudonymized (advanced protection)"
        }.get(x)
    )

    # Update PII mode if changed
    if session_manager.get_pii_mode() != pii_mode:
        session_manager.set_pii_mode(pii_mode)
        st.experimental_rerun()

    if uploaded_file is not None:
        if st.button("Process Participant List"):
            participants = participant_service.process_participants_file(uploaded_file.getvalue(), only_checked_in=only_check_in)
            if participants is not None:
                session_manager.set_participants(participants)
                st.success(f"{len(participants)} valid participants have been loaded")

        # Display column mapping information for clarity
        with st.expander("Column Mapping Information"):
            st.write("""
            The application handles various column naming formats:
            - Check-in timestamps: 'Check-in Date (UTC)', 'checked_in_at', 'checkin_date', or 'checkin_time'
            - Email: 'Email', 'email', 'email_address' or 'mail'
            - First name: 'First Name', 'first_name', 'firstname', or 'name'
            - Last name: 'Last Name', 'last_name', 'lastname', or 'surname'

            All formats are normalized internally for consistent processing.
            """)

        # GDPR compliance check
        if st.button("Check GDPR Compliance"):
            try:
                # Use the more secure method that handles temporary files properly
                report = CsvRepository.check_gdpr_compliance_from_bytes(uploaded_file.getvalue())

                # Display report
                if report['compliant']:
                    st.success("The file appears to comply with GDPR")
                else:
                    issues = ""
                    for issue in report['issues']:
                        issues += f"- {issue}\n"
                    st.warning("The file has GDPR compliance issues:" + "\n" + issues, icon="⚠️")

                if report['recommendations']:
                    recommendations = ""
                    for rec in report['recommendations']:
                        recommendations += f"- {rec}\n"
                    st.info("Recommendations:" + "\n" + recommendations, icon="ℹ️")
            except Exception as e:
                st.error(f"Error checking GDPR compliance: {e}")

    # Round management section
    st.subheader("Round Management")
    if st.button("Add Raffle Round"):
        raffle_service.add_round()

    # Reset button at the bottom
    if st.button("Reset Raffle Session"):
        session_manager.reset_session()
        st.success("Raffle session successfully reset")

    # Session info
    st.subheader("Session Information")
    session_info = {
        "session_id": session_manager.get_session_id(),
        "total_participants": len(session_manager.get_participants()),
        "total_winners": len(raffle_service.get_all_winners()),
        "pii_mode": session_manager.get_pii_mode()
    }
    st.text(f"Session ID: {session_info['session_id'][:8]}")
    st.text(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.text(f"Participants: {session_info['total_participants']}")
    st.text(f"Total Winners: {session_info['total_winners']}")
    st.text(f"PII Mode: {session_info['pii_mode']}")

# Main content area
st.title("🎉 GH Spain Raffle App")

# Welcome message if no file is uploaded yet
if not session_manager.get_participants():
    st.write("Welcome to the GH Spain Raffle App! Please upload a participant list to get started.")

    with st.expander("Expected File Format"):
        st.write("""
        The CSV file must contain at least the following columns:
        - 'Check-in Date (UTC)' or 'checked_in_at': Participant check-in date
        - 'Email' or 'email': Participant email address
        - 'First Name' or 'first_name': Participant first name
        - 'Last Name' or 'last_name': Participant last name
        """)
else:
    # Show participants summary
    with st.expander("Participant Summary"):
        st.write(f"Total Participants: {len(session_manager.get_participants())}")

    # Display and configure rounds
    rounds = session_manager.get_rounds()
    if not rounds:
        st.warning("No rounds configured. Add at least one round to proceed with the raffle.")

    for i, round_config in enumerate(rounds):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Round {i + 1}: {round_config.get('name', 'Prize Round')}")

        # Display existing winners for this round if any
        round_winners = raffle_service.get_winners_for_round(round_config['id'])
        if round_winners:
            st.write(f"Winners for Round {i + 1}:")
            for winner in round_winners:
                st.write(f"- {winner.get('First Name', '')} {winner.get('Last Name', '')} ({winner.get('Email', '')})")
        else:
            # Only show draw button if there are no winners yet
            with col2:
                if st.button(f"Draw Winner(s) for Round {i + 1}"):
                    winners = raffle_service.select_winners(
                        round_config['id'],
                        session_manager.get_participants(),
                        round_config.get('num_winners', 1)
                    )
                    if winners:
                        st.success(f"Selected {len(winners)} winners!")
                    else:
                        st.error("No winners could be selected. Check participant list.")

    # Summary of all winners
    st.subheader("Winners Summary:")
    winners = raffle_service.get_all_winners()
    if winners:
        for winner in winners:
            st.write(f"- {winner.get('First Name', '')} {winner.get('Last Name', '')} ({winner.get('Email', '')})")
    else:
        st.write("No winners yet. Draw winners from the rounds above to see them here.")
