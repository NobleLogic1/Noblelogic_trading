import json
import os

# Paths to JSON files
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRADE_LOG_PATH = os.path.join(BASE_DIR, 'trade_log.json')
STRATEGY_OUTPUT_PATH = os.path.join(BASE_DIR, 'strategy_output.json')
HEALTH_STATUS_PATH = os.path.join(BASE_DIR, 'health_status.json')

# Append a trade to the log
def logTrade(trade):
    # Create file if missing
    if not os.path.exists(TRADE_LOG_PATH):
        with open(TRADE_LOG_PATH, 'w') as f:
            json.dump([], f)

    # Try to load existing trades
    try:
        with open(TRADE_LOG_PATH, 'r') as f:
            trades = json.load(f)
    except json.JSONDecodeError:
        trades = []

    # Append new trade
    trades.append(trade)

    # Save updated log
    with open(TRADE_LOG_PATH, 'w') as f:
        json.dump(trades, f, indent=2)

# Save strategy confidence and activation
def updateStrategyOutput(strategies):
    try:
        with open(STRATEGY_OUTPUT_PATH, 'w') as f:
            json.dump(strategies, f, indent=2)
    except Exception as e:
        print(f"Error writing strategy output: {e}")

# Save system health status
def updateHealthStatus(status):
    try:
        with open(HEALTH_STATUS_PATH, 'w') as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        print(f"Error writing health status: {e}")