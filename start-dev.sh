#!/bin/bash

# NLP Knowledge Discovery System - Development Environment Setup

echo "==========================================="
echo "NLP Knowledge Discovery System"
echo "Starting Development Services..."
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$PROJECT_ROOT/backend"
FRONTEND="$PROJECT_ROOT/frontend"
ML_SERVICE="$PROJECT_ROOT/ml-service"

# Check if services are already running
check_port() {
  if nc -z localhost $1 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Start services
echo -e "${BLUE}[1] Starting MySQL (Port 3306)...${NC}"
if check_port 3306; then
  echo -e "${GREEN}✓ MySQL already running${NC}"
else
  sudo systemctl start mysql
  sleep 2
  echo -e "${GREEN}✓ MySQL started${NC}"
fi
echo ""

echo -e "${BLUE}[2] Starting Laravel API (Port 8000)...${NC}"
cd "$BACKEND"
php artisan serve --port=8000 > /tmp/laravel.log 2>&1 &
LARAVEL_PID=$!
sleep 2
if check_port 8000; then
  echo -e "${GREEN}✓ Laravel running (PID: $LARAVEL_PID)${NC}"
else
  echo -e "${YELLOW}⚠ Laravel may not be ready${NC}"
fi
echo ""

echo -e "${BLUE}[3] Starting Python ML Service (Port 5000)...${NC}"
cd "$ML_SERVICE"
source venv/bin/activate
python app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!
sleep 2
if check_port 5000; then
  echo -e "${GREEN}✓ Flask running (PID: $FLASK_PID)${NC}"
else
  echo -e "${YELLOW}⚠ Flask may not be ready${NC}"
fi
echo ""

echo -e "${BLUE}[4] Starting React Dev Server (Port 5173)...${NC}"
cd "$FRONTEND"
npm run dev > /tmp/react.log 2>&1 &
REACT_PID=$!
sleep 3
if check_port 5173; then
  echo -e "${GREEN}✓ React running (PID: $REACT_PID)${NC}"
else
  echo -e "${YELLOW}⚠ React may not be ready${NC}"
fi
echo ""

echo "==========================================="
echo -e "${GREEN}✓ Development environment started!${NC}"
echo "==========================================="
echo ""
echo "Services running on:"
echo "  • MySQL:     localhost:3306"
echo "  • Laravel:   http://localhost:8000"
echo "  • React:     http://localhost:5173"
echo "  • ML API:    http://localhost:5000"
echo ""
echo "Process IDs:"
echo "  • Laravel:   $LARAVEL_PID"
echo "  • Flask:     $FLASK_PID"
echo "  • React:     $REACT_PID"
echo ""
echo "Logs:"
echo "  • Laravel:   /tmp/laravel.log"
echo "  • Flask:     /tmp/flask.log"
echo "  • React:     /tmp/react.log"
echo ""
echo "To stop services, run: kill $LARAVEL_PID $FLASK_PID $REACT_PID"
echo "==========================================="

# Keep script running
wait
