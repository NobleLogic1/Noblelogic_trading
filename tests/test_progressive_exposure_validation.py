#!/usr/bin/env python3
"""
Comprehensive Validation Tests for Progressive Exposure System
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock

from comprehensive_validator import validator
from progressive_exposure import ProgressiveExposureSystem, ExposureLevel, PerformanceMetrics

class TestProgressiveExposureValidation:
    """Comprehensive validation tests for progressive exposure system"""

    def setup_method(self):
        """Setup for each test"""
        self.exposure_system = ProgressiveExposureSystem()

    def test_initialization(self):
        """Test system initialization"""
        assert self.exposure_system.min_trades_required == 10
        assert self.exposure_system.max_exposure == 0.10  # 10%
        assert len(self.exposure_system.trade_history) == 0
        assert self.exposure_system.current_balance == 10000.0

    def test_conservative_exposure_no_trades(self):
        """Test conservative exposure with no trading history"""
        recommendation = self.exposure_system.get_exposure_recommendation(0.5, 'medium', 10000.0)

        assert recommendation.exposure_level == ExposureLevel.CONSERVATIVE
        assert recommendation.final_multiplier < 0.005  # Very conservative
        assert "only 0 trades" in recommendation.reasoning[0]

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation with sample data"""
        # Add winning trades
        for i in range(15):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 50.0,
                'profit_pct': 0.05,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Add some losing trades
        for i in range(5):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': -25.0,
                'profit_pct': -0.025,
                'is_win': False,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        metrics = self.exposure_system.calculate_performance_metrics()

        assert metrics.total_trades == 20
        assert 0.7 <= metrics.win_rate <= 0.8  # Should be around 75%
        assert metrics.profit_factor > 1.0  # Profitable system
        assert metrics.total_pnl > 0  # Net positive

    def test_exposure_level_progression(self):
        """Test that exposure levels progress correctly with performance"""
        # Test conservative level
        recommendation = self.exposure_system.get_exposure_recommendation(0.5, 'low', 10000.0)
        assert recommendation.exposure_level == ExposureLevel.CONSERVATIVE

        # Add excellent performance trades
        for i in range(25):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 100.0,
                'profit_pct': 0.10,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Should progress to higher exposure level
        recommendation = self.exposure_system.get_exposure_recommendation(0.8, 'low', 10000.0)
        assert recommendation.exposure_level in [ExposureLevel.MODERATE, ExposureLevel.AGGRESSIVE, ExposureLevel.HIGH_CONFIDENCE]
        assert recommendation.final_multiplier > 0.005  # Should be higher than conservative

    def test_confidence_scaling(self):
        """Test confidence-based scaling"""
        # Add baseline trades
        for i in range(15):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 50.0,
                'profit_pct': 0.05,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Test different confidence levels
        low_conf = self.exposure_system.get_exposure_recommendation(0.3, 'medium', 10000.0)
        high_conf = self.exposure_system.get_exposure_recommendation(0.9, 'medium', 10000.0)

        # High confidence should give higher multiplier
        assert high_conf.confidence_multiplier >= low_conf.confidence_multiplier

    def test_risk_adjustment(self):
        """Test risk level adjustments"""
        # Add baseline trades
        for i in range(15):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 50.0,
                'profit_pct': 0.05,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Test different risk levels
        low_risk = self.exposure_system.get_exposure_recommendation(0.7, 'low', 10000.0)
        high_risk = self.exposure_system.get_exposure_recommendation(0.7, 'high', 10000.0)

        # Lower risk should allow higher exposure
        assert low_risk.risk_adjusted_multiplier >= high_risk.risk_adjusted_multiplier

    def test_max_exposure_limits(self):
        """Test that system respects maximum exposure limits"""
        # Add excellent performance trades
        for i in range(50):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 200.0,
                'profit_pct': 0.20,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        recommendation = self.exposure_system.get_exposure_recommendation(0.9, 'low', 10000.0)

        # Should not exceed max exposure (5% of balance = $500)
        max_allowed = 10000.0 * self.exposure_system.max_exposure
        assert recommendation.max_position_size <= max_allowed

    def test_trade_history_management(self):
        """Test trade history management and limits"""
        # Add many trades
        for i in range(1200):  # More than max history
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 10.0,
                'profit_pct': 0.01,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Should maintain reasonable history size
        assert len(self.exposure_system.trade_history) <= 1000  # Max history limit

    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Test with invalid trade data
        self.exposure_system.record_trade({})
        self.exposure_system.record_trade(None)
        self.exposure_system.record_trade("invalid")

        # Should still function
        recommendation = self.exposure_system.get_exposure_recommendation(0.5, 'medium', 10000.0)
        assert recommendation is not None

    def test_balance_tracking(self):
        """Test balance tracking and drawdown calculation"""
        initial_balance = self.exposure_system.current_balance

        # Add profitable trades
        for i in range(10):
            trade = {
                'symbol': 'BTCUSDT',
                'profit': 100.0,
                'profit_pct': 0.01,
                'is_win': True,
                'timestamp': datetime.now().isoformat()
            }
            self.exposure_system.record_trade(trade)

        # Balance should increase
        assert self.exposure_system.current_balance > initial_balance
        assert self.exposure_system.peak_balance >= self.exposure_system.current_balance

# Validation test runner
def run_progressive_exposure_validation():
    """Run all progressive exposure validation tests"""
    test_instance = TestProgressiveExposureValidation()
    test_instance.setup_method()  # Initialize the test instance

    tests = [
        ("initialization", test_instance.test_initialization),
        ("conservative_exposure_no_trades", test_instance.test_conservative_exposure_no_trades),
        ("performance_metrics_calculation", test_instance.test_performance_metrics_calculation),
        ("exposure_level_progression", test_instance.test_exposure_level_progression),
        ("confidence_scaling", test_instance.test_confidence_scaling),
        ("risk_adjustment", test_instance.test_risk_adjustment),
        ("max_exposure_limits", test_instance.test_max_exposure_limits),
        ("trade_history_management", test_instance.test_trade_history_management),
        ("error_handling", test_instance.test_error_handling),
        ("balance_tracking", test_instance.test_balance_tracking),
    ]

    print("🧪 Running Progressive Exposure Validation Tests")
    print("-" * 50)

    for test_name, test_func in tests:
        validator.validate_component("ProgressiveExposure", test_name, test_func)

if __name__ == "__main__":
    run_progressive_exposure_validation()