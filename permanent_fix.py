#!/usr/bin/env python3
"""
NobleLogic Trading System - Permanent Startup Fix
================================================
This script diagnoses and fixes all common startup issues automatically
"""

import os
import sys
import json
import subprocess
import time
import requests
import threading
import signal
from pathlib import Path

class TradingSystemFixer:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_port = 3001
        self.frontend_port = 3000
        self.processes = {}
        self.running = True
        
    def fix_directory_structure(self):
        """Create all required directories"""
        print("🔧 Fixing directory structure...")
        
        required_dirs = [
            'logs',
            'logs/audit', 
            'data',
            'models',
            'config/secure',
            'backend/data',
            'ml/models'
        ]
        
        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {dir_path}")
            
    def fix_api_keys(self):
        """Check and create API key configuration"""
        print("🔧 Checking API key configuration...")
        
        api_key_file = self.root_dir / 'config' / 'secure' / 'APIkeys.txt'
        
        if not api_key_file.exists():
            # Create template API key file
            template_content = """# NobleLogic Trading System API Keys
# Replace with your actual Binance.US API credentials

BINANCE_US_API_KEY=your_actual_binance_us_api_key_here
BINANCE_US_SECRET_KEY=your_actual_binance_us_secret_key_here

# Security Notes:
# - Never share these keys
# - Enable IP whitelist in Binance.US
# - Use spot trading permissions only
# - Regularly rotate your keys
"""
            api_key_file.write_text(template_content)
            print(f"   ⚠️  Created template API key file: {api_key_file}")
            print(f"   📝 Please edit {api_key_file} with your actual API keys")
            return False
        else:
            # Check if keys are configured
            content = api_key_file.read_text()
            if 'your_actual_binance_us_api_key_here' in content:
                print(f"   ⚠️  API keys need to be configured in: {api_key_file}")
                return False
            else:
                print(f"   ✅ API keys configured")
                return True
    
    def fix_environment_file(self):
        """Create or fix .env file"""
        print("🔧 Checking environment configuration...")
        
        env_file = self.root_dir / '.env'
        
        if not env_file.exists():
            env_content = """# NobleLogic Trading System Environment
NODE_ENV=development
REACT_APP_API_URL=http://localhost:3001
FLASK_ENV=development
FLASK_DEBUG=1

# Trading Settings
DEMO_MODE=true
INITIAL_CAPITAL=1000
MAX_RISK_PER_TRADE=0.02

# Security
ENABLE_CORS=true
LOG_LEVEL=INFO
"""
            env_file.write_text(env_content)
            print(f"   ✅ Created .env file")
        else:
            print(f"   ✅ .env file exists")
    
    def fix_python_dependencies(self):
        """Install missing Python dependencies"""
        print("🔧 Checking Python dependencies...")
        
        # Check if virtual environment exists
        venv_path = self.root_dir / '.venv'
        if not venv_path.exists():
            print("   🔄 Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', '.venv'], 
                         cwd=self.root_dir, check=True)
            print("   ✅ Virtual environment created")
        
        # Use the virtual environment Python
        if os.name == 'nt':  # Windows
            python_exe = venv_path / 'Scripts' / 'python.exe'
            pip_exe = venv_path / 'Scripts' / 'pip.exe'
        else:  # Unix/Linux/Mac
            python_exe = venv_path / 'bin' / 'python'
            pip_exe = venv_path / 'bin' / 'pip'
        
        # Install requirements
        requirements_file = self.root_dir / 'requirements.txt'
        if requirements_file.exists():
            print("   🔄 Installing Python packages...")
            try:
                subprocess.run([str(pip_exe), 'install', '-r', str(requirements_file)], 
                             cwd=self.root_dir, check=True, 
                             capture_output=True, text=True)
                print("   ✅ Python dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Some packages failed to install: {e}")
                return False
        else:
            print(f"   ⚠️  requirements.txt not found")
            return False
    
    def fix_node_dependencies(self):
        """Install Node.js dependencies"""
        print("🔧 Checking Node.js dependencies...")
        
        frontend_dir = self.root_dir / 'frontend'
        if not frontend_dir.exists():
            print("   ⚠️  Frontend directory not found")
            return False
        
        # Check if node_modules exists
        node_modules = frontend_dir / 'node_modules'
        package_json = frontend_dir / 'package.json'
        
        if package_json.exists() and not node_modules.exists():
            print("   🔄 Installing Node.js packages...")
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True,
                             capture_output=True, text=True)
                print("   ✅ Node.js dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  npm install failed: {e}")
                return False
        else:
            print("   ✅ Node.js dependencies OK")
            return True
    
    def kill_existing_processes(self):
        """Kill any existing processes on our ports"""
        print("🔧 Cleaning up existing processes...")
        
        ports = [self.backend_port, self.frontend_port]
        
        for port in ports:
            try:
                if os.name == 'nt':  # Windows
                    # Find processes using the port
                    result = subprocess.run(['netstat', '-ano'], 
                                          capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if f':{port} ' in line and 'LISTENING' in line:
                            # Extract PID (last column)
                            pid = line.strip().split()[-1]
                            try:
                                subprocess.run(['taskkill', '/F', '/PID', pid], 
                                             capture_output=True)
                                print(f"   ✅ Killed process on port {port}")
                            except:
                                pass
                else:  # Unix/Linux/Mac
                    subprocess.run(['pkill', '-f', f':{port}'], capture_output=True)
            except:
                pass
    
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        
        # Use virtual environment Python
        venv_path = self.root_dir / '.venv'
        if os.name == 'nt':
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:
            python_exe = venv_path / 'bin' / 'python'
        
        # Start backend
        backend_script = self.root_dir / 'backend' / 'server.py'
        
        try:
            process = subprocess.Popen(
                [str(python_exe), str(backend_script)],
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes['backend'] = process
            
            # Wait for server to start
            max_wait = 30  # seconds
            for i in range(max_wait):
                try:
                    response = requests.get(f'http://localhost:{self.backend_port}/api/health', 
                                          timeout=2)
                    if response.status_code == 200:
                        print(f"   ✅ Backend server running on port {self.backend_port}")
                        return True
                except:
                    time.sleep(1)
                    
            print(f"   ❌ Backend server failed to start")
            return False
            
        except Exception as e:
            print(f"   ❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🚀 Starting frontend server...")
        
        frontend_dir = self.root_dir / 'frontend'
        if not frontend_dir.exists():
            print("   ⚠️  Frontend directory not found, skipping...")
            return True
        
        package_json = frontend_dir / 'package.json'
        if not package_json.exists():
            print("   ⚠️  Frontend package.json not found, skipping...")
            return True
        
        try:
            # Set environment variables for frontend
            env = os.environ.copy()
            env['REACT_APP_API_URL'] = f'http://localhost:{self.backend_port}'
            env['PORT'] = str(self.frontend_port)
            
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env
            )
            
            self.processes['frontend'] = process
            
            # Wait for server to start
            max_wait = 60  # seconds (frontend takes longer)
            for i in range(max_wait):
                try:
                    response = requests.get(f'http://localhost:{self.frontend_port}', 
                                          timeout=2)
                    if response.status_code == 200:
                        print(f"   ✅ Frontend server running on port {self.frontend_port}")
                        return True
                except:
                    time.sleep(2)
                    
            print(f"   ⚠️  Frontend server may still be starting...")
            return True
            
        except Exception as e:
            print(f"   ❌ Error starting frontend: {e}")
            return False
    
    def enable_trading(self):
        """Enable trading system"""
        print("🔧 Enabling trading system...")
        
        try:
            response = requests.post(f'http://localhost:{self.backend_port}/api/autotrade',
                                   json={'enabled': True}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("   ✅ Trading system activated")
                    return True
                    
        except Exception as e:
            print(f"   ⚠️  Could not activate trading: {e}")
            
        return False
    
    def show_status(self):
        """Display system status"""
        print("\n" + "="*60)
        print("📊 NOBLELOGIC TRADING SYSTEM STATUS")
        print("="*60)
        
        # Backend status
        try:
            response = requests.get(f'http://localhost:{self.backend_port}/api/health', timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend Server: Running on http://localhost:{self.backend_port}")
                
                # Trading status
                try:
                    status_response = requests.get(f'http://localhost:{self.backend_port}/api/trading/status', timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        trading_active = status_data.get('trading_active', False)
                        demo_mode = status_data.get('demo_mode', True)
                        
                        print(f"📈 Trading Status: {'Active' if trading_active else 'Inactive'}")
                        print(f"🎭 Demo Mode: {'Yes' if demo_mode else 'No'}")
                except:
                    print("⚠️  Trading Status: Unknown")
            else:
                print(f"❌ Backend Server: Error {response.status_code}")
        except:
            print("❌ Backend Server: Not responding")
        
        # Frontend status
        try:
            response = requests.get(f'http://localhost:{self.frontend_port}', timeout=5)
            if response.status_code == 200:
                print(f"✅ Frontend Server: Running on http://localhost:{self.frontend_port}")
            else:
                print(f"❌ Frontend Server: Error {response.status_code}")
        except:
            print("❌ Frontend Server: Not responding")
        
        print("\n" + "="*60)
        print("🌐 ACCESS URLS:")
        print(f"   Dashboard: http://localhost:{self.frontend_port}")
        print(f"   API: http://localhost:{self.backend_port}")
        print("="*60)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        def signal_handler(signum, frame):
            print("\n🛑 Shutting down...")
            self.running = False
            for name, process in self.processes.items():
                print(f"   Stopping {name}...")
                process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_full_fix(self):
        """Run complete system fix and startup"""
        print("🚀 NobleLogic Trading System - Permanent Fix")
        print("="*60)
        
        # Fix all issues
        self.fix_directory_structure()
        self.fix_environment_file()
        api_keys_ok = self.fix_api_keys()
        python_ok = self.fix_python_dependencies()
        node_ok = self.fix_node_dependencies()
        
        print("\n🔧 SYSTEM PREPARATION COMPLETE")
        print("="*60)
        
        if not python_ok:
            print("❌ Python dependencies not fully installed")
            print("   Please run: pip install -r requirements.txt")
            return False
        
        # Clean up and start services
        self.kill_existing_processes()
        time.sleep(2)
        
        backend_ok = self.start_backend()
        if not backend_ok:
            print("❌ Failed to start backend server")
            return False
        
        # Enable trading
        self.enable_trading()
        
        # Start frontend (optional)
        if node_ok:
            self.start_frontend()
        
        # Show final status
        time.sleep(3)
        self.show_status()
        
        if not api_keys_ok:
            print("\n⚠️  IMPORTANT: Configure your API keys to enable live trading")
            print(f"   Edit: {self.root_dir / 'config' / 'secure' / 'APIkeys.txt'}")
        
        return True
    
    def monitor_services(self):
        """Monitor running services"""
        self.setup_signal_handlers()
        
        print("\n🔄 Monitoring services... (Press Ctrl+C to stop)")
        
        while self.running:
            try:
                time.sleep(30)
                
                # Check backend health
                try:
                    response = requests.get(f'http://localhost:{self.backend_port}/api/health', timeout=5)
                    if response.status_code != 200:
                        print("⚠️  Backend server unhealthy, restarting...")
                        if 'backend' in self.processes:
                            self.processes['backend'].terminate()
                        self.start_backend()
                except:
                    print("⚠️  Backend server not responding, restarting...")
                    if 'backend' in self.processes:
                        self.processes['backend'].terminate()
                    self.start_backend()
                    
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    fixer = TradingSystemFixer()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        fixer.monitor_services()
    else:
        success = fixer.run_full_fix()
        if success:
            print("\n✅ System startup complete!")
            
            # Ask if user wants to monitor
            try:
                monitor = input("\nStart service monitoring? (Y/n): ")
                if monitor.lower() != 'n':
                    fixer.monitor_services()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
        else:
            print("\n❌ System startup failed!")
            sys.exit(1)