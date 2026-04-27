# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import random
import time
import sys
import logging
from binance_us_api import BinanceUSAPI

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'backend.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load API keys from config/secure/APIkeys.txt
def load_api_keys():
    api_key = None
    api_secret = None
    try:
        with open(os.path.join(os.path.dirname(__file__), '../config/secure/APIkeys.txt'), 'r') as f:
            for line in f:
                if line.startswith('BINANCE_US_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                elif line.startswith('BINANCE_US_API_SECRET='):
                    api_secret = line.strip().split('=', 1)[1]
    except Exception as e:
        print(f"Error loading API keys: {e}")
    return api_key, api_secret

print("Starting server.py...")
print(f"Current directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(__file__)}")

# Make sure the current directory is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = Flask(__name__)
CORS(app)  #  Enables cross-origin requests from frontend

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# File paths
HEALTH_STATUS_PATH = os.path.join(BASE_DIR, '..', 'data', 'system_health_report.json')
GPU_AVAILABLE = False # Placeholder, will be determined by another script

@app.route('/api/health')
def get_health():
    """Provides a health check and basic system status."""
    # In a real scenario, you might load this from a file or a monitoring service
    health_data = {
        'status': 'operational',
        'timestamp': time.time(),
        'gpu_status': 'CUDA Available' if GPU_AVAILABLE else 'CPU Only',
        'gpu_acceleration': GPU_AVAILABLE
    }
    return jsonify(health_data)

#@app.route('/api/health')
#def get_health():
#    health_data = load_json(HEALTH_STATUS_PATH)
#    if isinstance(health_data, dict):
#        health_data['gpu_acceleration'] = GPU_AVAILABLE
#        health_data['gpu_status'] = 'CUDA Available' if GPU_AVAILABLE else 'CPU Only'
#    else:
#        health_data = {
#            'status': 'operational',
#            'gpu_acceleration'] = GPU_AVAILABLE
#            'gpu_status'] = 'CUDA Available' if GPU_AVAILABLE else 'CPU Only'
#        }
#    return jsonify(health_data)

# Chart data route for GPU rendering
@app.route('/api/chart-data')
def get_chart_data():
    """Generate sample chart data for GPU rendering"""
    data = []
    base_price = 50000
    for i in range(100):
        timestamp = int(time.time() * 1000) - (99 - i) * 60000  # 1 minute intervals
        price = base_price + random.uniform(-5000, 5000) + (i * 10)  # Trending upward
        data.append({
            'timestamp': timestamp,
            'price': round(price, 2),
            'volume': random.uniform(1000000, 10000000)
        })
    return jsonify({'data': data})

# Binance.US Account Balance endpoint
@app.route('/api/balance')
def get_balance():
    """Get real Binance.US account balance information"""
    try:
        logging.info("Attempting to fetch balance in live mode.")
        # Use the already imported BinanceUSAPI class
        api = BinanceUSAPI(live_mode=True)
        balance = api.get_account_balance()
        
        if not balance:
            logging.error("Balance endpoint returned no data or an error structure.")
            return jsonify({'error': 'Unable to fetch live balance'}), 500
        
        # Return the balance data directly since it's already in the correct format
        logging.info(f"Balance endpoint returning data with {len(balance)} assets.")
        return jsonify(balance)
    except Exception as e:
        logging.error(f"Error in balance endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f'Unable to fetch balance: {str(e)}'}), 500

# Enhanced trades endpoint with detailed tracking
@app.route('/api/trades')
def get_detailed_trades():
    """Get real trade information from Binance.US for all relevant symbols."""
    try:
        api = BinanceUSAPI(live_mode=True)
        
        # Get all non-zero balance assets to find relevant trade pairs
        balance = api.get_account_balance()
        if not balance or 'error' in balance:
            logging.warning("Could not retrieve balance to determine trade pairs.")
            return jsonify([])

        # Create a list of symbols to check, e.g., BTCUSDT, ETHUSDT
        assets = [item['asset'] for item in balance if item['asset'] not in ['USD', 'USDT']]
        symbols_to_check = [f"{asset}USDT" for asset in assets]
        
        # Always include a default or popular symbol
        if 'BTCUSDT' not in symbols_to_check:
            symbols_to_check.append('BTCUSDT')

        all_trades = []
        for symbol in symbols_to_check:
            trades = api.get_recent_trades(symbol=symbol)
            if trades:
                all_trades.extend(trades)
        
        # Sort trades by time, most recent first
        all_trades.sort(key=lambda x: x.get('time', 0), reverse=True)

        if all_trades:
            return jsonify(all_trades)
        else:
            logging.info("No recent trades found for any relevant symbols.")
            return jsonify([])
            
    except Exception as e:
        logging.error(f"Error in trades endpoint: {str(e)}", exc_info=True)
        return jsonify([]), 200

# Trading control endpoint
@app.route('/api/trading/control/<string:action>', methods=['POST'])
def control_trading(action):
    """Start or stop automated trading"""
    try:
        api = BinanceUSAPI(live_mode=True)
        
        if action.lower() == 'start':
            result = api.start_trading()
            return jsonify({
                "status": "success", 
                "message": "Trading started", 
                "trading_active": True,
                "timestamp": int(time.time() * 1000)
            })
        elif action.lower() == 'stop':
            result = api.stop_trading()
            return jsonify({
                "status": "success", 
                "message": "Trading stopped", 
                "trading_active": False,
                "timestamp": int(time.time() * 1000)
            })
        else:
            return jsonify({"status": "error", "message": "Invalid action. Use 'start' or 'stop'"}), 400
    except Exception as e:
        logging.error(f"Error controlling trading: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

# Trading status endpoint
@app.route('/api/trading/status')
def trading_status():
    """Get current trading status"""
    try:
        api = BinanceUSAPI(live_mode=True)
        status = api.get_trading_status()
        return jsonify(status)
    except Exception as e:
        logging.error(f"Error getting trading status: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": str(e),
            "trading_active": False
        }), 500

@app.route('/api/tickers')
def get_tickers():
    """Get all 24hr ticker price change statistics."""
    try:
        api = BinanceUSAPI(live_mode=True)
        tickers = api.get_all_tickers()
        if tickers:
            # The API returns a list of dictionaries. We can pass it directly.
            return jsonify(tickers)
        else:
            logging.warning("Ticker endpoint requested but API returned no data.")
            return jsonify([]), 200
    except Exception as e:
        logging.error(f"Error in tickers endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f'Unable to fetch tickers: {str(e)}'}), 500

# AutoTrade endpoint (matches frontend component)
@app.route('/api/autotrade', methods=['GET', 'POST'])
def autotrade():
    """Get or set autotrading status"""
    api = BinanceUSAPI(live_mode=True)
    if request.method == 'POST':
        try:
            data = request.get_json()
            enabled = data.get('enabled', False)
            if enabled:
                result = api.start_trading()
            else:
                result = api.stop_trading()
            return jsonify({
                "success": True,
                "enabled": enabled,
                "message": "AutoTrading " + ("started" if enabled else "stopped")
            })
        except Exception as e:
            logging.error(f"Error setting autotrade status: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
    else:
        # GET request - return current status
        status = api.get_trading_status()
        return jsonify({
            "enabled": status.get("trading_active", False),
            "demo_mode": status.get("demo_mode", True),
            "success": True
        })

# Trade execution endpoint
@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a real or demo trade"""
    try:
        # Get trade parameters from request
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Missing trade data"}), 400
        
        # Extract required parameters
        symbol = data.get('symbol')
        side = data.get('side')  # 'BUY' or 'SELL'
        quantity = data.get('quantity')
        price = data.get('price')  # Optional for market orders
        order_type = data.get('type', 'MARKET')
        live_mode = data.get('live_mode', False)
        
        # Validate required parameters
        if not symbol or not side or not quantity:
            return jsonify({
                "success": False,
                "message": "Missing required parameters: symbol, side, quantity"
            }), 400
            
        # Validate side
        if side not in ['BUY', 'SELL']:
            return jsonify({"success": False, "message": "Side must be 'BUY' or 'SELL'"}), 400
        
        # Initialize API with live_mode flag
        api = BinanceUSAPI(live_mode=True)
        
        # Execute the trade
        result = api.execute_trade(symbol, side, float(quantity), price, order_type)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"{side} order placed successfully",
                "order": result,
                "demo_mode": api.demo_mode
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to execute trade"
            }), 500
            
    except Exception as e:
        logging.error(f"Error executing trade: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# Get market price endpoint
@app.route('/api/market-price/<string:symbol>')
def get_market_price(symbol):
    """Get current market price for a symbol"""
    try:
        api = BinanceUSAPI(live_mode=True)
        price = api._get_current_price(symbol)
        
        if price:
            return jsonify({
                "success": True,
                "symbol": symbol,
                "price": price,
                "timestamp": int(time.time() * 1000)
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Could not get price for {symbol}"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    logging.info("Flask server starting.")
    app.run(host='0.0.0.0', port=3001, threaded=True, debug=True)
