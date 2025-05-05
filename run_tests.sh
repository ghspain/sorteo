#!/bin/bash
# Script to run tests in a virtual environment

# Exit on any error
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Display header
echo -e "${GREEN}=== Raffle Application Test Runner ===${NC}\n"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Install Playwright browsers (using direct command instead of Python check)
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
python -m playwright install chromium

# Run unit and integration tests
echo -e "\n${GREEN}Running unit and integration tests...${NC}"
pytest tests/unit/ tests/integration/ -v

# Check if the user wants to run e2e tests
echo -e "\n${YELLOW}Do you want to run end-to-end tests? (requires Streamlit app running) [y/N]${NC}"
read -r run_e2e

if [[ $run_e2e =~ ^[Yy]$ ]]; then
    # Check if Streamlit app is running
    echo -e "${YELLOW}Checking if Streamlit app is running...${NC}"
    if ! curl -s http://localhost:8501 &> /dev/null; then
        echo -e "${RED}Warning: Streamlit app doesn't seem to be running at http://localhost:8501${NC}"
        echo -e "${YELLOW}Do you want to start the Streamlit app? [y/N]${NC}"
        read -r start_app
        
        if [[ $start_app =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Starting Streamlit app in background...${NC}"
            make run
            started=true
            sleep 5
        else
            echo -e "${RED}Skipping e2e tests${NC}"
            exit 0
        fi
    else
        echo -e "${GREEN}Streamlit app is already running!${NC}"
    fi
    
    # Run e2e tests
    echo -e "\n${GREEN}Running end-to-end tests...${NC}"
    pytest tests/e2e/ -v
    
    # Kill Streamlit app if we started it
    if [ "$started" = true ]; then
        echo -e "${YELLOW}Stopping Streamlit app...${NC}"
        make stop
        sleep 2
    fi
fi

# Deactivate virtual environment
deactivate

echo -e "\n${GREEN}Tests completed!${NC}"