"""
Live Data Fetcher for NobleLogic Trading System
Fetches real-time cryptocurrency data from multiple sources
"""

import requests
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LiveDataFetcher:
    def __init__(self):
        self.binance_base_url = "https://api.binance.us/api/v3"  # Updated to use Binance.US
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_duration = 60  # Cache data for 60 seconds
        
        # CoinGecko symbol mapping
        self.coingecko_symbols = {
            'BTC/USDT': 'bitcoin',
            'ETH/USDT': 'ethereum',
            'BNB/USDT': 'binancecoin',
            'ADA/USDT': 'cardano',
            'SOL/USDT': 'solana',
            'DOGE/USDT': 'dogecoin',
            'DOT/USDT': 'polkadot',
            'LINK/USDT': 'chainlink'
        }
        
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol from CoinGecko (fallback to Binance)
        """
        # Try CoinGecko first (more reliable)
        coingecko_id = self.coingecko_symbols.get(symbol)
        if coingecko_id:
            try:
                url = f"{self.coingecko_base_url}/simple/price"
                params = {
                    "ids": coingecko_id,
                    "vs_currencies": "usd"
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if coingecko_id in data and 'usd' in data[coingecko_id]:
                    return float(data[coingecko_id]['usd'])
                    
            except Exception as e:
                print(f"[Live Data] CoinGecko error for {symbol}: {e}")
        
        # Fallback to Binance
        binance_symbol = symbol.replace('/', '')
        try:
            url = f"{self.binance_base_url}/ticker/price"
            params = {"symbol": binance_symbol}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return float(data['price'])
            
        except Exception as e:
            print(f"[Live Data] Binance error for {symbol}: {e}")
            return self._get_fallback_price(symbol)
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple symbols efficiently using CoinGecko
        """
        prices = {}
        
        # Prepare CoinGecko request for multiple symbols
        coingecko_ids = []
        symbol_to_id_map = {}
        
        for symbol in symbols:
            coingecko_id = self.coingecko_symbols.get(symbol)
            if coingecko_id:
                coingecko_ids.append(coingecko_id)
                symbol_to_id_map[coingecko_id] = symbol
        
        if coingecko_ids:
            try:
                url = f"{self.coingecko_base_url}/simple/price"
                params = {
                    "ids": ",".join(coingecko_ids),
                    "vs_currencies": "usd"
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                for coingecko_id, symbol in symbol_to_id_map.items():
                    if coingecko_id in data and 'usd' in data[coingecko_id]:
                        prices[symbol] = float(data[coingecko_id]['usd'])
                
            except Exception as e:
                print(f"[Live Data] CoinGecko bulk fetch error: {e}")
        
        # Fill in any missing prices with fallbacks
        for symbol in symbols:
            if symbol not in prices:
                prices[symbol] = self.get_current_price(symbol)
        
        return prices
    
    def get_kline_data(self, symbol: str, interval: str = "1m", limit: int = 100) -> List[Dict]:
        """
        Get recent kline/candlestick data for technical analysis
        """
        binance_symbol = symbol.replace('/', '')
        cache_key = f"{symbol}_{interval}_{limit}"
        
        # Check cache first
        if self._is_cached_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.binance_base_url}/klines"
            params = {
                "symbol": binance_symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Convert to more readable format
            klines = []
            for kline in raw_data:
                klines.append({
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': kline[6],
                    'quote_volume': float(kline[7]),
                    'trades': kline[8],
                    'taker_buy_base_volume': float(kline[9]),
                    'taker_buy_quote_volume': float(kline[10])
                })
            
            # Cache the result
            self.cache[cache_key] = {
                'data': klines,
                'timestamp': time.time()
            }
            
            return klines
            
        except Exception as e:
            print(f"[Live Data] Error fetching klines for {symbol}: {e}")
            return self._get_fallback_klines(symbol)
    
    def get_24h_stats(self, symbol: str) -> Dict:
        """
        Get 24-hour price change statistics
        """
        binance_symbol = symbol.replace('/', '')
        
        try:
            url = f"{self.binance_base_url}/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'volume': float(data['volume']),
                'count': int(data['count'])
            }
            
        except Exception as e:
            print(f"[Live Data] Error fetching 24h stats for {symbol}: {e}")
            return self._get_fallback_stats(symbol)
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get current order book data
        """
        binance_symbol = symbol.replace('/', '')
        
        try:
            url = f"{self.binance_base_url}/depth"
            params = {
                "symbol": binance_symbol,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'bids': [[float(bid[0]), float(bid[1])] for bid in data['bids']],
                'asks': [[float(ask[0]), float(ask[1])] for ask in data['asks']],
                'last_update_id': data['lastUpdateId']
            }
            
        except Exception as e:
            print(f"[Live Data] Error fetching order book for {symbol}: {e}")
            return {'bids': [], 'asks': [], 'last_update_id': 0}
    
    def get_market_summary(self, symbols: List[str]) -> Dict:
        """
        Get comprehensive market data for multiple symbols
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'symbols': {}
        }
        
        # Get current prices
        prices = self.get_multiple_prices(symbols)
        
        for symbol in symbols:
            try:
                # Get 24h stats
                stats = self.get_24h_stats(symbol)
                
                # Get recent klines for trend analysis
                klines = self.get_kline_data(symbol, "5m", 12)  # Last hour of 5-min data
                
                summary['symbols'][symbol] = {
                    'current_price': prices.get(symbol, 0),
                    'price_change_24h': stats.get('price_change_percent', 0),
                    'volume_24h': stats.get('volume', 0),
                    'high_24h': stats.get('high_price', 0),
                    'low_24h': stats.get('low_price', 0),
                    'recent_trend': self._calculate_trend(klines),
                    'volatility': self._calculate_volatility(klines)
                }
                
            except Exception as e:
                print(f"[Live Data] Error getting summary for {symbol}: {e}")
                summary['symbols'][symbol] = {
                    'current_price': prices.get(symbol, 0),
                    'price_change_24h': 0,
                    'volume_24h': 0,
                    'high_24h': 0,
                    'low_24h': 0,
                    'recent_trend': 'neutral',
                    'volatility': 0
                }
        
        return summary
    
    def _is_cached_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        return time.time() - self.cache[key]['timestamp'] < self.cache_duration
    
    def _get_fallback_price(self, symbol: str) -> float:
        """Get fallback price when API fails"""
        fallback_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 3200,
            'BNB/USDT': 320,
            'ADA/USDT': 1.20,
            'SOL/USDT': 85,
            'DOGE/USDT': 0.08,
            'DOT/USDT': 25,
            'LINK/USDT': 18
        }
        return fallback_prices.get(symbol, 100)
    
    def _get_fallback_klines(self, symbol: str) -> List[Dict]:
        """Generate fallback kline data"""
        base_price = self._get_fallback_price(symbol)
        klines = []
        
        for i in range(100):
            timestamp = int(time.time() * 1000) - (i * 60000)  # 1 minute intervals
            price_variation = base_price * 0.01 * (random.random() - 0.5)
            
            klines.append({
                'timestamp': timestamp,
                'open': base_price + price_variation,
                'high': base_price + abs(price_variation),
                'low': base_price - abs(price_variation),
                'close': base_price + price_variation * 0.5,
                'volume': random.uniform(1000, 10000)
            })
        
        return klines
    
    def _get_fallback_stats(self, symbol: str) -> Dict:
        """Generate fallback 24h stats"""
        return {
            'price_change': 0,
            'price_change_percent': random.uniform(-5, 5),
            'high_price': self._get_fallback_price(symbol) * 1.05,
            'low_price': self._get_fallback_price(symbol) * 0.95,
            'volume': random.uniform(100000, 1000000),
            'count': random.randint(50000, 200000)
        }
    
    def _calculate_trend(self, klines: List[Dict]) -> str:
        """Calculate recent price trend from kline data"""
        if len(klines) < 2:
            return 'neutral'
        
        recent_prices = [k['close'] for k in klines[-5:]]
        if len(recent_prices) < 2:
            return 'neutral'
        
        trend_score = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        if trend_score > 0.005:  # > 0.5% increase
            return 'bullish'
        elif trend_score < -0.005:  # > 0.5% decrease
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_volatility(self, klines: List[Dict]) -> float:
        """Calculate price volatility from kline data"""
        if len(klines) < 2:
            return 0
        
        prices = [k['close'] for k in klines]
        price_changes = []
        
        for i in range(1, len(prices)):
            change = abs(prices[i] - prices[i-1]) / prices[i-1]
            price_changes.append(change)
        
        if not price_changes:
            return 0
        
        return sum(price_changes) / len(price_changes)

# Create global instance
live_data_fetcher = LiveDataFetcher()