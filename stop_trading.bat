@echo off
echo Stopping NobleLogic Trading System...
echo ====================================

REM Stop Node.js processes
echo Stopping Node.js processes...
for /f "tokens=5" %%a in ('netstat -ano ^| find "3000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| find "3001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| find "3002" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

REM Stop Python processes
echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

echo ====================================
echo Trading system stopped successfully!
echo ====================================
pause