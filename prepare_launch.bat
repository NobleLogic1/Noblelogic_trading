@echo off
REM NobleLogic Trading System - Launch Preparation Script (Windows)
REM This script installs all dependencies and prepares the system for launch

title NobleLogic Trading System - Launch Preparation
echo 🚀 NobleLogic Trading System - Launch Preparation
echo =================================================

REM Check system requirements
echo 📋 Checking system requirements...

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js found: %NODE_VERSION%

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python from https://python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Check pip
where pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)
echo ✅ pip found

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Navigate to backend and install Node.js dependencies
echo 📦 Installing backend Node.js dependencies...
cd backend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

REM Navigate to frontend and install dependencies
echo 📦 Installing frontend dependencies...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "ml\models" mkdir ml\models
if not exist "backend\data" mkdir backend\data

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 🔧 Please edit .env file with your actual API keys before running the system.
)

echo.
echo ✅ Launch preparation completed!
echo.
echo Next steps:
echo 1. Edit the .env file with your Binance API credentials
echo 2. Run 'start_dashboard.bat' to launch the trading dashboard
echo 3. Run 'start_trading.bat' to start the trading system
echo.
echo 🔗 Dashboard will be available at: http://localhost:5173
echo 🔗 API Server will be available at: http://localhost:3001
echo.
pause