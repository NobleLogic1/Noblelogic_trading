@echo off
title NobleLogic Trading System - Quick Start
echo.
echo ===============================================
echo   🚀 NOBLELOGIC TRADING SYSTEM
echo ===============================================
echo.
echo This will automatically fix all startup issues
echo and launch the complete trading system.
echo.

REM Set working directory to script location
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Python not found in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Running system fix and startup...
echo.

python permanent_fix.py

echo.
pause