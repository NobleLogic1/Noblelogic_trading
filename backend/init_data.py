# Initialize data feeds and services
import os
import json
from datetime import datetime

# Create initial data files if they don't exist
def init_data_files():
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Initialize trade log
    if not os.path.exists('trade_log.json'):
        with open('trade_log.json', 'w') as f:
            json.dump([], f)
    
    # Initialize system health status
    health_status = {
        'status': 'operational',
        'last_update': datetime.now().isoformat(),
        'components': {
            'data_feed': 'operational',
            'trade_execution': 'operational',
            'risk_management': 'operational',
            'api_connectivity': 'operational'
        }
    }
    with open('health_status.json', 'w') as f:
        json.dump(health_status, f)
    
    # Initialize strategy output
    strategy_output = {
        'active_trades': [],
        'performance_metrics': {
            'win_rate': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0
        },
        'current_positions': []
    }
    with open('strategy_output.json', 'w') as f:
        json.dump(strategy_output, f)

if __name__ == '__main__':
    init_data_files()
    print("Data files initialized successfully")