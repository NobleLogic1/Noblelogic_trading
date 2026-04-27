"""
Demonstration of Adaptive Thresholds for Trading Decisions

This script demonstrates how adaptive thresholds improve trading decisions
by comparing fixed threshold performance with adaptive threshold performance.
"""

import os
import time
import random
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from ml.adaptive_thresholds import AdaptiveThresholds

class TradingSimulator:
    """Simple simulator to demonstrate adaptive threshold benefits"""
    
    def __init__(self):
        self.adaptive_thresholds = AdaptiveThresholds()
        self.fixed_thresholds = {
            'buy': 0.65,
            'sell': 0.70,
            'hold': 0.50
        }
        
        # Track performance
        self.fixed_results = []
        self.adaptive_results = []
        
        # Market states
        self.market_regimes = ["BULL", "BEAR", "VOLATILE", "SIDEWAYS", "EUPHORIA", "PANIC", "RECOVERY"]
        self.current_regime = "SIDEWAYS"
        self.volatility = 0.02
        self.regime_duration = 20  # How many decisions before regime change
        self.decisions_in_regime = 0
        
        # Decision quality varies by regime
        self.regime_quality = {
            "BULL": {'buy': 0.8, 'sell': 0.3, 'hold': 0.5},
            "BEAR": {'buy': 0.3, 'sell': 0.8, 'hold': 0.5},
            "VOLATILE": {'buy': 0.4, 'sell': 0.4, 'hold': 0.7},
            "SIDEWAYS": {'buy': 0.5, 'sell': 0.5, 'hold': 0.7},
            "EUPHORIA": {'buy': 0.2, 'sell': 0.9, 'hold': 0.4},
            "PANIC": {'buy': 0.9, 'sell': 0.2, 'hold': 0.4},
            "RECOVERY": {'buy': 0.7, 'sell': 0.6, 'hold': 0.5}
        }
        
    def update_market(self):
        """Update market conditions"""
        self.decisions_in_regime += 1
        if self.decisions_in_regime >= self.regime_duration:
            # Change market regime
            self.current_regime = random.choice(self.market_regimes)
            self.volatility = random.uniform(0.01, 0.09)
            self.decisions_in_regime = 0
            print(f"\n===== Market regime changed to {self.current_regime} (volatility: {self.volatility:.2f}) =====\n")
    
    def get_market_data(self):
        """Get current market data"""
        trend_direction = 1 if self.current_regime in ["BULL", "RECOVERY", "EUPHORIA"] else -1 if self.current_regime in ["BEAR", "PANIC"] else 0
        trend_strength = random.uniform(0.3, 0.9) if trend_direction != 0 else random.uniform(0.1, 0.3)
        
        return {
            "market_regime": self.current_regime,
            "volatility": self.volatility,
            "trend_strength": trend_strength,
            "trend_direction": trend_direction
        }
    
    def simulate_prediction(self):
        """Simulate an ML prediction"""
        # Random action with slight bias based on market regime
        regime_bias = {
            "BULL": [0.2, 0.6, 0.2],  # Hold, Buy, Sell probabilities
            "BEAR": [0.2, 0.2, 0.6],
            "VOLATILE": [0.4, 0.3, 0.3],
            "SIDEWAYS": [0.5, 0.25, 0.25],
            "EUPHORIA": [0.1, 0.8, 0.1],
            "PANIC": [0.1, 0.1, 0.8],
            "RECOVERY": [0.3, 0.5, 0.2]
        }
        
        bias = regime_bias.get(self.current_regime, [0.33, 0.33, 0.34])
        action = random.choices([0, 1, 2], weights=bias)[0]  # 0=Hold, 1=Buy, 2=Sell
        
        # Confidence level - simulate higher confidence in the preferred action for the regime
        if action == 0:  # Hold
            confidence = random.uniform(0.5, 0.8)
        elif action == 1:  # Buy - higher confidence in bull markets
            if self.current_regime in ["BULL", "RECOVERY", "EUPHORIA"]:
                confidence = random.uniform(0.65, 0.9)
            else:
                confidence = random.uniform(0.55, 0.8)
        else:  # Sell - higher confidence in bear markets
            if self.current_regime in ["BEAR", "PANIC"]:
                confidence = random.uniform(0.65, 0.9)
            else:
                confidence = random.uniform(0.55, 0.8)
        
        return {
            'action': action,
            'confidence': confidence
        }
    
    def simulate_trade_outcome(self, action, market_data):
        """Simulate trade outcome - success probability depends on action and market regime"""
        action_name = {0: 'hold', 1: 'buy', 2: 'sell'}.get(action, 'hold')
        
        # Get success probability based on regime and action
        success_prob = self.regime_quality[market_data['market_regime']].get(action_name, 0.5)
        
        # Random outcome based on success probability
        success = random.random() < success_prob
        
        # Simulate profit/loss
        if success:
            profit = random.uniform(0.01, 0.05)  # 1-5% profit
        else:
            profit = random.uniform(-0.05, -0.01)  # 1-5% loss
        
        return {
            'successful': success,
            'profit': profit,
            'hit_target': success,
            'hit_stop_loss': not success
        }
    
    def run_simulation(self, num_decisions=200):
        """Run simulation comparing fixed vs adaptive thresholds"""
        print(f"Starting simulation with {num_decisions} trading decisions")
        
        # Initialize results tracking
        fixed_profits = []
        adaptive_profits = []
        fixed_cumulative = 0
        adaptive_cumulative = 0
        fixed_trades = 0
        adaptive_trades = 0
        fixed_successful = 0
        adaptive_successful = 0
        
        # Run simulation
        for i in range(num_decisions):
            # Update market conditions periodically
            self.update_market()
            
            # Get current market data
            market_data = self.get_market_data()
            
            # Simulate ML prediction
            prediction = self.simulate_prediction()
            action = prediction['action']
            confidence = prediction['confidence']
            
            # Check if trade meets fixed threshold
            action_name = {0: 'hold', 1: 'buy', 2: 'sell'}.get(action, 'hold')
            fixed_threshold = self.fixed_thresholds.get(action_name, 0.5)
            fixed_trade = confidence >= fixed_threshold
            
            # Check if trade meets adaptive threshold
            adaptive_trade = self.adaptive_thresholds.check_confidence(action, confidence, market_data)
            
            # Simulate outcome
            outcome = self.simulate_trade_outcome(action, market_data)
            
            # Record decision for adaptive system
            decision = {
                'action': action,
                'confidence': confidence,
                'symbol': 'BTC/USD'
            }
            self.adaptive_thresholds.record_decision(decision, outcome)
            
            # Track results for fixed threshold
            if fixed_trade and action != 0:  # Only count actual trades (not holds)
                fixed_trades += 1
                fixed_profit = outcome['profit']
                fixed_cumulative += fixed_profit
                if outcome['successful']:
                    fixed_successful += 1
            else:
                fixed_profit = 0
            
            # Track results for adaptive threshold
            if adaptive_trade and action != 0:  # Only count actual trades (not holds)
                adaptive_trades += 1
                adaptive_profit = outcome['profit']
                adaptive_cumulative += adaptive_profit
                if outcome['successful']:
                    adaptive_successful += 1
            else:
                adaptive_profit = 0
            
            # Append to profit history
            fixed_profits.append(fixed_cumulative)
            adaptive_profits.append(adaptive_cumulative)
            
            # Print progress
            if (i + 1) % 20 == 0:
                fixed_win_rate = fixed_successful / fixed_trades if fixed_trades > 0 else 0
                adaptive_win_rate = adaptive_successful / adaptive_trades if adaptive_trades > 0 else 0
                
                print(f"Decision {i+1}/{num_decisions} - Market: {market_data['market_regime']}")
                print(f"  Fixed: {fixed_trades} trades, {fixed_successful} successful ({fixed_win_rate:.1%}), P/L: {fixed_cumulative:.2%}")
                print(f"  Adaptive: {adaptive_trades} trades, {adaptive_successful} successful ({adaptive_win_rate:.1%}), P/L: {adaptive_cumulative:.2%}")
                
                # Get current thresholds for comparison
                adaptive_thresholds = self.adaptive_thresholds.get_thresholds(market_data)
                print(f"  Current Thresholds - Buy: Fixed={self.fixed_thresholds['buy']:.2f} Adaptive={adaptive_thresholds['buy']:.2f}, " +
                      f"Sell: Fixed={self.fixed_thresholds['sell']:.2f} Adaptive={adaptive_thresholds['sell']:.2f}")
        
        # Calculate final statistics
        fixed_win_rate = fixed_successful / fixed_trades if fixed_trades > 0 else 0
        adaptive_win_rate = adaptive_successful / adaptive_trades if adaptive_trades > 0 else 0
        fixed_avg_profit = fixed_cumulative / fixed_trades if fixed_trades > 0 else 0
        adaptive_avg_profit = adaptive_cumulative / adaptive_trades if adaptive_trades > 0 else 0
        
        print("\n===== Simulation Results =====")
        print(f"Fixed Threshold Strategy:")
        print(f"  Trades Executed: {fixed_trades}/{num_decisions}")
        print(f"  Success Rate: {fixed_win_rate:.2%}")
        print(f"  Total P/L: {fixed_cumulative:.2%}")
        print(f"  Average Profit per Trade: {fixed_avg_profit:.2%}")
        
        print(f"\nAdaptive Threshold Strategy:")
        print(f"  Trades Executed: {adaptive_trades}/{num_decisions}")
        print(f"  Success Rate: {adaptive_win_rate:.2%}")
        print(f"  Total P/L: {adaptive_cumulative:.2%}")
        print(f"  Average Profit per Trade: {adaptive_avg_profit:.2%}")
        
        # Plot results
        self.plot_results(fixed_profits, adaptive_profits, num_decisions)
        
        return {
            'fixed': {
                'trades': fixed_trades,
                'success_rate': fixed_win_rate,
                'total_profit': fixed_cumulative,
                'avg_profit': fixed_avg_profit
            },
            'adaptive': {
                'trades': adaptive_trades,
                'success_rate': adaptive_win_rate,
                'total_profit': adaptive_cumulative,
                'avg_profit': adaptive_avg_profit
            }
        }
    
    def plot_results(self, fixed_profits, adaptive_profits, num_decisions):
        """Plot comparison of fixed vs adaptive thresholds"""
        try:
            plt.figure(figsize=(12, 7))
            plt.plot(range(num_decisions), fixed_profits, 'b-', label='Fixed Thresholds')
            plt.plot(range(num_decisions), adaptive_profits, 'g-', label='Adaptive Thresholds')
            plt.title('Adaptive vs Fixed Thresholds Performance')
            plt.xlabel('Trading Decisions')
            plt.ylabel('Cumulative Profit/Loss')
            plt.legend()
            plt.grid(True)
            
            # Save the plot
            plot_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adaptive_vs_fixed.png')
            plt.savefig(plot_file)
            print(f"\nPlot saved to {plot_file}")
            
            # Show the plot if in interactive mode
            plt.show()
        except Exception as e:
            print(f"Error creating plot: {e}")

if __name__ == "__main__":
    simulator = TradingSimulator()
    simulator.run_simulation(num_decisions=300)