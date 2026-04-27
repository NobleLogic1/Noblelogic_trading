import requests
import time

def get_klines(symbol="BTCUSDT", interval="1m", limit=500, max_retries=3):
    """
    Fetch klines data from Binance API with error handling and retries
    """
    url = f"https://api.binance.us/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            data = response.json()
            if isinstance(data, list):
                return data
            else:
                print(f"[Data Fetch] Warning: Unexpected data format for {symbol}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"[Data Fetch] Timeout on attempt {attempt + 1} for {symbol}")
        except requests.exceptions.ConnectionError:
            print(f"[Data Fetch] Connection error on attempt {attempt + 1} for {symbol}")
        except requests.exceptions.HTTPError as e:
            print(f"[Data Fetch] HTTP error {e.response.status_code} for {symbol}")
            break  # Don't retry on HTTP errors like 404, 401, etc.
        except requests.exceptions.RequestException as e:
            print(f"[Data Fetch] Request error on attempt {attempt + 1} for {symbol}: {str(e)}")
        except ValueError as e:
            print(f"[Data Fetch] JSON decode error for {symbol}: {str(e)}")
            break
        
        if attempt < max_retries - 1:
            time.sleep(1)  # Wait 1 second before retrying
    
    print(f"[Data Fetch] Failed to fetch {symbol} after {max_retries} attempts")
    return []