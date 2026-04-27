@echo off
echo Starting NobleLogic Trading System...
echo ====================================

REM Check for required dependencies
echo Checking dependencies...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed! Please install Node.js and try again.
    exit /b 1
)

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed! Please install Python and try again.
    exit /b 1
)

REM Set environment variables
echo Loading environment variables...
if exist .env (
    for /F "tokens=*" %%i in (.env) do set %%i
) else (
    echo Warning: .env file not found!
    echo Please ensure your API keys are properly configured.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking for dependencies...
cd backend
if not exist "node_modules" (
    echo Installing backend Node dependencies...
    call npm install
)
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt

cd ..\frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start backend services
echo Starting backend services...
cd ..\backend
start cmd /k "call venv\Scripts\activate && python ml_server.py"
timeout /t 2 /nobreak
start cmd /k "node server.js"

REM Start frontend
echo Starting frontend...
cd ..\frontend
start cmd /k "npm start"

REM Wait for services to start
echo Waiting for services to initialize...
timeout /t 10 /nobreak

REM Open dashboard in default browser
echo Opening dashboard in browser...
start http://localhost:3000

echo ====================================
echo NobleLogic Trading System is running!
echo ====================================
echo.
echo Control Panel URLs:
echo - Dashboard: http://localhost:3000
echo - Backend API: http://localhost:3001
echo - ML Service: http://localhost:3002
echo.
echo To stop the system:
echo 1. Press Ctrl+C in each terminal window
echo 2. Or run stop_trading.bat
echo ====================================

REM Keep the script running
pause