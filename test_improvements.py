#!/usr/bin/env python3
"""
Simple test script to verify the NobleLogic Trading improvements
"""
import sys
import os
import json
import time
import requests
import subprocess
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_shared_utils():
    """Test the shared utilities module"""
    print("Testing shared_utils module...")
    
    try:
        from shared_utils import logTrade, updateStrategyOutput, updateHealthStatus
        
        # Test valid trade
        valid_trade = {
            'id': 'test-1',
            'coin': 'BTC',
            'status': 'Open',
            'confidence': 0.75,
            'strategy': 'Momentum',
            'direction': 'Long',
            'pnl': 50.0,
            'signal': 'Buy',
            'timestamp': datetime.now().isoformat()
        }
        
        result = logTrade(valid_trade)
        if result:
            print("✅ Valid trade logging: PASSED")
        else:
            print("❌ Valid trade logging: FAILED")
        
        # Test invalid trade (missing fields)
        invalid_trade = {'id': 'test-2'}
        result = logTrade(invalid_trade)
        if not result:
            print("✅ Invalid trade rejection: PASSED")
        else:
            print("❌ Invalid trade rejection: FAILED")
        
        # Test strategy output
        valid_strategy = {
            'strategy': 'Momentum',
            'confidence': 75.5,
            'active': True
        }
        
        result = updateStrategyOutput(valid_strategy)
        if result:
            print("✅ Strategy output: PASSED")
        else:
            print("❌ Strategy output: FAILED")
        
        # Test health status
        valid_health = {
            'accuracy': 80.5,
            'status': 'Optimal'
        }
        
        result = updateHealthStatus(valid_health)
        if result:
            print("✅ Health status: PASSED")
        else:
            print("❌ Health status: FAILED")
            
    except Exception as e:
        print(f"❌ Shared utils test failed: {e}")

def test_backend_syntax():
    """Test Python backend syntax"""
    print("\nTesting Python syntax...")
    
    python_files = [
        'backend/train_model.py',
        'ml/train_model.py',
        'ml/data_fetcher.py',
        'ml/backtest.py',
        'shared_utils.py'
    ]
    
    for file_path in python_files:
        try:
            result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {file_path}: PASSED")
            else:
                print(f"❌ {file_path}: FAILED - {result.stderr}")
        except Exception as e:
            print(f"❌ {file_path}: ERROR - {e}")

def test_backend_server():
    """Test if the backend server can start"""
    print("\nTesting backend server...")
    
    try:
        # Start server in background
        process = subprocess.Popen(['node', 'backend/server.js'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get('http://localhost:3001/api/status', timeout=5)
            if response.status_code == 200:
                print("✅ Backend server: PASSED")
            else:
                print(f"❌ Backend server: FAILED - Status code {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Backend server: FAILED - {e}")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Backend server test: ERROR - {e}")

def test_frontend_build():
    """Test if the frontend can be built"""
    print("\nTesting frontend build...")
    
    try:
        os.chdir('frontend')
        result = subprocess.run(['npx', 'vite', 'build', '--outDir', '../tmp/dist'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Frontend build: PASSED")
        else:
            print(f"❌ Frontend build: FAILED - {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Frontend build: TIMEOUT")
    except Exception as e:
        print(f"❌ Frontend build: ERROR - {e}")
    finally:
        os.chdir('..')

if __name__ == "__main__":
    print("🔍 Running NobleLogic Trading Tests\n")
    
    test_shared_utils()
    test_backend_syntax()
    test_backend_server()
    test_frontend_build()
    
    print("\n✅ Test suite completed!")