#!/bin/bash
# Script to run tests in Docker for consistent environments

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Display header
echo -e "${GREEN}=== Raffle Application Docker Test Runner ===${NC}\n"

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is required but not found${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is required but not found${NC}"
    exit 1
fi

# Build the test image
echo -e "${YELLOW}Building test Docker image...${NC}"
docker-compose build test

# Run unit and integration tests
echo -e "\n${GREEN}Running unit and integration tests in Docker...${NC}"
docker-compose run --rm test -- pytest tests/unit/ tests/integration/ -v

# Check if the user wants to run e2e tests
echo -e "\n${YELLOW}Do you want to run end-to-end tests in Docker? [y/N]${NC}"
read -r run_e2e

if [[ $run_e2e =~ ^[Yy]$ ]]; then
    # Ensure the app is running in Docker
    echo -e "${YELLOW}Starting Streamlit app in Docker...${NC}"
    docker-compose up -d app
    
    # Wait for the app to start and be healthy
    echo -e "${YELLOW}Waiting for app to start and be healthy...${NC}"
    
    # Function to check if the app is accessible
    check_app_health() {
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            echo -n "."
            
            # Use Docker's health check first if available
            HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $(docker-compose ps -q app) 2>/dev/null || echo "unknown")
            
            if [ "$HEALTH" = "healthy" ]; then
                echo -e "\n${GREEN}✅ App container is healthy!${NC}"
                return 0
            fi
            
            # Try a direct HTTP request as fallback
            if docker-compose exec -T app curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
                echo -e "\n${GREEN}✅ App is responding to HTTP requests!${NC}"
                return 0
            fi
            
            # Test direct network connectivity between test and app containers
            if docker-compose run --rm test -- python -c "import socket; s=socket.socket(); result=s.connect_ex(('app', 8501)); s.close(); exit(0 if result == 0 else 1)" &>/dev/null; then
                echo -e "\n${GREEN}✅ Network connectivity verified between test and app containers!${NC}"
                # Give a little more time for app to fully initialize
                sleep 3
                return 0
            fi
            
            attempt=$((attempt + 1))
            sleep 2
        done
        
        echo -e "\n${RED}❌ App did not become healthy after $(( max_attempts * 2 )) seconds${NC}"
        return 1
    }
    
    # Check app health
    check_app_health
    
    # If app is healthy, run e2e tests
    if [ $? -eq 0 ]; then
        # Run e2e tests in Docker with proper network configuration
        echo -e "\n${GREEN}Running end-to-end tests in Docker...${NC}"
        docker-compose run --rm \
            --network="sorteo_raffle-network" \
            -e STREAMLIT_HOST=app \
            -e STREAMLIT_PORT=8501 \
            test -- pytest tests/e2e/ -v
    else
        echo -e "${RED}Skipping e2e tests due to app health check failure${NC}"
    fi
    
    # Stop the app container
    echo -e "${YELLOW}Stopping app container...${NC}"
    docker-compose stop app
fi

echo -e "\n${GREEN}Tests completed!${NC}"