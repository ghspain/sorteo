# Getting Started

## Requirements

- Python 3.10 or higher
- Dependencies from `requirements.txt`

## Run the Application Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The application is available at `http://localhost:8501`.

## Build and Preview the Documentation Locally

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

The documentation site is available at `http://127.0.0.1:8000`.

## Docker Compose

The repository includes a `docs` profile for local documentation preview:

```bash
docker-compose --profile docs up docs
```
