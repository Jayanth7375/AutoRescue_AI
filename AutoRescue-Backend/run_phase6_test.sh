#!/bin/bash

# AutoRescue AI - Phase 6 Complete System Test
# Tests: HTTP Gateway → Orchestrator → All Specialist Agents

set -e

echo "============================================================"
echo "AutoRescue AI - Phase 6: FastAPI Gateway Integration Test"
echo "============================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to wait for a service
wait_for_service() {
    local name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local max_retries=30

    echo -e "${YELLOW}Waiting for $name on port $port...${NC}"

    for ((i=1; i<=max_retries; i++)); do
        if curl -s "http://127.0.0.1:$port$endpoint" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi
        if [ $i -lt $max_retries ]; then
            echo -n "."
            sleep 1
        fi
    done

    echo -e "${RED}✗ $name failed to start${NC}"
    return 1
}

# Kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    sleep 1
}
trap cleanup EXIT

# Start all agents and gateway
echo -e "\n${BLUE}Starting all services...${NC}\n"

echo "1. Starting Diagnostic Agent (port 8011)..."
python run_diagnostic_agent.py > /tmp/diagnostic.log 2>&1 &
wait_for_service "Diagnostic Agent" 8011

echo "2. Starting Service Agent (port 8013)..."
python run_service_agent.py > /tmp/service.log 2>&1 &
wait_for_service "Service Agent" 8013

echo "3. Starting Rescue Agent (port 8015)..."
python run_rescue_agent.py > /tmp/rescue.log 2>&1 &
wait_for_service "Rescue Agent" 8015

echo "4. Starting Orchestrator Agent (port 8018)..."
python run_orchestrator_agent.py > /tmp/orchestrator.log 2>&1 &
wait_for_service "Orchestrator Agent" 8018

echo "5. Starting FastAPI Gateway (port 8000)..."
python -m uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/gateway.log 2>&1 &
wait_for_service "FastAPI Gateway" 8000

# All services ready
echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}============================================================${NC}"

echo -e "\n${BLUE}Running Gateway Integration Tests...${NC}\n"

# Run the gateway tests
python test_gateway.py

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}============================================================${NC}"
    echo -e "${GREEN}Phase 6 Complete: All Gateway Tests Passed!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    exit 0
else
    echo -e "\n${RED}============================================================${NC}"
    echo -e "${RED}Phase 6 Failed: Some Gateway Tests Failed!${NC}"
    echo -e "${RED}============================================================${NC}"
    exit 1
fi
