#!/usr/bin/env python3
"""
Simple Trading System Status Checker
====================================
Check if the trading system is ready and running
"""

import requests
import json
import time

def check_system_status():
    """Check complete system status"""
    print("🔍 Trading System Status Check")
    print("=" * 50)
    
    # Check backend
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Server: Running")
            
            # Check trading status
            status_response = requests.get("http://localhost:5000/api/trading/status", timeout=5)
            if status_response.status_code == 200:
                data = status_response.json()
                print(f"📊 Trading Status: {'Active' if data.get('trading_active') else 'Inactive'}")
                print(f"🎭 Demo Mode: {'Yes' if data.get('demo_mode') else 'No'}")
            else:
                print("❌ Trading Status: Unable to determine")
                
        else:
            print("❌ Backend Server: Not responding properly")
            
    except requests.exceptions.RequestException:
        print("❌ Backend Server: Not running")
    
    # Check frontend (if running)
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("✅ Frontend: Running")
        else:
            print("❌ Frontend: Not responding")
    except requests.exceptions.RequestException:
        print("❌ Frontend: Not running")
    
    print("\n" + "=" * 50)
    
def activate_trading():
    """Activate trading via API"""
    try:
        response = requests.post("http://localhost:5000/api/autotrade", 
                               json={"enabled": True}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Trading activated successfully!")
                return True
            else:
                print(f"❌ Failed to activate: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_system_status()
    
    # Ask if user wants to activate trading
    activate = input("\nActivate trading? (y/N): ")
    if activate.lower() == 'y':
        print("\n🚀 Activating trading...")
        if activate_trading():
            print("🎯 Trading system is now active!")
        else:
            print("❌ Trading activation failed")
    
    print("\n💡 To check status again, run: python check_status.py")