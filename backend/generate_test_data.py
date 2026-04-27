# Generate test data for development
import json
import random
from datetime import datetime, timedelta

def generate_test_data():
    # Generate sample active trades
    active_trades = [
        {
            'id': f'trade_{i}',
            'symbol': random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT']),
            'type': random.choice(['LONG', 'SHORT']),
            'entry_price': round(random.uniform(20000, 60000), 2),
            'current_price': round(random.uniform(20000, 60000), 2),
            'size': round(random.uniform(0.1, 2.0), 3),
            'pnl': round(random.uniform(-1000, 1000), 2),
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        } for i in range(5)
    ]
    with open('trade_log.json', 'w') as f:
        json.dump(active_trades, f, indent=2)

    # Generate system health data
    health_status = {
        'status': 'operational',
        'last_update': datetime.now().isoformat(),
        'components': {
            'data_feed': random.choice(['operational', 'degraded']),
            'trade_execution': random.choice(['operational', 'degraded']),
            'risk_management': random.choice(['operational', 'degraded']),
            'api_connectivity': random.choice(['operational', 'degraded'])
        },
        'metrics': {
            'latency': round(random.uniform(50, 200), 2),
            'success_rate': round(random.uniform(95, 100), 2),
            'error_rate': round(random.uniform(0, 5), 2)
        }
    }
    with open('health_status.json', 'w') as f:
        json.dump(health_status, f, indent=2)

    # Generate strategy performance data
    strategy_data = {
        'performance': [
            {
                'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
                'pnl': round(random.uniform(-1000, 1000), 2),
                'win_rate': round(random.uniform(40, 70), 2),
                'sharpe_ratio': round(random.uniform(1, 3), 2)
            } for i in range(30)
        ],
        'insights': [
            {
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'symbol': random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT']),
                'signal': random.choice(['BUY', 'SELL']),
                'confidence': round(random.uniform(0.5, 0.95), 2),
                'reason': random.choice([
                    'Strong trend continuation',
                    'Support level bounce',
                    'Resistance breakout',
                    'Volume spike'
                ])
            } for i in range(10)
        ]
    }
    with open('strategy_output.json', 'w') as f:
        json.dump(strategy_data, f, indent=2)

if __name__ == '__main__':
    generate_test_data()
    print("Test data generated successfully")