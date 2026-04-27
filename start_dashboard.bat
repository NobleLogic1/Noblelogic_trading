@echo off
title NobleLogic Trading Dashboard Launcher
echo ===================================
echo NobleLogic Trading Dashboard Launcher
echo ===================================

:: Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

:: Set the path to include Python and Node.js
set PATH=%PATH%;C:\Program Files\nodejs;%USERPROFILE%\AppData\Roaming\Python\Python313\Scripts

:: Create a timestamp for log files
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

:: Create logs directory if it doesn't exist
if not exist logs mkdir logs

echo Starting services...
echo.

:: Start the backend server with logging
echo Starting backend server...
:: Start the backend server
start "Backend Server" cmd /k "cd backend && python api_server.py"

:: Wait for backend to initialize
echo Waiting for backend initialization...
timeout /t 5 /nobreak > nul

:: Start the frontend development server with logging
echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm run dev > ..\logs\frontend_%TIMESTAMP%.log 2>&1"

:: Wait for frontend to initialize
echo Waiting for frontend initialization...
timeout /t 8 /nobreak > nul

:: Check if ports are in use
netstat -ano | findstr :5000 > nul
if %ERRORLEVEL% EQU 0 (
    echo Backend server is running on port 5000
) else (
    echo WARNING: Backend server may not have started properly
)

netstat -ano | findstr :5173 > nul
if %ERRORLEVEL% EQU 0 (
    echo Frontend server is running on port 5173
) else (
    echo WARNING: Frontend server may not have started properly
)

:: Open the dashboard in default browser
echo.
echo Opening dashboard in browser...
start http://localhost:5173

echo.
echo ===================================
echo Dashboard is now starting up!
echo.
echo Backend server: http://localhost:5000
echo Frontend server: http://localhost:5173
echo Logs are saved in the logs directory
echo.
echo Press Ctrl+C in the respective windows to stop the servers
echo ===================================
echo.

:: Keep the main window open for status messages
pause