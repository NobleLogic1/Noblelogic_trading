"""
Adaptive Confidence Thresholds for ML Trading Decisions

Dynamically adjusts confidence thresholds based on market conditions,
model performance, and risk parameters.
"""

import numpy as np
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import joblib
import os
import math

class AdaptiveThresholds:
    """
    Dynamically adjusts confidence thresholds based on:
    - Market regime (volatility, trend)
    - Historical model performance
    - Time of day effects
    - Recent signal quality
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize adaptive thresholds manager
        
        Args:
            base_path: Base path for storing threshold data
        """
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), 'thresholds')
        os.makedirs(self.base_path, exist_ok=True)
        
        # Base thresholds that will be dynamically adjusted
        self.base_thresholds = {
            'buy': 0.65,    # Default threshold for BUY signals
            'sell': 0.70,   # Higher threshold for SELL signals (more conservative)
            'hold': 0.50    # Lower threshold for HOLD signals
        }
        
        # Performance tracking
        self.decision_history = []  # Track recent decisions and outcomes
        self.max_history = 1000     # Maximum history entries to keep
        self.time_windows = {
            'short': 12 * 3600,     # 12 hours
            'medium': 24 * 3600,    # 24 hours
            'long': 7 * 24 * 3600   # 7 days
        }
        
        # Threshold adjustment factors
        self.market_regime_factors = {
            'BULL': {'buy': 0.9, 'sell': 1.1, 'hold': 1.0},    # Lower buy threshold in bull market
            'BEAR': {'buy': 1.1, 'sell': 0.9, 'hold': 1.0},    # Lower sell threshold in bear market
            'VOLATILE': {'buy': 1.2, 'sell': 1.2, 'hold': 0.9}, # Higher thresholds in volatile markets
            'SIDEWAYS': {'buy': 1.1, 'sell': 1.1, 'hold': 0.9}, # Higher thresholds in sideways markets
            'EUPHORIA': {'buy': 1.3, 'sell': 0.9, 'hold': 1.0}, # Much higher buy threshold in euphoria
            'PANIC': {'buy': 0.9, 'sell': 1.3, 'hold': 1.0},    # Much higher sell threshold in panic
            'RECOVERY': {'buy': 0.95, 'sell': 1.05, 'hold': 1.0} # Slightly lowered buy threshold in recovery
        }
        
        # Load existing data if available
        self.load_history()
        
    def load_history(self):
        """Load decision history and threshold data from disk"""
        history_path = os.path.join(self.base_path, 'decision_history.joblib')
        if os.path.exists(history_path):
            try:
                self.decision_history = joblib.load(history_path)
                print(f"[ML] Loaded {len(self.decision_history)} historical decisions for threshold adaptation")
            except Exception as e:
                print(f"[ML] Error loading threshold history: {e}")
        
        thresholds_path = os.path.join(self.base_path, 'adaptive_thresholds.joblib')
        if os.path.exists(thresholds_path):
            try:
                self.base_thresholds = joblib.load(thresholds_path)
                print(f"[ML] Loaded adaptive thresholds: {self.base_thresholds}")
            except Exception as e:
                print(f"[ML] Error loading thresholds: {e}")
    
    def save_history(self):
        """Save decision history and threshold data to disk"""
        history_path = os.path.join(self.base_path, 'decision_history.joblib')
        try:
            joblib.dump(self.decision_history, history_path)
        except Exception as e:
            print(f"[ML] Error saving threshold history: {e}")
        
        thresholds_path = os.path.join(self.base_path, 'adaptive_thresholds.joblib')
        try:
            joblib.dump(self.base_thresholds, thresholds_path)
        except Exception as e:
            print(f"[ML] Error saving thresholds: {e}")
    
    def record_decision(self, decision: Dict[str, Any], outcome: Optional[Dict[str, Any]] = None):
        """
        Record a trading decision and its outcome for adaptation
        
        Args:
            decision: Trading decision dictionary
            outcome: Optional outcome information
        """
        # Create a record of the decision
        record = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'action': decision.get('action'),
            'confidence': decision.get('confidence'),
            'symbol': decision.get('symbol'),
            'outcome': outcome,
            'successful': outcome.get('successful') if outcome else None,
            'profit': outcome.get('profit') if outcome else None
        }
        
        # Add to history
        self.decision_history.append(record)
        
        # Limit history size
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]
        
        # Adapt thresholds if we have outcome data
        if outcome:
            self._adapt_thresholds()
        
        # Save updated data periodically
        if len(self.decision_history) % 10 == 0:
            self.save_history()
    
    def _adapt_thresholds(self):
        """Update base thresholds based on historical performance"""
        # Only adapt if we have enough history
        if len(self.decision_history) < 50:
            return
        
        # Get decisions with outcomes
        decisions_with_outcomes = [d for d in self.decision_history 
                                  if d.get('outcome') is not None]
        
        if not decisions_with_outcomes:
            return
        
        # Calculate success rates for each action
        action_counts = {'buy': 0, 'sell': 0, 'hold': 0}
        success_counts = {'buy': 0, 'sell': 0, 'hold': 0}
        
        for decision in decisions_with_outcomes:
            action = {0: 'hold', 1: 'buy', 2: 'sell'}.get(decision.get('action'))
            if action:
                action_counts[action] += 1
                if decision.get('successful'):
                    success_counts[action] += 1
        
        # Calculate success rates and adjust thresholds
        for action in ['buy', 'sell', 'hold']:
            if action_counts[action] > 0:
                success_rate = success_counts[action] / action_counts[action]
                
                # Adjust threshold based on success rate
                # Lower success rate = higher threshold
                adjustment = max(0.8, min(1.2, (1.0 - success_rate + 0.5)))
                
                # Apply adjustment with dampening (20% of calculated adjustment)
                current = self.base_thresholds[action]
                target = current * adjustment
                self.base_thresholds[action] = current * 0.8 + target * 0.2
                
                # Ensure thresholds stay in reasonable bounds
                self.base_thresholds[action] = max(0.5, min(0.85, self.base_thresholds[action]))
    
    def get_thresholds(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Get adaptive thresholds based on current market conditions
        
        Args:
            market_data: Dictionary containing market information
            
        Returns:
            Dictionary of action-specific confidence thresholds
        """
        # Start with base thresholds
        thresholds = dict(self.base_thresholds)
        
        # Apply market regime adjustment if available
        market_regime = market_data.get('market_regime', 'SIDEWAYS')
        if market_regime in self.market_regime_factors:
            regime_factors = self.market_regime_factors[market_regime]
            for action, factor in regime_factors.items():
                thresholds[action] *= factor
        
        # Apply volatility adjustment
        volatility = market_data.get('volatility', 0.02)  # Default to 2% volatility
        if volatility > 0.05:  # High volatility
            # Increase all thresholds in high volatility
            for action in thresholds:
                thresholds[action] *= (1.0 + min(0.5, volatility))
        
        # Apply time-of-day effect
        hour = datetime.now().hour
        # Higher thresholds during market opens (first trading hour)
        if 13 <= hour <= 15:  # UTC hours that typically correspond to market opens
            for action in thresholds:
                thresholds[action] *= 1.05
        
        # Apply trend strength adjustment
        trend_strength = market_data.get('trend_strength', 0.5)
        trend_direction = market_data.get('trend_direction', 0)
        
        if abs(trend_strength) > 0.7:  # Strong trend
            if trend_direction > 0:  # Uptrend
                thresholds['buy'] *= 0.95  # Lower buy threshold
                thresholds['sell'] *= 1.1  # Raise sell threshold
            else:  # Downtrend
                thresholds['buy'] *= 1.1   # Raise buy threshold
                thresholds['sell'] *= 0.95 # Lower sell threshold
        
        # Apply recent performance adjustment
        recent_decisions = [d for d in self.decision_history 
                           if d.get('timestamp', 0) > time.time() - self.time_windows['short']]
        
        if recent_decisions:
            recent_success_rate = sum(1 for d in recent_decisions if d.get('successful')) / len(recent_decisions)
            
            # If recent success rate is low, be more conservative
            if recent_success_rate < 0.4:
                for action in thresholds:
                    thresholds[action] *= 1.1
            # If recent success rate is high, be more aggressive
            elif recent_success_rate > 0.7:
                for action in thresholds:
                    thresholds[action] *= 0.95
        
        # Ensure thresholds stay in reasonable bounds
        for action in thresholds:
            thresholds[action] = max(0.5, min(0.9, thresholds[action]))
        
        return thresholds
    
    def check_confidence(self, action: int, confidence: float, market_data: Dict[str, Any]) -> bool:
        """
        Check if a prediction meets the adaptive confidence threshold
        
        Args:
            action: Action index (0=hold, 1=buy, 2=sell)
            confidence: Model confidence
            market_data: Market data for context
            
        Returns:
            Boolean indicating if confidence threshold is met
        """
        # Get adaptive thresholds
        thresholds = self.get_thresholds(market_data)
        
        # Map action index to action name
        action_name = {0: 'hold', 1: 'buy', 2: 'sell'}.get(action, 'hold')
        
        # Get threshold for this action
        threshold = thresholds.get(action_name, 0.5)
        
        # Return comparison
        return confidence >= threshold
    
    def get_threshold_info(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information about current thresholds
        
        Args:
            market_data: Market data for context
            
        Returns:
            Dictionary with threshold information
        """
        thresholds = self.get_thresholds(market_data)
        
        # Calculate success rates
        action_success = {}
        for action_name in ['buy', 'sell', 'hold']:
            action_idx = {'hold': 0, 'buy': 1, 'sell': 2}.get(action_name)
            
            # Get relevant decisions
            relevant_decisions = [d for d in self.decision_history 
                               if d.get('action') == action_idx and
                               d.get('outcome') is not None]
            
            if relevant_decisions:
                success_count = sum(1 for d in relevant_decisions if d.get('successful'))
                success_rate = success_count / len(relevant_decisions)
                action_success[action_name] = {
                    'success_rate': success_rate,
                    'sample_size': len(relevant_decisions)
                }
            else:
                action_success[action_name] = {
                    'success_rate': 0.5,
                    'sample_size': 0
                }
        
        return {
            'current_thresholds': thresholds,
            'base_thresholds': self.base_thresholds,
            'market_regime': market_data.get('market_regime', 'UNKNOWN'),
            'success_rates': action_success,
            'history_size': len(self.decision_history),
            'adaptation_active': len(self.decision_history) >= 50
        }