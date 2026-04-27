@echo off
title NobleLogic Trading System - Stop All Services
echo.
echo ===============================================
echo   🛑 STOPPING NOBLELOGIC TRADING SYSTEM
echo ===============================================
echo.
echo Stopping all running services...
echo.

REM Kill all Node.js processes (frontend)
echo Stopping frontend services...
taskkill /f /im node.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend services stopped
) else (
    echo ℹ️  No frontend services were running
)

REM Kill all Python processes related to NobleLogic
echo Stopping Python services...
taskkill /f /im python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python services stopped
) else (
    echo ℹ️  No Python services were running
)

REM Kill specific command windows
echo Stopping background services...
taskkill /f /fi "WINDOWTITLE eq NobleLogic Backend API*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq NobleLogic Frontend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq NobleLogic ML Engine*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq NobleLogic Trading Monitor*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq NobleLogic Health Monitor*" >nul 2>&1

echo.
echo ===============================================
echo   ✅ ALL SERVICES STOPPED
echo ===============================================
echo.
echo All NobleLogic Trading System services have been stopped.
echo You can safely close this window.
echo.
pause