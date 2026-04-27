"""
API Helper Utilities for NobleLogic Trading
==========================================
Common utilities for API rate limiting and connection management
"""

import time
from collections import deque
import threading

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_calls, period):
        """
        Initialize rate limiter
        
        Args:
            max_calls (int): Maximum number of calls allowed
            period (float): Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = threading.Lock()
    
    def __call__(self, func):
        """Decorator for rate limiting a function"""
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                
                # Remove old timestamps
                while self.calls and self.calls[0] <= now - self.period:
                    self.calls.popleft()
                
                # Check if we're over the limit
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.calls[0] - (now - self.period)
                    if sleep_time > 0:
                        print(f"⚠️ Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                        time.sleep(sleep_time)
                
                # Add current timestamp and execute
                self.calls.append(time.time())
                
            return func(*args, **kwargs)
        return wrapper

class APIRetryManager:
    """Manages API retries with exponential backoff"""
    
    def __init__(self, max_retries=3, base_delay=1.0, max_delay=10.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                retries += 1
                
                if retries <= self.max_retries:
                    delay = min(self.base_delay * (2 ** (retries - 1)), self.max_delay)
                    print(f"⚠️ Request failed (attempt {retries}/{self.max_retries}), retrying in {delay:.1f}s: {str(e)}")
                    time.sleep(delay)
        
        # If we get here, all retries failed
        raise last_exception