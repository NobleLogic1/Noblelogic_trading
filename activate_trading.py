#!/usr/bin/env python3
"""
Trading System Activator - Enables Live Trading
============================================
This script activates the automated trading system
"""

import sys
import os
import asyncio
import requests
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.binance_us_api import BinanceUSAPI
from live_trading_30min import LiveTradingSystem

class TradingSystemActivator:
    def __init__(self):
        self.backend_url = "http://localhost:5000"
        self.api = BinanceUSAPI(live_mode=True)
        
    def check_backend_status(self):
        """Check if backend server is running"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running")
                return True
            else:
                print(f"❌ Backend server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend server not accessible: {e}")
            return False
    
    def check_api_keys(self):
        """Check if API keys are configured"""
        try:
            # Check for .env file
            if not os.path.exists('.env'):
                print("❌ .env file not found")
                return False
                
            with open('.env', 'r') as f:
                content = f.read()
                if 'your-binance-api-key-here' in content or 'your-binance-secret-key-here' in content:
                    print("❌ API keys not configured in .env file")
                    print("   Please update your API keys in .env file")
                    return False
                    
            print("✅ API keys appear to be configured")
            return True
            
        except Exception as e:
            print(f"❌ Error checking API keys: {e}")
            return False
    
    def activate_trading_backend(self):
        """Activate trading through backend API"""
        try:
            response = requests.post(f"{self.backend_url}/api/autotrade", 
                                   json={"enabled": True}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Backend trading activated")
                    return True
                else:
                    print(f"❌ Backend trading activation failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Failed to activate backend trading: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error activating backend trading: {e}")
            return False
    
    def get_trading_status(self):
        """Get current trading status"""
        try:
            response = requests.get(f"{self.backend_url}/api/trading/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Trading Status:")
                print(f"   Active: {data.get('trading_active', False)}")
                print(f"   Demo Mode: {data.get('demo_mode', True)}")
                print(f"   Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0)/1000)}")
                return data
            else:
                print(f"❌ Failed to get trading status: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting trading status: {e}")
            return None
    
    def start_live_trading_system(self):
        """Start the dedicated live trading system"""
        print("\n🚀 Starting Live Trading System...")
        print("   This will run the 30-minute live trading session")
        print("   Press Ctrl+C to stop\n")
        
        try:
            # Import and run the live trading system
            asyncio.run(self.run_live_trading())
        except KeyboardInterrupt:
            print("\n🛑 Live trading interrupted by user")
        except Exception as e:
            print(f"❌ Live trading system error: {e}")
    
    async def run_live_trading(self):
        """Run the live trading system"""
        # Initialize trading system
        trading_system = LiveTradingSystem()

        # Start real-time data aggregator
        print("📡 Starting real-time data aggregator...")
        await trading_system.data_fetcher.subscribe_symbols(trading_system.symbols)

        # Start data aggregator in background
        aggregator_task = asyncio.create_task(trading_system.data_fetcher.start())

        try:
            # Run live trading session
            await trading_system.run_live_session()
        finally:
            # Clean shutdown
            print("🛑 Shutting down data aggregator...")
            await trading_system.data_fetcher.stop()
            aggregator_task.cancel()

            try:
                await aggregator_task
            except asyncio.CancelledError:
                pass

    def run_diagnostic(self):
        """Run full system diagnostic"""
        print("🔍 NobleLogic Trading System - Diagnostic Report")
        print("=" * 60)
        
        # Check backend
        backend_ok = self.check_backend_status()
        
        # Check API keys
        api_keys_ok = self.check_api_keys()
        
        # Get current status
        status = self.get_trading_status()
        
        print("\n" + "=" * 60)
        print("📋 DIAGNOSTIC SUMMARY:")
        print(f"   Backend Server: {'✅ Running' if backend_ok else '❌ Not Running'}")
        print(f"   API Keys: {'✅ Configured' if api_keys_ok else '❌ Missing'}")
        print(f"   Trading Active: {'✅ Yes' if status and status.get('trading_active') else '❌ No'}")
        
        if not backend_ok:
            print("\n🛠️  TO FIX: Start the backend server")
            print("   Run: python backend/server.py")
            
        if not api_keys_ok:
            print("\n🛠️  TO FIX: Configure API keys in .env file")
            
        if backend_ok and api_keys_ok and status and not status.get('trading_active'):
            print("\n🛠️  TO FIX: Activate trading")
            print("   Run: python activate_trading.py --activate")
            
        return backend_ok and api_keys_ok

def main():
    activator = TradingSystemActivator()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--activate':
        print("🚀 Activating Trading System...")
        print("=" * 60)
        
        # Run diagnostic first
        if not activator.run_diagnostic():
            print("\n❌ System not ready for trading activation")
            sys.exit(1)
            
        print("\n🔄 Activating trading...")
        
        # Activate backend trading
        if activator.activate_trading_backend():
            print("\n✅ Trading system activated!")
            
            # Optionally start live trading
            start_live = input("\nStart live trading session? (y/N): ")
            if start_live.lower() == 'y':
                activator.start_live_trading_system()
        else:
            print("\n❌ Failed to activate trading system")
            sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--live':
        print("🚀 Starting Live Trading Session...")
        activator.start_live_trading_system()
        
    else:
        # Just run diagnostic
        activator.run_diagnostic()
        print("\n" + "=" * 60)
        print("💡 USAGE:")
        print("   python activate_trading.py                 # Run diagnostic")
        print("   python activate_trading.py --activate      # Activate trading")
        print("   python activate_trading.py --live          # Start live session")

if __name__ == "__main__":
    main()