#!/bin/bash

echo "🚀 Starting NobleLogic Trading Cockpit..."

# Step 1: Start backend
echo "🔌 Launching backend server..."
cd backend
npm install express cors --silent
node server.js &
BACKEND_PID=$!
cd ..

# Step 2: Run ML pipeline
echo "🧠 Running ML training and backtest..."
cd ml
pip install -q pandas numpy scikit-learn ta requests
python train_model.py
python backtest.py
cd ..

# Step 3: Launch frontend
echo "🎨 Starting frontend dashboard..."
cd frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!
cd ..

# Step 4: Summary
echo "✅ Cockpit is live!"
echo "Backend: http://localhost:3001"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop servers."

# Keep script alive
wait $BACKEND_PID $FRONTEND_PID