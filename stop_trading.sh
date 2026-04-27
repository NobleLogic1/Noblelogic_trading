#!/bin/bash

echo "Stopping NobleLogic Trading System..."
echo "===================================="

# Kill processes by port
echo "Stopping Node.js processes..."
kill $(lsof -t -i:3000) 2>/dev/null
kill $(lsof -t -i:3001) 2>/dev/null
kill $(lsof -t -i:3002) 2>/dev/null

# Kill Python processes
echo "Stopping Python processes..."
pkill -f "python.*ml_server.py"

echo "===================================="
echo "Trading system stopped successfully!"
echo "===================================="