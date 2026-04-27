"""
Safe Launch Script for NobleLogic Trading System
Starts the system in test mode for safe trials
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """
    Check if environment is properly configured
    """
    print("🔍 Checking environment...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Check required directories
    required_dirs = ['logs', 'ml/models', 'backend/data']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"📁 Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # Check Python dependencies (fast check)
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'fast_dependency_check.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All Python dependencies found")
        else:
            print("❌ Missing dependencies detected")
            print("Run: pip install -r requirements.txt")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        # Fallback to basic imports
        try:
            import flask
            import pandas
            print("✅ Core dependencies available")
        except ImportError as ie:
            print(f"❌ Missing dependency: {ie}")
            return False
    
    print("✅ Environment check passed")
    return True

def display_launch_menu():
    """
    Display launch options
    """
    print("\n" + "="*50)
    print("🚀 NOBLELOGIC TRADING SYSTEM - SAFE LAUNCH")
    print("="*50)
    print("\nLAUNCH OPTIONS:")
    print("1. 🧪 Test Mode - 30 min simulation (RECOMMENDED)")
    print("2. 🔬 Extended Test - 4 hour simulation")
    print("3. 🌐 Dashboard Only - View interface without trading")
    print("4. ⚙️  Backend Only - API server for external tools")
    print("5. 🚨 Paper Trading - Live data, simulated trades")
    print("6. ❌ Exit")
    print("-"*50)

async def launch_test_mode(duration_minutes=30):
    """
    Launch safe test mode
    """
    print(f"\n🧪 Starting Test Mode ({duration_minutes} minutes)")
    print("This mode uses simulated data and ML learning")
    print("No real money will be used")
    print("-"*30)
    
    try:
        from test_mode import TradingTestMode
        test_system = TradingTestMode()
        await test_system.start_test_session(
            duration_minutes=duration_minutes,
            trades_per_hour=20 if duration_minutes <= 60 else 15
        )
    except Exception as e:
        print(f"❌ Test mode failed: {e}")
        print("Check that all dependencies are installed")

def launch_dashboard_only():
    """
    Launch only the dashboard for viewing
    """
    print("\n🌐 Starting Dashboard Only Mode")
    print("You can view the interface at: http://localhost:5173")
    print("Press Ctrl+C to stop")
    print("-"*30)
    
    try:
        os.system("cd frontend && npm run dev")
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

def launch_backend_only():
    """
    Launch only the backend API
    """
    print("\n⚙️  Starting Backend API Only")
    print("API available at: http://localhost:3001")
    print("Press Ctrl+C to stop")
    print("-"*30)
    
    try:
        os.system("cd backend && python server.py")
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")

async def launch_paper_trading():
    """
    Launch paper trading with live data
    """
    print("\n🚨 Paper Trading Mode")
    print("⚠️  WARNING: This mode uses live market data")
    print("⚠️  but simulates trades (no real money)")
    print("-"*30)
    
    # Check if API keys are configured
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'your-binance-api-key-here' in env_content:
            print("❌ Please configure your API keys in .env file first")
            return
    
    confirm = input("Continue with paper trading? (y/N): ")
    if confirm.lower() != 'y':
        print("Paper trading cancelled")
        return
    
    print("🚀 Starting paper trading...")
    # This would start the live paper trading system
    print("📝 Paper trading is not fully implemented yet")
    print("Please use test mode for now")

async def main():
    """
    Main launch function
    """
    print(f"🕒 System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues and try again.")
        return
    
    while True:
        display_launch_menu()
        
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                await launch_test_mode(30)
            elif choice == '2':
                await launch_test_mode(240)  # 4 hours
            elif choice == '3':
                launch_dashboard_only()
            elif choice == '4':
                launch_backend_only()
            elif choice == '5':
                await launch_paper_trading()
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 System shutdown requested")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        # Ask if user wants to continue
        if choice in ['1', '2']:
            continue_choice = input("\nRun another test? (y/N): ")
            if continue_choice.lower() != 'y':
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 System shutdown")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please check your installation and try again")