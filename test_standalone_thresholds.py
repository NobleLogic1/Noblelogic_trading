"""
Standalone test for adaptive thresholds without ML model dependencies
"""

import os
import time
from datetime import datetime
import json
import random
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the AdaptiveThresholds class
from ml.adaptive_thresholds import AdaptiveThresholds

def test_adaptive_thresholds():
    """Test the adaptive thresholds functionality independently"""
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
    print("Recording 100 simulated decisions with varying success rates...")
    
    # Record some successful trades
    for i in range(100):
        action = i % 3  # Cycle through hold (0), buy (1), sell (2)
        
        # Vary success rate by action
        if action == 0:  # Hold
            success = random.random() > 0.3  # 70% success rate for hold
        elif action == 1:  # Buy
            success = random.random() > 0.4  # 60% success rate for buy
        else:  # Sell
            success = random.random() > 0.5  # 50% success rate for sell
            
        profit = random.uniform(0.01, 0.05) if success else random.uniform(-0.05, -0.01)
        
        decision = {
            "action": action,
            "confidence": 0.65 + (random.random() * 0.2),  # Between 0.65-0.85
            "symbol": "BTC/USD" 
        }
        
        outcome = {
            "successful": success,
            "profit": profit,
            "hit_target": success,
            "hit_stop_loss": not success
        }
        
        thresholds.record_decision(decision, outcome)
        
        # Print status periodically
        if (i + 1) % 20 == 0:
            market_data = {"market_regime": "SIDEWAYS", "volatility": 0.02}
            current = thresholds.get_thresholds(market_data)
            print(f"After {i+1} decisions: Buy={current['buy']:.2f}, Sell={current['sell']:.2f}, Hold={current['hold']:.2f}")
    
    # Test confidence checking in different scenarios
    print("\n----- Testing Confidence Checking -----")
    
    test_scenarios = [
        {"name": "Moderate Buy", "action": 1, "confidence": 0.70, "regime": "BULL", "volatility": 0.02},
        {"name": "High Buy", "action": 1, "confidence": 0.85, "regime": "BULL", "volatility": 0.02},
        {"name": "Low Buy", "action": 1, "confidence": 0.60, "regime": "BULL", "volatility": 0.02},
        {"name": "Moderate Sell", "action": 2, "confidence": 0.75, "regime": "BEAR", "volatility": 0.02},
        {"name": "High Vol Buy", "action": 1, "confidence": 0.70, "regime": "VOLATILE", "volatility": 0.08},
        {"name": "Low Vol Sell", "action": 2, "confidence": 0.70, "regime": "SIDEWAYS", "volatility": 0.01},
    ]
    
    for scenario in test_scenarios:
        market_data = {
            "market_regime": scenario["regime"],
            "volatility": scenario["volatility"],
            "trend_strength": 0.5,
            "trend_direction": 1 if scenario["regime"] == "BULL" else -1 if scenario["regime"] == "BEAR" else 0
        }
        
        result = thresholds.check_confidence(
            scenario["action"], 
            scenario["confidence"], 
            market_data
        )
        
        action_name = {0: "Hold", 1: "Buy", 2: "Sell"}.get(scenario["action"])
        print(f"Scenario: {scenario['name']}")
        print(f"  {action_name} with {scenario['confidence']:.2%} confidence in {scenario['regime']} market")
        print(f"  Meets threshold: {result}")
    
    # Get threshold info
    print("\n----- Threshold Information -----")
    market_data = {"market_regime": "SIDEWAYS", "volatility": 0.02}
    threshold_info = thresholds.get_threshold_info(market_data)
    
    print("Current Thresholds:")
    for action, value in threshold_info['current_thresholds'].items():
        print(f"  {action.capitalize()}: {value:.2f}")
        
    print("\nBase Thresholds:")
    for action, value in threshold_info['base_thresholds'].items():
        print(f"  {action.capitalize()}: {value:.2f}")
    
    print(f"\nAdaptation Active: {threshold_info['adaptation_active']}")
    print(f"Market Regime: {threshold_info['market_regime']}")
    
    if 'success_rates' in threshold_info:
        print("\nAction Success Rates:")
        for action, stats in threshold_info['success_rates'].items():
            success_rate = stats.get('success_rate', 0)
            sample_size = stats.get('sample_size', 0)
            print(f"  {action.capitalize()}: {success_rate:.2%} (from {sample_size} samples)")
    
if __name__ == "__main__":
    test_adaptive_thresholds()