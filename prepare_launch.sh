#!/bin/bash
# NobleLogic Trading System - Launch Preparation Script
# This script installs all dependencies and prepares the system for launch

echo "🚀 NobleLogic Trading System - Launch Preparation"
echo "================================================="

# Check system requirements
echo "📋 Checking system requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi
echo "✅ Python found: $(python --version)"

# Check pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi
echo "✅ pip found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to backend and install Node.js dependencies
echo "📦 Installing backend Node.js dependencies..."
cd backend
npm install
cd ..

# Navigate to frontend and install dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ml/models
mkdir -p backend/data

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "🔧 Please edit .env file with your actual API keys before running the system."
fi

# Set proper permissions for scripts
echo "🔐 Setting script permissions..."
chmod +x start_dashboard.bat
chmod +x start_trading.bat
chmod +x stop_trading.bat

echo ""
echo "✅ Launch preparation completed!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your Binance API credentials"
echo "2. Run 'start_dashboard.bat' to launch the trading dashboard"
echo "3. Run 'start_trading.bat' to start the trading system"
echo ""
echo "🔗 Dashboard will be available at: http://localhost:5173"
echo "🔗 API Server will be available at: http://localhost:3001"