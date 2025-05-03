#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import csv
import io
import uuid
from datetime import datetime

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

# Set page configuration
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
.winner-card.absent {
    background-color: rgba(255, 0, 0, 0.1);
    border: 1px solid #ff0000;
    opacity: 0.7;
}
.absent-label {
    color: #ff0000;
    font-weight: bold;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state if not exists
if 'participants' not in st.session_state:
    st.session_state.participants = None
if 'all_winners' not in st.session_state:
    st.session_state.all_winners = []  # List to store all winners across rounds
if 'rounds' not in st.session_state:
    st.session_state.rounds = []  # List to store round configurations
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'drawn_winners' not in st.session_state:
    st.session_state.drawn_winners = {}  # Dictionary to store winners by round
if 'absent_participants' not in st.session_state:
    st.session_state.absent_participants = []  # List to store absent participants' emails

def reset_session():
    """Reset the session completely"""
    st.session_state.participants = None
    st.session_state.all_winners = []
    st.session_state.rounds = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.drawn_winners = {}
    st.session_state.absent_participants = []

def process_csv(uploaded_file, only_checkin=True):
    """Process uploaded CSV file and filter participants"""
    try:
        # Try to read the CSV file
        content = uploaded_file.getvalue().decode('utf-8')
        participants_df = pd.read_csv(io.StringIO(content))

        # Check for required columns
        expected_columns = [
            ('Checkin Date (UTC)', 'checked_in_at'),
            ('Email', 'email'),
            ('First Name', 'first_name'),
            ('Last Name', 'last_name')
        ]

        # Map actual column names to standardized names
        column_mapping = {}
        for expected_pair in expected_columns:
            found = False
            for expected in expected_pair:
                if expected in participants_df.columns:
                    column_mapping[expected] = expected_pair[0]
                    found = True
                    break
            if not found:
                st.error(f"No se encontró ninguna columna del tipo {expected_pair}")
                return None

        # Rename columns to standardized names
        participants_df = participants_df.rename(columns=column_mapping)

        # Filter participants based on check-in status
        if only_checkin:
            participants_df = participants_df[participants_df['Checkin Date (UTC)'].notna() &
                                             (participants_df['Checkin Date (UTC)'] != '')]

        # Filter out specific email domains if needed
        participants_df = participants_df[~participants_df['Email'].str.contains('bevylabs', case=False, na=False)]

        return participants_df
    except Exception as e:
        st.error(f"Error al procesar el archivo CSV: {e}")
        return None

def draw_winners(participants_df, num_winners, exclude_emails=None):
    """Draw winners from participants"""
    if exclude_emails is None:
        exclude_emails = []

    # Combine previous winners and absent participants to exclude from drawing
    all_excluded_emails = list(set(exclude_emails + st.session_state.absent_participants))

    # Filter out previous winners and absent participants
    available_participants = participants_df[~participants_df['Email'].isin(all_excluded_emails)]

    if len(available_participants) < num_winners:
        st.error(f"No hay suficientes participantes disponibles. Solicitados: {num_winners}, Disponibles: {len(available_participants)}")
        return []

    # Select winners randomly
    winners = available_participants.sample(n=num_winners)
    return winners.to_dict('records')

def add_round():
    """Add a new round configuration"""
    st.session_state.rounds.append({
        'id': len(st.session_state.rounds) + 1,
        'name': f"Ronda {len(st.session_state.rounds) + 1}",
        'num_winners': 1,
        'prizes': []
    })

def add_prize(round_idx):
    """Add a new prize to a specific round"""
    st.session_state.rounds[round_idx]['prizes'].append({
        'id': len(st.session_state.rounds[round_idx]['prizes']) + 1,
        'name': '',
        'description': '',
    })

def delete_round(round_idx):
    """Delete a round and its associated winners"""
    round_id = st.session_state.rounds[round_idx]['id']
    if round_id in st.session_state.drawn_winners:
        # Get emails of winners from this round
        winner_emails = [w['Email'] for w in st.session_state.drawn_winners[round_id]]
        # Remove these winners from the all_winners list
        st.session_state.all_winners = [
            email for email in st.session_state.all_winners
            if email not in winner_emails
        ]
        # Remove the round from drawn_winners
        del st.session_state.drawn_winners[round_id]

    # Remove the round configuration
    st.session_state.rounds.pop(round_idx)

def mark_winner_absent(round_id, winner_index):
    """Mark a winner as absent and redraw a replacement"""
    if round_id not in st.session_state.drawn_winners:
        return

    winners = st.session_state.drawn_winners[round_id]
    if winner_index >= len(winners):
        return

    # Get the winner to mark as absent
    absent_winner = winners[winner_index]

    # Check if the winner doesn't have the absent flag yet
    if 'absent' not in absent_winner or not absent_winner['absent']:
        # Mark as absent
        absent_winner['absent'] = True

        # Add to absent participants list if not already there
        if absent_winner['Email'] not in st.session_state.absent_participants:
            st.session_state.absent_participants.append(absent_winner['Email'])

        # Find the corresponding round configuration
        round_config = next((r for r in st.session_state.rounds if r['id'] == round_id), None)
        if round_config:
            # Try to draw a replacement winner
            replacement = draw_winners(
                st.session_state.participants,
                1,
                exclude_emails=st.session_state.all_winners
            )

            if replacement:
                replacement_winner = replacement[0]
                # Add a flag to identify it as a replacement
                replacement_winner['is_replacement'] = True
                # Store reference to the original absent winner
                replacement_winner['replaced'] = absent_winner['Email']

                # Add to global winners list
                st.session_state.all_winners.append(replacement_winner['Email'])

                # Add to the winners list for this round
                winners.append(replacement_winner)

                return True
            else:
                st.warning("No hay participantes disponibles para reemplazar al ganador ausente.")
                return False
    return False

# Sidebar for configuration
with st.sidebar:
    st.title("🎲 Configuración del Sorteo")

    # File upload section
    st.subheader("Subir lista de participantes")
    uploaded_file = st.file_uploader("Subir CSV con los datos de los participantes", type=['csv'])

    only_checkin = st.checkbox("Solo participantes con check-in", value=True)

    if uploaded_file is not None:
        if st.button("Procesar lista de participantes"):
            participants_df = process_csv(uploaded_file, only_checkin)
            if participants_df is not None:
                st.session_state.participants = participants_df
                st.success(f"Se han cargado {len(participants_df)} participantes válidos")

    # Round management section
    st.subheader("Gestión de rondas")
    if st.button("Añadir ronda de sorteo"):
        add_round()

    # Reset button at the bottom
    if st.button("Reiniciar sesión de sorteo"):
        reset_session()
        st.success("Sesión reiniciada correctamente")

    # Session info
    st.subheader("Información de sesión")
    st.text(f"ID de sesión: {st.session_state.session_id[:8]}")
    st.text(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if st.session_state.participants is not None:
        st.text(f"Participantes: {len(st.session_state.participants)}")

    # Count different types of winners
    total_winners = len(st.session_state.all_winners)

    # Calculate number of absent winners (those marked as absent)
    absent_winners = len(st.session_state.absent_participants)

    # Calculate final winners (total winners excluding absent ones)
    final_winners = total_winners - absent_winners

    # Display winner statistics with clearer differentiation
    st.markdown("**Estadísticas de Ganadores**")
    st.text(f"Total de ganadores sorteados: {total_winners}")
    st.text(f"Ganadores ausentes: {absent_winners}")
    st.text(f"Receptores finales de premios: {final_winners}")

# Main content area
st.title("🎉 Sorteo de Eventos")

# Welcome message if no file is uploaded yet
if st.session_state.participants is None:
    st.info("Sube un archivo CSV con la lista de participantes para comenzar")

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
        # Create a display dataframe with masked emails
        display_df = st.session_state.participants.copy()
        display_df['Email'] = display_df['Email'].apply(mask_email)
        st.dataframe(display_df[['First Name', 'Last Name', 'Email', 'Checkin Date (UTC)']])

    # Display and configure rounds
    if not st.session_state.rounds:
        st.warning("No hay rondas configuradas. Añade al menos una ronda para realizar el sorteo.")

    for i, round_config in enumerate(st.session_state.rounds):
        round_id = round_config['id']
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### Ronda {i+1}: {round_config['name']}")

        with col2:
            st.button("Eliminar ronda", key=f"del_round_{i}", on_click=delete_round, args=(i,))

        # Round configuration
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.rounds[i]['name'] = st.text_input("Nombre de la ronda",
                                                               value=round_config['name'],
                                                               key=f"round_name_{i}")
        with col2:
            st.session_state.rounds[i]['num_winners'] = st.number_input("Número de ganadores",
                                                                        min_value=1, value=round_config['num_winners'],
                                                                        key=f"num_winners_{i}")

        # Prize configuration
        st.subheader("Premios")

        if not round_config['prizes']:
            st.button("Añadir premio", key=f"add_prize_{i}", on_click=add_prize, args=(i,))

        for j, prize in enumerate(round_config['prizes']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"##### Premio {j+1}")
            with col2:
                if st.button("Eliminar", key=f"del_prize_{i}_{j}"):
                    st.session_state.rounds[i]['prizes'].pop(j)
                    st.experimental_rerun()

            col1, col2 = st.columns(2)
            with col1:
                st.session_state.rounds[i]['prizes'][j]['name'] = st.text_input(
                    "Nombre del premio", value=prize['name'], key=f"prize_name_{i}_{j}")
            with col2:
                st.session_state.rounds[i]['prizes'][j]['description'] = st.text_input(
                    "Descripción", value=prize['description'], key=f"prize_desc_{i}_{j}")

        if round_config['prizes']:
            st.button("Añadir otro premio", key=f"add_another_prize_{i}", on_click=add_prize, args=(i,))

        # Draw winners button
        if st.button("Sortear ganadores", key=f"draw_{i}"):
            if st.session_state.participants is None:
                st.error("Debes cargar un archivo de participantes primero")
            else:
                num_winners = int(round_config['num_winners'])
                winners = draw_winners(
                    st.session_state.participants,
                    num_winners,
                    exclude_emails=st.session_state.all_winners
                )

                if winners:
                    # Store winners by round
                    st.session_state.drawn_winners[round_id] = winners

                    # Add winner emails to the global list
                    for winner in winners:
                        st.session_state.all_winners.append(winner['Email'])

                    st.success(f"Se han sorteado {len(winners)} ganadores")
                    st.experimental_rerun()

        # Display winners for this round
        if round_id in st.session_state.drawn_winners and st.session_state.drawn_winners[round_id]:
            st.subheader("Ganadores de esta ronda")

            winners = st.session_state.drawn_winners[round_id]
            replacements = [w for w in winners if w.get('is_replacement')]
            original_winners = [w for w in winners if not w.get('is_replacement')]

            # Display original winners first, then replacements
            all_display_winners = original_winners + replacements
            cols = st.columns(min(3, len(all_display_winners)))

            for j, winner in enumerate(all_display_winners):
                with cols[j % len(cols)]:
                    # Determine CSS class based on absent status
                    card_class = "winner-card absent" if winner.get('absent') else "winner-card"

                    # Build winner card HTML
                    card_html = f"""
                    <div class="{card_class}">
                        <h4>{winner['First Name']} {winner['Last Name']}</h4>
                        <p>{mask_email(winner['Email'])}</p>
                    """

                    # Add absent label if applicable
                    if winner.get('absent'):
                        card_html += '<p class="absent-label">Ausente</p>'

                    # Add replacement info if applicable
                    if winner.get('is_replacement'):
                        replaced_email = winner.get('replaced', '')
                        card_html += f'<p><small>Reemplazo para: {mask_email(replaced_email)}</small></p>'

                    # Close the div
                    card_html += '</div>'

                    # Render the card
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Assign prize if available and not a replacement
                    prize_index = original_winners.index(winner) if winner in original_winners else -1
                    if prize_index >= 0 and prize_index < len(round_config['prizes']):
                        prize = round_config['prizes'][prize_index]
                        st.info(f"Premio: {prize['name']}")

                    # Mark as absent button (show for any non-absent winner, including replacements)
                    if not winner.get('absent'):
                        if st.button("Marcar como ausente", key=f"mark_absent_{round_id}_{j}"):
                            if mark_winner_absent(round_id, winners.index(winner)):
                                st.experimental_rerun()

        st.markdown("---")

    # Summary of all winners
    if any(st.session_state.drawn_winners.values()):
        st.header("Resumen de todos los ganadores")

        all_winners_data = []
        for round_id, winners in st.session_state.drawn_winners.items():
            round_name = next((r['name'] for r in st.session_state.rounds if r['id'] == round_id), f"Ronda {round_id}")

            for i, winner in enumerate(winners):
                winner_data = {
                    'Ronda': round_name,
                    'Nombre': f"{winner['First Name']} {winner['Last Name']}",
                    'Email': mask_email(winner['Email']),
                    'Estado': 'Ausente' if winner.get('absent') else 'Presente',
                    'Tipo': 'Reemplazo' if winner.get('is_replacement') else 'Original'
                }

                # Add replacement info if applicable
                if winner.get('is_replacement') and winner.get('replaced'):
                    winner_data['Reemplazo para'] = mask_email(winner.get('replaced'))
                else:
                    winner_data['Reemplazo para'] = '-'

                # Add prize info if available
                round_config = next((r for r in st.session_state.rounds if r['id'] == round_id), None)
                if round_config:
                    # For replacements, find the prize of the original winner they replaced
                    if winner.get('is_replacement') and winner.get('replaced'):
                        # Find the original winner this replaced
                        original_winners = [w for w in winners if not w.get('is_replacement')]
                        for idx, orig_winner in enumerate(original_winners):
                            if orig_winner.get('Email') == winner.get('replaced') and idx < len(round_config['prizes']):
                                winner_data['Premio'] = round_config['prizes'][idx]['name']
                                break
                        else:
                            winner_data['Premio'] = '-'
                    # For original winners (not replacements)
                    elif not winner.get('is_replacement'):
                        original_winners = [w for w in winners if not w.get('is_replacement')]
                        idx = original_winners.index(winner) if winner in original_winners else -1
                        if idx >= 0 and idx < len(round_config['prizes']):
                            winner_data['Premio'] = round_config['prizes'][idx]['name']
                        else:
                            winner_data['Premio'] = '-'
                    else:
                        winner_data['Premio'] = '-'
                else:
                    winner_data['Premio'] = '-'

                all_winners_data.append(winner_data)

        if all_winners_data:
            winners_df = pd.DataFrame(all_winners_data)
            st.dataframe(winners_df)

            # Export winners to CSV
            csv = winners_df.to_csv(index=False)
            st.download_button(
                label="Descargar resultados en CSV",
                data=csv,
                file_name=f"ganadores_{st.session_state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )