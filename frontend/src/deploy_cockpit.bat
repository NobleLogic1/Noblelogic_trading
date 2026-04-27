@echo off
echo 🚀 Launching NobleLogic Trading Cockpit...

REM Step 1: Start backend
echo 🔌 Starting backend server...
cd backend
call npm install express cors --silent
start cmd /k "node server.js"
cd ..

REM Step 2: Run ML pipeline
echo 🧠 Running ML training and backtest...
cd ml
call pip install pandas numpy scikit-learn ta requests --quiet
python train_model.py
python backtest.py
cd ..

REM Step 3: Launch frontend
echo 🎨 Starting frontend dashboard...
cd frontend
call npm install --silent
start cmd /k "npm run dev"
cd ..

echo ✅ Cockpit is live!
echo Backend: http://localhost:3001
echo Frontend: http://localhost:5173
pause