@echo off
echo ================================
echo  Launching NobleLogic Cockpit
echo ================================

REM Step 1: Start backend server
start cmd /k "cd /d F:\noblelogic_trading\backend && python server.py"

REM Step 2: Run ML model
start cmd /k "cd /d F:\noblelogic_trading\backend && python train_model.py"

REM Step 3: Start frontend
start cmd /k "cd /d F:\noblelogic_trading\frontend && npm run dev"

REM Step 4: Launch cockpit in default browser
start http://localhost:5173

echo All systems launched. Cockpit is now open in your browser.
pause