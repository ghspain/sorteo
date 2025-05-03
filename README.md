# Event Raffle Application

This web application allows managing raffles at events, providing a system to:

- Load a participant list from a CSV file
- Create multiple raffle rounds
- Define different prizes per round
- Perform random draws ensuring unique winners throughout the event
- Export results

## Features

- Intuitive user interface built with Streamlit
- Support for CSV files with different column formats
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

## CSV File Format

The CSV file must contain at least the following columns:

- `Checkin Date (UTC)` or `checked_in_at`: Check-in date
- `Email` or `email`: Participant's email
- `First Name` or `first_name`: Participant's first name
- `Last Name` or `last_name`: Participant's last name

## License

This project is licensed under the [MIT License](LICENSE).
