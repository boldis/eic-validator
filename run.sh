#!/bin/bash
# Startup script for EIC/EAN Validation Service

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting EIC/EAN Validation Service${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run tests
echo -e "${BLUE}Running tests...${NC}"
pytest -q

# Start the server
echo -e "${GREEN}Starting server on http://0.0.0.0:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}Health Check: http://localhost:8000/health${NC}"
echo ""
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
