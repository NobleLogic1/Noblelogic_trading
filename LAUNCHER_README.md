# 🚀 NobleLogic Trading System Launcher

## Quick Start
Double-click the **"NobleLogic Trading"** shortcut on your desktop to start the complete system!

## What It Does
The launcher automatically starts all components of the NobleLogic Trading System:

### Services Started:
1. **Backend API Server** (Port 3001) - Flask REST API
2. **Frontend Dashboard** (Port 5173) - React web interface
3. **ML Engine** - GPU-accelerated machine learning
4. **Trading Monitor** - Live trading surveillance
5. **Health Monitor** - System validation and monitoring

### Features:
- ✅ Automatic dependency checking
- ✅ Virtual environment activation
- ✅ API key validation
- ✅ Parallel service startup
- ✅ Browser auto-launch
- ✅ Comprehensive logging

## Manual Usage
If you prefer to run manually:
```batch
# Start everything
start_noblelogic.bat

# Stop everything
stop_noblelogic.bat
```

## System Requirements
- Python 3.8+ with virtual environment
- Node.js 16+
- GPU recommended for ML acceleration
- API keys configured in `config/secure/APIkeys.txt`

## Troubleshooting
- Check logs in the `logs/` directory
- Ensure API keys are properly configured
- Verify Python virtual environment exists
- Make sure ports 3001 and 5173 are available

## Desktop Shortcut
- **Location:** Desktop
- **Name:** NobleLogic Trading
- **Icon:** Large 64x64 custom icon from your screenshot
- **Target:** `start_noblelogic.bat`

## Stopping Services
Use `stop_noblelogic.bat` or close all command windows manually.

---
**Happy Trading! 📈🤖**