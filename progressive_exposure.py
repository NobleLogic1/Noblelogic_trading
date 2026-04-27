"""
Progressive Exposure System for NobleLogic Trading
Gradually increases position sizes based on system performance and confidence
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import math

class ExposureLevel(Enum):
    CONSERVATIVE = 1
    MODERATE = 2
    AGGRESSIVE = 3
    HIGH_CONFIDENCE = 4

@dataclass
class PerformanceMetrics:
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    avg_win: float
    avg_loss: float
    consecutive_wins: int
    consecutive_losses: int
    total_pnl: float
    days_active: int

@dataclass
class ExposureRecommendation:
    base_multiplier: float
    performance_multiplier: float
    confidence_multiplier: float
    risk_adjusted_multiplier: float
    final_multiplier: float
    exposure_level: ExposureLevel
    max_position_size: float
    reasoning: List[str]

class ProgressiveExposureSystem:
    """
    Progressive exposure system that gradually increases position sizes
    based on trading performance, confidence, and risk metrics
    """

    def __init__(self):
        # Performance tracking
        self.trade_history = []
        self.daily_pnl = []
        self.peak_balance = 10000.0  # Starting balance
        self.current_balance = 10000.0

        # Exposure parameters
        self.base_exposure = 0.01  # 1% of balance as base
        self.max_exposure = 0.10  # Maximum 10% of balance
        self.min_trades_required = 10  # Minimum trades before progressive exposure
        self.confidence_threshold = 0.75  # Minimum confidence for increased exposure

        # Progressive scaling parameters
        self.performance_weights = {
            'win_rate': 0.3,
            'profit_factor': 0.25,
            'sharpe_ratio': 0.2,
            'drawdown_penalty': 0.15,
            'consistency_bonus': 0.1
        }

        # Exposure level thresholds
        self.exposure_thresholds = {
            ExposureLevel.CONSERVATIVE: {
                'min_trades': 0,
                'min_win_rate': 0.0,
                'max_multiplier': 0.5
            },
            ExposureLevel.MODERATE: {
                'min_trades': 25,
                'min_win_rate': 0.55,
                'max_multiplier': 1.0
            },
            ExposureLevel.AGGRESSIVE: {
                'min_trades': 50,
                'min_win_rate': 0.60,
                'max_multiplier': 2.0
            },
            ExposureLevel.HIGH_CONFIDENCE: {
                'min_trades': 100,
                'min_win_rate': 0.65,
                'max_multiplier': 3.0
            }
        }

        # Risk-based exposure adjustments
        self.risk_adjustments = {
            'very_low': 1.2,
            'low': 1.1,
            'medium': 1.0,
            'high': 0.8,
            'very_high': 0.6
        }

        # Confidence-based scaling
        self.confidence_scaling = {
            (0.0, 0.6): 0.5,   # Low confidence: 50% of calculated size
            (0.6, 0.75): 0.75, # Medium confidence: 75% of calculated size
            (0.75, 0.85): 1.0, # High confidence: 100% of calculated size
            (0.85, 1.0): 1.25  # Very high confidence: 125% of calculated size
        }

    def record_trade(self, trade_result: Dict[str, Any]):
        """
        Record a completed trade for performance tracking

        Args:
            trade_result: Dictionary containing trade details
        """
        # Handle invalid inputs gracefully
        if trade_result is None or not isinstance(trade_result, dict):
            return  # Silently ignore invalid trade records

        trade_entry = {
            'timestamp': datetime.now(),
            'symbol': trade_result.get('symbol', 'UNKNOWN'),
            'pnl': trade_result.get('profit', 0.0),
            'win': trade_result.get('profit', 0) > 0,
            'confidence': trade_result.get('confidence', 0.5),
            'risk_level': trade_result.get('risk_level', 'medium'),
            'position_size': trade_result.get('position_size', 0.0)
        }

        self.trade_history.append(trade_entry)

        # Update balance tracking
        self.current_balance += trade_entry['pnl']
        self.peak_balance = max(self.peak_balance, self.current_balance)

        # Keep history manageable
        if len(self.trade_history) > 1000:
            self.trade_history = self.trade_history[-1000:]

    def calculate_performance_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if not self.trade_history:
            return PerformanceMetrics(
                total_trades=0, win_rate=0.0, profit_factor=0.0, max_drawdown=0.0,
                sharpe_ratio=0.0, calmar_ratio=0.0, avg_win=0.0, avg_loss=0.0,
                consecutive_wins=0, consecutive_losses=0, total_pnl=0.0, days_active=0
            )

        trades_df = pd.DataFrame(self.trade_history)

        # Basic metrics
        total_trades = len(trades_df)
        wins = trades_df[trades_df['win'] == True]
        losses = trades_df[trades_df['win'] == False]

        win_rate = len(wins) / total_trades if total_trades > 0 else 0.0

        # Profit metrics
        total_pnl = trades_df['pnl'].sum()
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0.0
        avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0.0

        # Profit factor
        total_wins = wins['pnl'].sum() if len(wins) > 0 else 0.0
        total_losses = abs(losses['pnl'].sum()) if len(losses) > 0 else 0.0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

        # Drawdown calculation
        cumulative = trades_df['pnl'].cumsum()
        running_max = cumulative.expanding().max()
        drawdowns = running_max - cumulative
        max_drawdown = drawdowns.max() / self.peak_balance if self.peak_balance > 0 else 0.0

        # Risk-adjusted metrics
        returns = trades_df['pnl'] / self.peak_balance  # Normalize to starting balance
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0.0
        calmar_ratio = returns.mean() / max_drawdown * 252 if max_drawdown > 0 else float('inf')

        # Consistency metrics
        consecutive_wins = 0
        consecutive_losses = 0
        current_streak = 0

        for win in trades_df['win']:
            if win:
                if current_streak >= 0:
                    current_streak += 1
                else:
                    current_streak = 1
                consecutive_wins = max(consecutive_wins, current_streak)
            else:
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                consecutive_losses = max(consecutive_losses, abs(current_streak))

        # Days active
        if total_trades > 0:
            start_date = trades_df['timestamp'].min()
            end_date = trades_df['timestamp'].max()
            days_active = (end_date - start_date).days + 1
        else:
            days_active = 0

        return PerformanceMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            calmar_ratio=calmar_ratio,
            avg_win=avg_win,
            avg_loss=avg_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            total_pnl=total_pnl,
            days_active=days_active
        )

    def calculate_performance_multiplier(self, metrics: PerformanceMetrics) -> float:
        """
        Calculate exposure multiplier based on performance metrics
        """
        if metrics.total_trades < self.min_trades_required:
            # Conservative approach for new systems
            base_multiplier = 0.3
            reasoning = [f"System has only {metrics.total_trades} trades, using conservative exposure"]
        else:
            # Performance-based scaling
            win_rate_score = min(1.0, metrics.win_rate / 0.7)  # Target 70% win rate
            profit_factor_score = min(2.0, metrics.profit_factor / 1.5)  # Target profit factor > 1.5
            sharpe_score = min(2.0, max(0.0, metrics.sharpe_ratio / 1.0))  # Target Sharpe > 1.0

            # Drawdown penalty
            drawdown_penalty = max(0.1, 1.0 - (metrics.max_drawdown * 2))

            # Consistency bonus
            consistency_bonus = min(1.5, 1.0 + (metrics.consecutive_wins * 0.05))

            base_multiplier = (
                win_rate_score * self.performance_weights['win_rate'] +
                profit_factor_score * self.performance_weights['profit_factor'] +
                sharpe_score * self.performance_weights['sharpe_ratio'] +
                drawdown_penalty * self.performance_weights['drawdown_penalty'] +
                consistency_bonus * self.performance_weights['consistency_bonus']
            )

            reasoning = [
                f"Win rate: {metrics.win_rate:.1%} (target: 70%)",
                f"Profit factor: {metrics.profit_factor:.2f} (target: >1.5)",
                f"Sharpe ratio: {metrics.sharpe_ratio:.2f} (target: >1.0)",
                f"Max drawdown: {metrics.max_drawdown:.1%}",
                f"Performance multiplier: {base_multiplier:.2f}"
            ]

        return max(0.1, min(3.0, base_multiplier)), reasoning

    def calculate_confidence_multiplier(self, confidence: float) -> float:
        """
        Calculate exposure multiplier based on prediction confidence
        """
        for (min_conf, max_conf), multiplier in self.confidence_scaling.items():
            if min_conf <= confidence < max_conf:
                return multiplier
        return 0.5  # Default conservative multiplier

    def determine_exposure_level(self, metrics: PerformanceMetrics) -> ExposureLevel:
        """
        Determine the current exposure level based on performance
        """
        for level in reversed(ExposureLevel):  # Check highest levels first
            thresholds = self.exposure_thresholds[level]
            if (metrics.total_trades >= thresholds['min_trades'] and
                metrics.win_rate >= thresholds['min_win_rate']):
                return level

        return ExposureLevel.CONSERVATIVE

    def get_exposure_recommendation(self,
                                  confidence: float,
                                  risk_level: str,
                                  current_balance: float) -> ExposureRecommendation:
        """
        Get comprehensive exposure recommendation

        Args:
            confidence: ML model confidence (0.0 to 1.0)
            risk_level: Risk assessment level ('very_low', 'low', 'medium', 'high', 'very_high')
            current_balance: Current account balance

        Returns:
            ExposureRecommendation with all calculated multipliers
        """
        # Calculate performance metrics
        performance_metrics = self.calculate_performance_metrics()

        # Base exposure as percentage of balance
        base_multiplier = self.base_exposure

        # Performance-based multiplier
        performance_multiplier, performance_reasoning = self.calculate_performance_multiplier(performance_metrics)

        # Confidence-based multiplier
        confidence_multiplier = self.calculate_confidence_multiplier(confidence)

        # Risk-based adjustment
        risk_multiplier = self.risk_adjustments.get(risk_level.lower(), 1.0)

        # Combined multiplier with caps
        combined_multiplier = base_multiplier * performance_multiplier * confidence_multiplier * risk_multiplier

        # Apply exposure level caps
        exposure_level = self.determine_exposure_level(performance_metrics)
        level_cap = self.exposure_thresholds[exposure_level]['max_multiplier']
        final_multiplier = min(combined_multiplier, level_cap * base_multiplier)

        # Ensure within absolute limits
        final_multiplier = max(self.base_exposure * 0.1, min(final_multiplier, self.max_exposure))

        # Calculate maximum position size
        max_position_size = current_balance * final_multiplier

        # Compile reasoning
        reasoning = performance_reasoning + [
            f"Confidence: {confidence:.1%} -> multiplier: {confidence_multiplier:.2f}",
            f"Risk level: {risk_level} -> adjustment: {risk_multiplier:.2f}",
            f"Exposure level: {exposure_level.name} (cap: {level_cap:.1f}x)",
            f"Final multiplier: {final_multiplier:.4f} ({final_multiplier/current_balance:.2%} of balance)",
            f"Max position size: ${max_position_size:.2f}"
        ]

        return ExposureRecommendation(
            base_multiplier=base_multiplier,
            performance_multiplier=performance_multiplier,
            confidence_multiplier=confidence_multiplier,
            risk_adjusted_multiplier=risk_multiplier,
            final_multiplier=final_multiplier,
            exposure_level=exposure_level,
            max_position_size=max_position_size,
            reasoning=reasoning
        )

    def get_progressive_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the progressive exposure system
        """
        metrics = self.calculate_performance_metrics()

        return {
            'performance_metrics': {
                'total_trades': metrics.total_trades,
                'win_rate': f"{metrics.win_rate:.1%}",
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'max_drawdown': f"{metrics.max_drawdown:.1%}",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.2f}",
                'total_pnl': f"${metrics.total_pnl:.2f}",
                'days_active': metrics.days_active
            },
            'exposure_system': {
                'current_exposure_level': self.determine_exposure_level(metrics).name,
                'base_exposure': f"{self.base_exposure:.1%}",
                'max_exposure': f"{self.max_exposure:.1%}",
                'min_trades_required': self.min_trades_required,
                'confidence_threshold': f"{self.confidence_threshold:.1%}"
            },
            'recent_performance': self._get_recent_performance_summary()
        }

    def _get_recent_performance_summary(self) -> Dict[str, Any]:
        """Get summary of recent trading performance"""
        if not self.trade_history:
            return {'message': 'No trades recorded yet'}

        recent_trades = self.trade_history[-20:]  # Last 20 trades
        recent_df = pd.DataFrame(recent_trades)

        recent_win_rate = recent_df['win'].mean()
        recent_pnl = recent_df['pnl'].sum()
        recent_avg_confidence = recent_df['confidence'].mean()

        return {
            'trades_analyzed': len(recent_trades),
            'win_rate': f"{recent_win_rate:.1%}",
            'total_pnl': f"${recent_pnl:.2f}",
            'avg_confidence': f"{recent_avg_confidence:.1%}",
            'avg_position_size': recent_df['position_size'].mean() if 'position_size' in recent_df.columns else 0.0
        }

# Global instance
progressive_exposure = ProgressiveExposureSystem()