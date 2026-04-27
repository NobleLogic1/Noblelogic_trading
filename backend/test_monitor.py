from flask import Flask, jsonify, send_file
import json
import threading
import time
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

# Initialize test environment
test_env = {
    'balance': 100.0,
    'positions': {},
    'order_history': [],
    'trade_history': [],
    'fees': {'maker': 0.001, 'taker': 0.001},
    'slippage': 0.001,
    'start_time': time.time(),
    'metrics': {
        'total_trades': 0,
        'successful_trades': 0,
        'failed_trades': 0,
        'profit_factor': 0,
        'max_drawdown': 0,
        'win_rate': 0,
        'average_win': 0,
        'average_loss': 0
    }
}

def update_test_metrics():
    """Update test metrics every second"""
    while True:
        # Simulate trading activity
        current_time = time.time()
        elapsed_time = current_time - test_env['start_time']
        
        # Generate test data every 30 seconds
        if int(elapsed_time) % 30 == 0:
            simulate_trade()
        
        # Generate performance report after 10 minutes
        if elapsed_time >= 600 and not hasattr(update_test_metrics, 'report_generated'):
            generate_performance_report()
            update_test_metrics.report_generated = True
        
        time.sleep(1)

def simulate_trade():
    """Simulate a trade for testing"""
    import random
    
    # 80% chance of successful trade
    success = random.random() < 0.8
    
    # Generate trade data
    trade_amount = random.uniform(5, 15)
    profit_loss = trade_amount * (random.uniform(0.01, 0.05) if success else -random.uniform(0.01, 0.03))
    
    # Update metrics
    test_env['metrics']['total_trades'] += 1
    if success:
        test_env['metrics']['successful_trades'] += 1
    else:
        test_env['metrics']['failed_trades'] += 1
    
    # Update balance
    test_env['balance'] += profit_loss
    
    # Record trade
    trade = {
        'timestamp': time.time(),
        'amount': trade_amount,
        'profit_loss': profit_loss,
        'success': success
    }
    test_env['trade_history'].append(trade)
    
    # Update win rate
    total = test_env['metrics']['total_trades']
    wins = test_env['metrics']['successful_trades']
    test_env['metrics']['win_rate'] = (wins / total) if total > 0 else 0

def generate_performance_report():
    """Generate comprehensive performance report"""
    report = {
        'summary': {
            'total_trades': test_env['metrics']['total_trades'],
            'win_rate': test_env['metrics']['win_rate'],
            'final_balance': test_env['balance'],
            'profit_loss': test_env['balance'] - 100.0  # Initial balance was 100
        },
        'improvement_suggestions': []
    }
    
    # Generate suggestions based on performance
    if test_env['metrics']['win_rate'] < 0.8:
        report['improvement_suggestions'].append({
            'priority': 'HIGH',
            'category': 'Win Rate',
            'suggestion': 'Increase prediction confidence threshold to improve accuracy'
        })
    
    if test_env['balance'] < 100:
        report['improvement_suggestions'].append({
            'priority': 'HIGH',
            'category': 'Capital Preservation',
            'suggestion': 'Implement stricter stop-loss controls'
        })
    
    # Save report
    with open('test_data/performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

@app.route('/api/test/status')
def get_status():
    """Get current test status"""
    return jsonify({
        'balance': test_env['balance'],
        'metrics': test_env['metrics'],
        'elapsed_time': time.time() - test_env['start_time'],
        'active_positions': len(test_env['positions'])
    })

@app.route('/api/test/performance')
def get_performance():
    """Get performance report"""
    if os.path.exists('test_data/performance_report.json'):
        with open('test_data/performance_report.json', 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Performance report not yet generated'})

@app.route('/')
def dashboard():
    """Serve the HTML dashboard"""
    return send_file('templates/dashboard.html')

if __name__ == '__main__':
    # Create test_data directory if it doesn't exist
    Path('test_data').mkdir(exist_ok=True)
    
    # Start metrics update thread
    threading.Thread(target=update_test_metrics, daemon=True).start()
    
    # Start Flask server
    app.run(port=3001, debug=True)