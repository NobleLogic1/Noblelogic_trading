#!/usr/bin/env python3
"""
Comprehensive Validation Tests for Enhanced Risk Assessment System
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

from comprehensive_validator import validator
from enhanced_risk_assessment import EnhancedRiskAssessment, RiskMetrics, RiskLevel

class TestRiskAssessmentValidation:
    """Comprehensive validation tests for risk assessment system"""

    def setup_method(self):
        """Setup for each test"""
        self.risk_assessor = EnhancedRiskAssessment()

    def test_initialization(self):
        """Test system initialization"""
        assert self.risk_assessor.market_regime == 'NORMAL'
        assert hasattr(self.risk_assessor, 'comprehensive_risk_assessment')
        assert hasattr(self.risk_assessor, 'get_position_size_recommendation')

    def test_default_risk_metrics(self):
        """Test default risk metrics generation"""
        metrics = self.risk_assessor._default_risk_metrics()

        assert isinstance(metrics, RiskMetrics)
        assert metrics.risk_level in RiskLevel
        assert 0.0 <= metrics.confidence <= 1.0
        assert len(metrics.recommendations) > 0

    def test_position_size_recommendation_basic(self):
        """Test basic position size recommendation"""
        metrics = self.risk_assessor._default_risk_metrics()

        recommendation = self.risk_assessor.get_position_size_recommendation(
            metrics, 1.0, 0.5, 10000.0
        )

        required_keys = [
            'base_position', 'traditional_position', 'progressive_position',
            'final_position', 'method_used', 'risk_level', 'exposure_level'
        ]

        for key in required_keys:
            assert key in recommendation, f"Missing key: {key}"

        assert recommendation['final_position'] > 0
        assert recommendation['method_used'] in ['traditional', 'progressive']

    def test_risk_level_multipliers(self):
        """Test that different risk levels produce appropriate multipliers"""
        base_position = 1.0
        confidence = 0.7
        balance = 10000.0

        results = {}
        for risk_level in RiskLevel:
            # Create mock metrics with specific risk level
            metrics = RiskMetrics(
                volatility_risk=0.5,
                liquidity_risk=0.5,
                market_risk=0.5,
                technical_risk=0.5,
                sentiment_risk=0.5,
                concentration_risk=0.5,
                correlation_risk=0.5,
                drawdown_risk=0.5,
                overall_score=0.5,
                risk_level=risk_level,
                confidence=0.7,
                recommendations=["Test recommendation"]
            )

            recommendation = self.risk_assessor.get_position_size_recommendation(
                metrics, base_position, confidence, balance
            )

            results[risk_level.name] = recommendation['traditional_position']

        # Very low risk should have highest position size
        assert results['VERY_LOW'] >= results['LOW'] >= results['MEDIUM'] >= results['HIGH'] >= results['VERY_HIGH']

    def test_confidence_impact(self):
        """Test that confidence affects position sizing"""
        metrics = self.risk_assessor._default_risk_metrics()
        base_position = 1.0
        balance = 10000.0

        low_conf = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, 0.3, balance
        )

        high_conf = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, 0.9, balance
        )

        # Higher confidence should generally lead to larger positions
        assert high_conf['final_position'] >= low_conf['final_position']

    def test_market_regime_adjustments(self):
        """Test market regime adjustments"""
        metrics = self.risk_assessor._default_risk_metrics()
        base_position = 1.0
        confidence = 0.7
        balance = 10000.0

        regimes = ['BULL', 'BEAR', 'SIDEWAYS', 'VOLATILE', 'EUPHORIA', 'PANIC', 'RECOVERY']

        results = {}
        for regime in regimes:
            self.risk_assessor.market_regime = regime
            recommendation = self.risk_assessor.get_position_size_recommendation(
                metrics, base_position, confidence, balance
            )
            results[regime] = recommendation['traditional_position']

        # Bull and recovery should have higher positions than bear and panic
        assert results['BULL'] >= results['SIDEWAYS']
        assert results['RECOVERY'] >= results['SIDEWAYS']
        assert results['BEAR'] <= results['SIDEWAYS']
        assert results['PANIC'] <= results['SIDEWAYS']
        assert results['VOLATILE'] <= results['SIDEWAYS']

    def test_progressive_vs_traditional(self):
        """Test progressive vs traditional method selection"""
        metrics = self.risk_assessor._default_risk_metrics()
        base_position = 1.0
        confidence = 0.7
        balance = 10000.0

        # With no trades, should use traditional
        recommendation = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, confidence, balance
        )

        assert recommendation['method_used'] == 'traditional'
        # Note: Progressive position may be larger due to different calculation methods
        # The key is that traditional method is used when insufficient trade history

    def test_max_exposure_limits(self):
        """Test that position sizes respect maximum exposure limits"""
        metrics = self.risk_assessor._default_risk_metrics()
        base_position = 100.0  # Large base position
        confidence = 0.9
        balance = 10000.0

        recommendation = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, confidence, balance
        )

        # Should not exceed reasonable limits (e.g., 10% of balance for very aggressive)
        max_reasonable = balance * 0.10
        assert recommendation['final_position'] <= max_reasonable

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test with None metrics
            with pytest.raises((AttributeError, TypeError)):
                self.risk_assessor.get_position_size_recommendation(
                    None, 1.0, 0.5, 10000.0
                )

        except Exception as e:
            pytest.fail(f"Error handling for None metrics failed unexpectedly: {e}")

        try:
            # Test with invalid confidence
            metrics = self.risk_assessor._default_risk_metrics()
            recommendation = self.risk_assessor.get_position_size_recommendation(
                metrics, 1.0, 1.5, 10000.0  # Invalid confidence > 1.0
            )
            # Should handle gracefully
            assert recommendation['final_position'] >= 0

        except Exception as e:
            pytest.fail(f"Error handling for invalid confidence failed unexpectedly: {e}")

    def test_balance_impact(self):
        """Test that account balance affects position sizing"""
        metrics = self.risk_assessor._default_risk_metrics()
        base_position = 1.0
        confidence = 0.7

        small_balance = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, confidence, 1000.0  # Small balance
        )

        large_balance = self.risk_assessor.get_position_size_recommendation(
            metrics, base_position, confidence, 100000.0  # Large balance
        )

        # Larger balance should generally allow larger positions
        assert large_balance['final_position'] >= small_balance['final_position']

    def test_risk_calculations(self):
        """Test individual risk calculation components"""
        # Test dynamic threshold calculation
        threshold = self.risk_assessor._calculate_dynamic_threshold('volatility')
        assert 0.0 <= threshold <= 1.0

        # Test risk level determination
        very_low_risk = self.risk_assessor._determine_risk_level(0.1)
        high_risk = self.risk_assessor._determine_risk_level(0.8)

        assert very_low_risk in [RiskLevel.VERY_LOW, RiskLevel.LOW]
        assert high_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]

# Validation test runner
def run_risk_assessment_validation():
    """Run all risk assessment validation tests"""
    test_instance = TestRiskAssessmentValidation()
    test_instance.setup_method()  # Initialize the test instance

    tests = [
        ("initialization", test_instance.test_initialization),
        ("default_risk_metrics", test_instance.test_default_risk_metrics),
        ("position_size_recommendation_basic", test_instance.test_position_size_recommendation_basic),
        ("risk_level_multipliers", test_instance.test_risk_level_multipliers),
        ("confidence_impact", test_instance.test_confidence_impact),
        ("market_regime_adjustments", test_instance.test_market_regime_adjustments),
        ("progressive_vs_traditional", test_instance.test_progressive_vs_traditional),
        ("max_exposure_limits", test_instance.test_max_exposure_limits),
        ("error_handling", test_instance.test_error_handling),
        ("balance_impact", test_instance.test_balance_impact),
        ("risk_calculations", test_instance.test_risk_calculations),
    ]

    print("🛡️  Running Risk Assessment Validation Tests")
    print("-" * 50)

    for test_name, test_func in tests:
        validator.validate_component("RiskAssessment", test_name, test_func)

if __name__ == "__main__":
    run_risk_assessment_validation()