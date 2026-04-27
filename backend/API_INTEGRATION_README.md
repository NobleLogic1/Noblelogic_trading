"""
NobleLogic Trading - Binance.US API Documentation
================================================

## Enhanced API Integration Features

### 1. Rate Limiting Protection

The API client implements intelligent rate limiting to prevent account lockouts:
- Per-endpoint rate tracking with timestamps
- Automatic request throttling when approaching limits
- Progressive backoff when rate limits are hit
- Separate limits for general requests vs. order operations

### 2. Connection Pooling

Optimized HTTP connections for better performance:
- Connection reuse for faster requests
- Persistent connections to reduce overhead
- Automatic connection management
- Configurable pool sizes based on needs

### 3. Error Handling

Comprehensive error handling system:
- API error code mapping to human-readable messages
- Error tracking with pattern detection
- Diagnostics for common issues (insufficient funds, etc)
- Detailed logging for troubleshooting

### 4. System Features

Other advanced features:
- Thread-safe API calls
- Exponential backoff with jitter for retries
- Automatic timeout handling
- API weight monitoring
- Demo mode fallback

## Usage Examples

```python
# Initialize API with connection pooling and rate limiting
api = BinanceUSAPI()

# Execute a trade with enhanced error handling
result = api.execute_trade(
    symbol="BTCUSD",
    side="BUY",
    quantity=0.01,
    confidence=85.5,
    strategy="ML_Enhanced_Momentum"
)

# Get market data with rate limiting protection
market_data = api.get_market_data()
```
"""