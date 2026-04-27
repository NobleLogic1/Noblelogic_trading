"""
Binance.US API Configuration Test
Test the updated API endpoints to ensure only Binance.US is used
"""

import requests
import sys
sys.path.append('.')

from live_data_fetcher import LiveDataFetcher

def test_binance_us_api():
    """Test Binance.US API configuration"""
    print("[API TEST] Testing Binance.US Configuration")
    print("=" * 50)
    
    # Initialize data fetcher
    fetcher = LiveDataFetcher()
    
    # Check API endpoints
    print(f"[CONFIG] Binance Base URL: {fetcher.binance_base_url}")
    
    if "binance.us" in fetcher.binance_base_url:
        print("[OK] Using Binance.US API endpoint")
    elif "binance.com" in fetcher.binance_base_url:
        print("[WARNING] Still using global Binance API - needs update")
    else:
        print("[ERROR] Unknown Binance API endpoint")
    
    # Test API connectivity
    print("\n[TEST] Testing API connectivity...")
    
    test_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    
    for symbol in test_symbols:
        try:
            print(f"[TESTING] {symbol}")
            price = fetcher.get_current_price(symbol)
            
            if price and price > 0:
                print(f"  [OK] Price: ${price:,.2f}")
            else:
                print(f"  [FAIL] No price data received")
                
        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}")
    
    # Test direct Binance.US API call
    print("\n[DIRECT] Testing direct Binance.US API call...")
    try:
        url = "https://api.binance.us/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            print(f"[OK] Direct Binance.US API: BTC Price = ${price:,.2f}")
        else:
            print(f"[FAIL] Direct API call failed: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Direct API test failed: {e}")
    
    print("\n[SUMMARY] Binance.US API Configuration Test Complete")
    print("=" * 50)

def test_ml_config():
    """Test ML configuration for Binance.US"""
    try:
        import sys
        sys.path.append('ml')
        from config import CONFIG
        
        print(f"\n[ML CONFIG] Binance URL: {CONFIG['binance_base_url']}")
        
        if "binance.us" in CONFIG['binance_base_url']:
            print("[OK] ML module configured for Binance.US")
        else:
            print("[WARNING] ML module not configured for Binance.US")
            
    except Exception as e:
        print(f"[ERROR] Could not check ML config: {e}")

if __name__ == "__main__":
    test_binance_us_api()
    test_ml_config()