@echo off
title NobleLogic Trading System - Complete Startup
echo.
echo ===============================================
echo   🚀 STARTING NOBLELOGIC TRADING SYSTEM
echo ===============================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

echo [1/5] Checking Python environment...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Activate virtual environment if available
if exist ".venv\Scripts\activate.bat" (
    echo [2/5] Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo [2/5] Using system Python...
)

echo [3/5] Starting backend server...
start "NobleLogic Backend" python backend\server.py

REM Wait for backend to start
echo [4/5] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Check if backend started successfully
python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=2)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend server started successfully
) else (
    echo ⚠️  Backend server may still be starting...
)

echo [5/5] System startup complete!
echo.
echo ===============================================
echo   📊 TRADING SYSTEM STATUS
echo ===============================================

REM Run diagnostic
python activate_trading.py

echo.
echo ===============================================
echo   💡 NEXT STEPS
echo ===============================================
echo.
echo To activate trading:
echo   1. Configure API keys in .env file (if not done)
echo   2. Run: python activate_trading.py --activate
echo.
echo To start live trading:
echo   3. Run: python activate_trading.py --live
echo.
echo Dashboard URLs (if frontend running):
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:5000
echo.
pause