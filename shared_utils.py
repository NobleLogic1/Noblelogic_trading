"""
Shared utilities for the NobleLogic Trading application
"""
import json
import os

# Get the backend directory path relative to any location
def get_backend_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Find backend directory by looking for it in parent directories
    while current_dir != '/':
        backend_path = os.path.join(current_dir, 'backend')
        if os.path.exists(backend_path):
            return backend_path
        current_dir = os.path.dirname(current_dir)
    # Fallback to relative path
    return os.path.join(os.path.dirname(__file__), '..', 'backend')

BASE_DIR = get_backend_dir()
TRADE_LOG_PATH = os.path.join(BASE_DIR, 'trade_log.json')
STRATEGY_OUTPUT_PATH = os.path.join(BASE_DIR, 'strategy_output.json')
HEALTH_STATUS_PATH = os.path.join(BASE_DIR, 'health_status.json')

def logTrade(trade):
    """Append a trade to the log"""
    # Validate trade data
    required_fields = ['id', 'coin', 'status', 'confidence', 'strategy', 'direction', 'pnl', 'signal']
    if not isinstance(trade, dict):
        print("Error: Trade must be a dictionary")
        return False
    
    for field in required_fields:
        if field not in trade:
            print(f"Error: Trade missing required field: {field}")
            return False
    
    # Validate data types
    if not isinstance(trade['confidence'], (int, float)) or not (0 <= trade['confidence'] <= 1):
        print("Error: Confidence must be a number between 0 and 1")
        return False
    
    if not isinstance(trade['pnl'], (int, float)):
        print("Error: PnL must be a number")
        return False
    
    try:
        # Create file if missing
        if not os.path.exists(TRADE_LOG_PATH):
            os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
            with open(TRADE_LOG_PATH, 'w') as f:
                json.dump([], f)

        # Try to load existing trades
        try:
            with open(TRADE_LOG_PATH, 'r') as f:
                trades = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            trades = []

        # Append new trade
        trades.append(trade)

        # Save updated log
        with open(TRADE_LOG_PATH, 'w') as f:
            json.dump(trades, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error logging trade: {e}")
        return False

def updateStrategyOutput(strategy):
    """Save strategy confidence and activation"""
    # Validate strategy data
    if not isinstance(strategy, dict):
        print("Error: Strategy must be a dictionary")
        return False
    
    required_fields = ['strategy', 'confidence', 'active']
    for field in required_fields:
        if field not in strategy:
            print(f"Error: Strategy missing required field: {field}")
            return False
    
    if not isinstance(strategy['confidence'], (int, float)) or not (0 <= strategy['confidence'] <= 100):
        print("Error: Confidence must be a number between 0 and 100")
        return False
    
    if not isinstance(strategy['active'], bool):
        print("Error: Active must be a boolean value")
        return False
    
    try:
        os.makedirs(os.path.dirname(STRATEGY_OUTPUT_PATH), exist_ok=True)
        with open(STRATEGY_OUTPUT_PATH, 'w') as f:
            json.dump(strategy, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing strategy output: {e}")
        return False

def updateHealthStatus(status):
    """Save system health status"""
    # Validate health status data
    if not isinstance(status, dict):
        print("Error: Health status must be a dictionary")
        return False
    
    required_fields = ['accuracy', 'status']
    for field in required_fields:
        if field not in status:
            print(f"Error: Health status missing required field: {field}")
            return False
    
    if not isinstance(status['accuracy'], (int, float)) or not (0 <= status['accuracy'] <= 100):
        print("Error: Accuracy must be a number between 0 and 100")
        return False
    
    valid_statuses = ['Optimal', 'Needs Review', 'Alert', 'Unknown']
    if status['status'] not in valid_statuses:
        print(f"Error: Status must be one of {valid_statuses}")
        return False
    
    try:
        os.makedirs(os.path.dirname(HEALTH_STATUS_PATH), exist_ok=True)
        with open(HEALTH_STATUS_PATH, 'w') as f:
            json.dump(status, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing health status: {e}")
        return False