@echo off
TITLE NobleLogic Trading System - Quick Start
ECHO.
ECHO ========================================
ECHO  NobleLogic Trading System - Quick Start
ECHO ========================================
ECHO.

REM Set working directory to script location
cd /d "%~dp0"

REM Activate virtual environment if it exists
IF EXIST .\.venv\Scripts\activate.bat (
    ECHO Activating Python virtual environment...
    CALL .\.venv\Scripts\activate.bat
) ELSE (
    ECHO WARNING: Virtual environment not found. Running with system Python.
)
ECHO.

REM Kill any processes on the ports we need
ECHO Checking for running processes on ports 3001 and 3000...
FOR /F "tokens=5" %%P IN ('netstat -a -n -o ^| findstr ":3001"') DO (
    ECHO Killing process %%P on port 3001
    TASKKILL /F /PID %%P >NUL
)
FOR /F "tokens=5" %%P IN ('netstat -a -n -o ^| findstr ":3000"') DO (
    ECHO Killing process %%P on port 3000
    TASKKILL /F /PID %%P >NUL
)
ECHO.

REM Start the backend server in the background
ECHO Starting Backend Server on port 3001...
START "NobleLogic Backend" /B python backend/server.py
ECHO.

REM Wait a few seconds for the backend to initialize
ECHO Waiting for backend to initialize...
timeout /t 5 /nobreak > NUL
ECHO.

REM Start the frontend server
ECHO Starting Frontend Development Server on port 3000...
cd frontend
START "NobleLogic Frontend" /B npm run dev
cd ..
ECHO.

ECHO All services have been launched in background windows.
ECHO You can view the frontend at http://localhost:3000
ECHO This window will close in 10 seconds.

timeout /t 10 > NUL
EXIT