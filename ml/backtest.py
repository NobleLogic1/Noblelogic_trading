import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from datetime import datetime
from shared_utils import logTrade

coins = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP']
strategies = ['Momentum', 'Mean Reversion', 'Breakout']

for i in range(5):
    trade = {
        'id': i + 1,
        'coin': random.choice(coins),
        'status': random.choice(['Open', 'Closed', 'Pending']),
        'confidence': round(random.uniform(0.5, 0.95), 2),
        'strategy': random.choice(strategies),
        'direction': random.choice(['Long', 'Short']),
        'pnl': round(random.uniform(-50, 150), 2),
        'signal': random.choice(['Buy', 'Sell']),
        'timestamp': datetime.now().isoformat()
    }
    logTrade(trade)

