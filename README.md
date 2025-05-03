# Event Raffle Application

This web application allows managing raffles at events, providing a system to:

- Load a participant list from a CSV file
- Create multiple raffle rounds
- Define different prizes per round
- Perform random draws ensuring unique winners throughout the event
- Export results

This web application allows you to manage raffles for events, providing a system to:

- Upload a list of participants from a CSV file
- Create multiple raffle rounds
- Define different prizes per round
- Perform random draws ensuring unique winners throughout the event
- Export the results

## Features

- Intuitive user interface built with Streamlit
- Support for CSV files with different column formats

- Filtering of participants by check-in status
- Configuration of multiple rounds with variable number of winners
- Prize management system
- Guarantee that no participant wins more than one prize throughout the raffle
- Export results to CSV
- Internationalization support (English and Spanish)
- Structured logging for debugging and monitoring
- Clean Architecture design following SOLID principles

- Filter participants by check-in status
- Configuration of multiple rounds with variable number of winners
- Prize management system
- Guarantee that no participant wins more than one prize
- Results export

## Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`

## How to run

### python

1. Virtual environment setup (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

3. Run the app

    ```bash
    streamlit run app.py
    ```

4. Open your browser and go to `http://localhost:8501`

### Docker

1. Build the Docker image

    ```bash
    docker build -t sorteo-app .
    ```

2. Run the Docker container

    ```bash
    docker run -p 8501:8501 sorteo-app
    ```

3. Open your browser and go to `http://localhost:8501`

### Docker Compose

1. Start the application using Docker Compose

    ```bash
    docker-compose up
    ```

2. Open your browser and go to `http://localhost:8501`

## Usage

Options for using the application:

- **Web Interface**: Use the web interface for a user-friendly experience.
- **Command Line Interface (CLI)**: Use the command line for quick operations or automation.

### cli

NOTE:

- `-f` or `--file`: Path to the CSV file with participant data
- `-w` or `--winners`: Number of winners to draw
- `-c` or `--checked-in`: Use only checked-in participants
- `-p` or `--prize`: Prize name for the round
- `-r` or `--round`: Round name for the draw
- `-h` or `--help`: Show help message and exit

Steps:

1. **Download the participant list**:

   - Access the [GDG Bevy](https://gdg.community.dev/) or [Luma](https://lu.ma/) Platform and download the participant list to your event in CSV.

2. **Run the script**:

    - Make sure you have Python 3.7 or higher installed
    - Install the required dependencies using `pip install -r requirements.txt`
    - Make sure the script is executable by running `chmod +x sorteo.py`
    - Run the script with the command `python sorteo.py -f <event-participant-list>.csv -w <number-of-winners>`

### web

1. **Download the participant list**:

   - Access the [GDG Bevy](https://gdg.community.dev/) or [Luma](https://lu.ma/) Platform and download the participant list to your event in CSV.

2. **Upload participant list**:

   - Upload a CSV file with participant data
   - Optionally filter by checked-in participants

3. **Round configuration**:

   - Add one or more raffle rounds
   - Configure name and number of winners for each round
   - Add prizes to be raffled in each round

4. **Conduct raffles**:
   - Use the "Draw winners" button in each round
   - View winners immediately
   - Export results when finished

## Architecture

The application is built following Clean Architecture principles:

- **Domain Layer**: Core business entities and rules
- **Application Layer**: Use cases and business logic
- **Infrastructure Layer**: External services and data access
- **Presentation Layer**: User interface and state management

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## Local Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/sorteo.git
cd sorteo
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run app.py
```

4. Open the application in your browser (typically at <http://localhost:8501>)

## Running with Docker

### Option 1: Using Docker Compose (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system

2. Run the application with:

```bash
docker-compose up
```

3. To run in the background:

```bash
docker-compose up -d
```

4. To stop the application:

```bash
docker-compose down
```

### Option 2: Using Docker directly

1. Build the image:

```bash
docker build -t sorteo-app .
```

2. Run the container:

```bash
docker run -p 8501:8501 sorteo-app
```

3. Access the application at <http://localhost:8501>

## Running Tests

You can run tests using either Docker Compose or pytest directly:

### Using Docker Compose

```bash
docker-compose run test
```

### Using pytest directly

```bash
pytest
```

## Usage

1. **Upload participant list**:
   - Upload a CSV file with participant data
   - Optionally filter by participants with check-in

2. **Round configuration**:
   - Add one or more raffle rounds
   - Configure the name and number of winners for each round
   - Add the prizes to be raffled in each round

3. **Perform raffles**:
    - Use the "Draw winners" button in each round
    - View winners immediately
    - Export results when finished

## CSV File Format

The CSV file must contain at least the following columns:

- `Checkin Date (UTC)` or `checked_in_at`: Check-in date
- `Email` or `email`: Participant's email
- `First Name` or `first_name`: Participant's first name
- `Last Name` or `last_name`: Participant's last name

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Project Structure

```
app.py                        # Main entry point
application/                  # Application layer (use cases)
  draw_service.py             # Service for draw operations
  participant_service.py      # Service for participant operations
  session_service.py          # Service for session management
domain/                       # Domain layer (entities and rules)
  models.py                   # Domain models
infrastructure/               # Infrastructure layer (external interfaces)
  csv_repository.py           # CSV data access
  i18n_service.py             # Internationalization service
  logging_service.py          # Logging service
presentation/                 # Presentation layer (UI)
  session_state_manager.py    # Streamlit session state management
  ui_components.py            # UI components
tests/                        # Test suite
  e2e/                        # End-to-end tests
  integration/                # Integration tests
  unit/                       # Unit tests
translations/                 # Translation files
  en/                         # English translations
  es/                         # Spanish translations
```

## License

This project is licensed under the [MIT License](LICENSE).
