"""
Test script for adaptive confidence thresholds in ML predictions
"""

import sys
import os
import asyncio
import time
from datetime import datetime
import json

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the required modules
from ml_integration import ml_trading_integration
from ml.adaptive_thresholds import AdaptiveThresholds

async def test_adaptive_thresholds():
    """Test the adaptive thresholds functionality"""
    print("\n===== TESTING ADAPTIVE THRESHOLDS =====\n")
    
    # Create a standalone adaptive thresholds instance
    thresholds = AdaptiveThresholds()
    
    # Test different market regimes
    market_regimes = ["BULL", "BEAR", "VOLATILE", "SIDEWAYS", "EUPHORIA", "PANIC", "RECOVERY"]
    print("\n----- Testing Different Market Regimes -----")
    
    for regime in market_regimes:
        market_data = {
            "market_regime": regime,
            "volatility": 0.02,
            "trend_strength": 0.5,
            "trend_direction": 0 if regime in ["BEAR", "PANIC"] else 1
        }
        
        thresholds_info = thresholds.get_thresholds(market_data)
        print(f"Market Regime: {regime}")
        print(f"  Buy Threshold: {thresholds_info['buy']:.2f}")
        print(f"  Sell Threshold: {thresholds_info['sell']:.2f}")
        print(f"  Hold Threshold: {thresholds_info['hold']:.2f}")
    
    # Test different volatility levels
    volatilities = [0.01, 0.03, 0.05, 0.08, 0.12]
    print("\n----- Testing Different Volatility Levels -----")
    
    for vol in volatilities:
        market_data = {
            "market_regime": "SIDEWAYS",
            "volatility": vol,
            "trend_strength": 0.5,
            "trend_direction": 0
        }
        
        thresholds_info = thresholds.get_thresholds(market_data)
        print(f"Volatility: {vol:.2f}")
        print(f"  Buy Threshold: {thresholds_info['buy']:.2f}")
        print(f"  Sell Threshold: {thresholds_info['sell']:.2f}")
    
    # Test different trend strengths
    trends = [(0.8, 1), (0.8, -1), (0.3, 1), (0.3, -1)]
    print("\n----- Testing Different Trend Strengths -----")
    
    for strength, direction in trends:
        market_data = {
            "market_regime": "SIDEWAYS",
            "volatility": 0.02,
            "trend_strength": strength,
            "trend_direction": direction
        }
        
        thresholds_info = thresholds.get_thresholds(market_data)
        trend_type = "Uptrend" if direction > 0 else "Downtrend"
        print(f"Trend: {trend_type}, Strength: {strength:.1f}")
        print(f"  Buy Threshold: {thresholds_info['buy']:.2f}")
        print(f"  Sell Threshold: {thresholds_info['sell']:.2f}")
    
    # Test recording decisions and adaptation
    print("\n----- Testing Decision Recording and Adaptation -----")
    print("Recording 50 simulated decisions...")
    
    # Record some successful trades
    for i in range(50):
        action = 1 if i % 3 != 0 else 2  # Alternate buy/sell with some holds
        success = True if i % 4 < 3 else False  # 75% success rate
        profit = 0.02 if success else -0.01  # 2% profit or 1% loss
        
        decision = {
            "action": action,
            "confidence": 0.75 + (i % 10) / 100,  # Varying confidence
            "symbol": "BTC/USD"
        }
        
        outcome = {
            "successful": success,
            "profit": profit,
            "hit_target": success,
            "hit_stop_loss": not success
        }
        
        thresholds.record_decision(decision, outcome)
        
        # Print status every 10 decisions
        if (i + 1) % 10 == 0:
            market_data = {"market_regime": "SIDEWAYS", "volatility": 0.02}
            current = thresholds.get_thresholds(market_data)
            print(f"After {i+1} decisions: Buy={current['buy']:.2f}, Sell={current['sell']:.2f}")
    
    # Test integration with trading system
    print("\n----- Testing Integration with ML Trading System -----")
    
    # Test different market scenarios
    market_scenarios = [
        {"name": "Bullish Low Vol", "regime": "BULL", "volatility": 0.01, "trend_strength": 0.7, "direction": 1},
        {"name": "Bearish High Vol", "regime": "BEAR", "volatility": 0.08, "trend_strength": 0.6, "direction": -1},
        {"name": "Sideways Mid Vol", "regime": "SIDEWAYS", "volatility": 0.03, "trend_strength": 0.2, "direction": 0},
        {"name": "Panic Mode", "regime": "PANIC", "volatility": 0.12, "trend_strength": 0.8, "direction": -1}
    ]
    
    for scenario in market_scenarios:
        # Prepare market data
        market_data = {
            "market_regime": scenario["regime"],
            "volatility": scenario["volatility"],
            "trend_strength": scenario["trend_strength"],
            "trend_direction": scenario["direction"],
            # Add additional market data required by risk assessment
            "volume": 1000,
            "liquidity_score": 0.7,
            "correlation_matrix": {"BTC/USD": {"BTC/USD": 1.0, "ETH/USD": 0.8}},
            "sentiment_score": 0.6
        }
        
        # Get trading decision
        trading_decision = await ml_trading_integration.get_trading_decision(
            "BTC/USD", 45000, market_data
        )
        
        print(f"\nScenario: {scenario['name']}")
        print(f"  Trading Decision: {trading_decision['should_trade']}")
        print(f"  Action: {trading_decision.get('action', 'HOLD')}")
        print(f"  Reason: {trading_decision['reason']}")
        print(f"  Confidence: {trading_decision.get('confidence', 0):.2%}")
        if 'adaptive_thresholds' in trading_decision:
            thresholds = trading_decision['adaptive_thresholds']['current_thresholds']
            print(f"  Thresholds: Buy={thresholds['buy']:.2f}, Sell={thresholds['sell']:.2f}, Hold={thresholds['hold']:.2f}")
    
    # Get overall ML performance stats
    performance = ml_trading_integration.get_ml_performance_stats()
    print("\n----- ML Performance Stats -----")
    print(f"Total Trades: {performance.get('total_trades', 0)}")
    print(f"Accuracy: {performance.get('accuracy', '0%')}")
    print(f"Adaptive Thresholds Active: {performance.get('adaptive_thresholds', {}).get('adaptation_active', False)}")
    
    if 'adaptive_thresholds' in performance:
        current = performance['adaptive_thresholds']['current']
        print(f"Current Thresholds: Buy={current['buy']:.2f}, Sell={current['sell']:.2f}, Hold={current['hold']:.2f}")

if __name__ == "__main__":
    asyncio.run(test_adaptive_thresholds())