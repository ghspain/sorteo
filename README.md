# Event Raffle Application

Streamlit application for running event raffles from attendee CSV exports.

## Features

- Import participants from CSV files with supported column aliases.
- Optionally restrict the draw to checked-in attendees.
- Configure multiple raffle rounds and prizes.
- Prevent duplicate winners across the full session.
- Mark a drawn winner as absent and automatically redraw a replacement when possible.
- Exclude absent winners from future rounds.
- Export raffle results to CSV with round, prize, status, and replacement information.
- Run locally with Python or Docker.

## Requirements

- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

## Run Locally

1. Create and activate a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Start the application.

```bash
streamlit run app.py
```

4. Open `http://localhost:8501`.

## Run With Docker

Build and run the container directly:

```bash
docker build -t sorteo-app .
docker run -p 8501:8501 sorteo-app
```

Or use Docker Compose:

```bash
docker-compose up
```

## Documentation

Project documentation is published through GitHub Pages at `https://ghspain.github.io/sorteo/`.

To preview the docs locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

## Raffle Workflow

1. Upload an attendee CSV export.
2. Choose whether to limit the draw to checked-in participants.
3. Create one or more rounds and add prizes.
4. Draw winners for each round.
5. If a winner is no longer present, use the absent action on the winner card.
6. The application marks that winner as absent, keeps the prize assignment, and redraws a replacement from the remaining eligible participants.
7. Export the final winners CSV when the session is complete.

## Testing

Fast local verification used for this stabilization:

```bash
python -m pytest tests/unit tests/integration -q
```

End-to-end tests require a running Streamlit server on port `8501`:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
STREAMLIT_HOST=127.0.0.1 STREAMLIT_PORT=8501 python -m pytest tests/e2e/test_csv_upload.py tests/e2e/test_raffle_process.py -q
```

## Architecture

The project follows a layered structure:

- `presentation/`: Streamlit UI and session state helpers
- `application/`: orchestration and raffle/session services
- `domain/`: domain models and value objects
- `infrastructure/`: CSV parsing, logging, and error handling

## Notes

- Test fixtures should avoid blacklisted email domains such as `example.com` and `test.com`, because the CSV import intentionally filters them out.
