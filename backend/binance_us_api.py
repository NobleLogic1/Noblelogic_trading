import requests
import hmac
import hashlib
import time
import json
from datetime import datetime
import logging
import os

class BinanceUSAPI:
    def __init__(self, live_mode=False):
        # Your API credentials (replace with actual values)
        self.api_key = None
        self.api_secret = None
        self.base_url = "https://api.binance.us"
        self.demo_mode = not live_mode  # Demo mode when not in live mode
        self.trading_active = False  # Trading starts inactive
        
        # Load API keys from file if available
        api_key_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'secure', 'APIkeys.txt')
        
        if os.path.exists(api_key_file):
            try:
                with open(api_key_file, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('BINANCE_US_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip()
                            logging.info("Found Binance.US API Key.")
                        elif line.startswith('BINANCE_US_SECRET_KEY='):
                            self.api_secret = line.split('=', 1)[1].strip()
                            logging.info("Found Binance.US API Secret.")
                            
                if self.api_key and self.api_secret and not live_mode:
                    logging.info("API keys loaded, but running in demo mode.")
                elif self.api_key and self.api_secret:
                    logging.info("API keys loaded for live trading mode.")
                else:
                    logging.warning("API keys not found in file.")
                    
            except Exception as e:
                logging.error(f"Error loading API keys: {e}")
        else:
            logging.warning(f"API key file not found: {api_key_file}")

    def _generate_signature(self, data):
        return hmac.new(self.api_secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()

    def _make_request(self, method, endpoint, params=None, signed=False):
        if params is None:
            params = {}
        
        headers = {'X-MBX-APIKEY': self.api_key} if self.api_key else {}
        url = f"{self.base_url}{endpoint}"

        if signed:
            if not self.api_key or not self.api_secret:
                logging.error(f"Cannot make signed request to {endpoint}, API keys are missing.")
                return None
            
            params['timestamp'] = int(time.time() * 1000)
            
            # The query string for the signature MUST be sorted.
            query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
            signature = self._generate_signature(query_string)
            
            # For GET requests, all parameters (including signature) go in the URL.
            if method == 'GET':
                url = f"{url}?{query_string}&signature={signature}"
                params = None # Params are now in the URL, so we don't pass them to requests library separately.
            # For POST, parameters go in the body.
            elif method == 'POST':
                params['signature'] = signature

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=params, timeout=10)
            else:
                logging.error(f"Unsupported request method: {method}")
                return None

            if response.status_code == 200:
                return response.json()
            else:
                # Log the exact URL for debugging to see what was sent.
                full_url = response.request.url
                logging.error(f"API Error for {method} {full_url}: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {method} {url}: {e}", exc_info=True)
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred in _make_request: {e}", exc_info=True)
            return None

    def get_account_balance(self):
        """Get account balance information"""
        if not self.api_key or not self.api_secret:
            logging.error("Cannot get balance, API keys are not available.")
            return {"error": "API keys not loaded"}

        endpoint = '/api/v3/account'
        params = {}
        logging.info(f"Making request to {self.base_url}{endpoint}")
        result = self._make_request('GET', endpoint, params, signed=True)

        if result and 'balances' in result:
            # Filter out zero balances and format
            balances = []
            for balance in result['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    balances.append({
                        'asset': balance['asset'],
                        'free': balance['free'],
                        'locked': balance['locked']
                    })
            logging.info(f"Found {len(balances)} assets with non-zero balance.")
            return balances
        elif result:
            logging.warning(f"Account balance response received, but 'balances' key missing. Response: {result}")
            return []
        else:
            logging.error("Failed to get account balance. The request returned None.")
            return []

    def get_all_tickers(self):
        """Get 24hr ticker price change statistics for all symbols."""
        endpoint = '/api/v3/ticker/24hr'
        logging.info(f"Making request to {self.base_url}{endpoint}")
        result = self._make_request('GET', endpoint)
        if result:
            logging.info(f"Successfully fetched data for {len(result)} tickers.")
        else:
            logging.error("Failed to get ticker data. The request returned None.")
        return result

    def get_recent_trades(self, symbol='BTCUSDT'):
        """Get recent trades for a specific symbol"""
        if not self.api_key or not self.api_secret:
            logging.error("Cannot get trades, API keys are not available.")
            return []

        endpoint = '/api/v3/myTrades'
        params = {'symbol': symbol, 'limit': 20} # Increased limit
        logging.info(f"Making request to {self.base_url}{endpoint} for symbol {symbol}")
        result = self._make_request('GET', endpoint, params, signed=True)

        if result:
            trades = []
            for trade in result:
                trades.append({
                    'id': trade.get('id'),
                    'orderId': trade.get('orderId'),
                    'symbol': trade.get('symbol'),
                    'price': trade.get('price'),
                    'qty': trade.get('qty'),
                    'time': trade.get('time'),
                    'isBuyer': trade.get('isBuyer', False)
                })
            logging.info(f"Found {len(trades)} recent trades for {symbol}.")
            return trades
        else:
            logging.error(f"Failed to get recent trades for {symbol}. The request returned None or an error.")
            return []

    def start_trading(self):
        """Start trading"""
        self.trading_active = True
        logging.info("Trading started - system now active")
        return True

    def stop_trading(self):
        """Stop trading"""
        self.trading_active = False
        logging.info("Trading stopped - system now inactive")
        return True

    def get_trading_status(self):
        """Get trading status"""
        return {
            "trading_active": self.trading_active,
            "demo_mode": self.demo_mode,
            "timestamp": int(time.time() * 1000),
            "api_configured": bool(self.api_key and self.api_secret)
        }

    def execute_trade(self, symbol, side, quantity, price=None, order_type='MARKET'):
        """Execute a trade"""
        if not self.trading_active:
            return {
                'error': 'Trading is not active. Enable trading first.',
                'status': 'FAILED'
            }
            
        if self.demo_mode:
            # Demo mode - simulate trade
            trade_result = {
                'symbol': symbol,
                'orderId': int(time.time() * 1000),
                'status': 'FILLED',
                'side': side,
                'type': order_type,
                'origQty': str(quantity),
                'price': price or '0',
                'time': int(time.time() * 1000),
                'demo_mode': True
            }
            logging.info(f"Demo trade executed: {side} {quantity} {symbol} @ {price or 'market'}")
            return trade_result
        else:
            # Live mode - would make real API call
            if self.api_key and self.api_secret:
                # Placeholder for real API call
                logging.info(f"Live trade would execute: {side} {quantity} {symbol}")
                return {
                    'error': 'Live trading API not fully implemented',
                    'status': 'PENDING',
                    'note': 'Real API integration needed'
                }
            else:
                return {
                    'error': 'API keys not configured for live trading',
                    'status': 'FAILED'
                }
            return None

    def _get_current_price(self, symbol):
        """Get current market price for a symbol"""
        endpoint = '/api/v3/ticker/price'
        params = {'symbol': symbol}
        result = self._make_request('GET', endpoint, params)

        if result and 'price' in result:
            return result['price']
        return None