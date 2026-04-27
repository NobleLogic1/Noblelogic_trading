#!/bin/bash

echo "Starting NobleLogic Trading System..."
echo "===================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
echo "Checking dependencies..."
if ! command_exists node; then
    echo "Node.js is not installed! Please install Node.js and try again."
    exit 1
fi

if ! command_exists python3; then
    echo "Python is not installed! Please install Python and try again."
    exit 1
fi

# Load environment variables
echo "Loading environment variables..."
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "Warning: .env file not found!"
    echo "Please ensure your API keys are properly configured."
    read -p "Press Enter to exit..."
    exit 1
fi

# Install dependencies if needed
echo "Checking for dependencies..."
cd backend
if [ ! -d "node_modules" ]; then
    echo "Installing backend Node dependencies..."
    npm install
fi

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start backend services
echo "Starting backend services..."
cd ../backend
source venv/bin/activate
python3 ml_server.py &
ML_PID=$!
sleep 2
node server.js &
SERVER_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 10

# Open dashboard in default browser
echo "Opening dashboard in browser..."
if command_exists xdg-open; then
    xdg-open http://localhost:3000
elif command_exists open; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi

echo "===================================="
echo "NobleLogic Trading System is running!"
echo "===================================="
echo
echo "Control Panel URLs:"
echo "- Dashboard: http://localhost:3000"
echo "- Backend API: http://localhost:3001"
echo "- ML Service: http://localhost:3002"
echo
echo "To stop the system:"
echo "1. Press Ctrl+C"
echo "2. Or run ./stop_trading.sh"
echo "===================================="

# Create cleanup function
cleanup() {
    echo "Stopping services..."
    kill $ML_PID 2>/dev/null
    kill $SERVER_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Keep script running
wait