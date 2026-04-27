#!/usr/bin/env python3
"""
Test script for RL integration in ML trading system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ml_integration import MLTradingIntegration
from datetime import datetime
import random

async def test_rl_integration():
    """Test RL integration with sample market data"""
    print("🧪 Testing RL Integration...")

    # Test DQN RL method
    print("\n1. Testing DQN RL method...")
    rl_integration = MLTradingIntegration(ml_method='rl_dqn')

    # Create sample market data
    market_data_history = []
    base_price = 45000.0

    for i in range(100):
        price_change = random.uniform(-0.02, 0.02)  # -2% to +2% change
        price = base_price * (1 + price_change)
        base_price = price

        market_data = {
            'price': price,
            'price_change': price_change,
            'volume': random.uniform(100000, 1000000),
            'volatility': random.uniform(0.01, 0.05),
            'trend_strength': random.uniform(0.1, 0.9),
            'trend_direction': random.choice([-1, 0, 1]),
            'rsi': random.uniform(20, 80),
            'macd': random.uniform(-100, 100),
            'macd_signal': random.uniform(-100, 100),
            'sentiment_score': random.uniform(0, 1),
            'news_score': random.uniform(0, 1),
            'current_drawdown': random.uniform(0, 0.1),
            'sharpe_ratio': random.uniform(0.5, 2.0)
        }
        market_data_history.append(market_data)

    # Test training
    print("   Training DQN agent...")
    train_result = await rl_integration.train_rl_agent(market_data_history, episodes=5)
    print(f"   Training result: {train_result}")

    # Test decision making
    print("   Testing decision making...")
    current_market_data = market_data_history[-1]
    decision = await rl_integration.get_trading_decision(
        'BTCUSDT',
        current_market_data['price'],
        current_market_data
    )
    print(f"   Decision: {decision}")

    # Test Q-learning method
    print("\n2. Testing Q-learning RL method...")
    qlearning_integration = MLTradingIntegration(ml_method='rl_qlearning')

    # Test training
    print("   Training Q-learning agent...")
    train_result = await qlearning_integration.train_rl_agent(market_data_history, episodes=5)
    print(f"   Training result: {train_result}")

    # Test decision making
    print("   Testing decision making...")
    decision = await qlearning_integration.get_trading_decision(
        'BTCUSDT',
        current_market_data['price'],
        current_market_data
    )
    print(f"   Decision: {decision}")

    # Test trade result recording
    print("\n3. Testing trade result recording...")
    if 'prediction_id' in decision:
        prediction_id = decision['prediction_id']
        trade_result = {
            'profit': random.uniform(-100, 200),  # Random profit/loss
            'hit_target': random.choice([True, False]),
            'hit_stop_loss': random.choice([True, False])
        }

        await rl_integration.record_trade_result(prediction_id, trade_result)
        print(f"   Recorded trade result for prediction {prediction_id}")

    # Test performance stats
    print("\n4. Testing performance statistics...")
    stats = rl_integration.get_ml_performance_stats()
    print(f"   Performance stats: {stats}")

    print("\n✅ RL Integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_rl_integration())