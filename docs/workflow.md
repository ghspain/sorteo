# Raffle Workflow

## Participant Import

1. Export the attendee list from the event platform.
2. Upload the CSV file in the Streamlit application.
3. Optionally restrict the participant pool to checked-in attendees.

The CSV import normalizes accepted column names and filters blacklisted domains used only for dummy data.

## Round Execution

1. Create one or more rounds.
2. Define the number of winners.
3. Add prizes for each round.
4. Draw winners from the eligible participants.

The application tracks previous winners across the session to avoid duplicate prizes.

## Absent Winner Handling

If a winner is no longer present:

1. Mark that winner as absent from the winner card.
2. The session stores the participant in the absent list.
3. The application redraws a replacement from the remaining eligible participants.
4. Future rounds exclude both previous winners and absent participants.

The CSV export preserves the winner status, replacement type, and the original recipient reference.
