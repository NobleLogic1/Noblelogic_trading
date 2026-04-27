"""
Test script to validate the enhanced risk assessment system
with dynamic thresholds, correlation analysis, and market regime detection
"""

import asyncio
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from enhanced_risk_assessment import EnhancedRiskAssessment, RiskLevel

async def test_dynamic_risk_thresholds():
    """
    Test the dynamic risk threshold functionality
    """
    print("\n==== Testing Dynamic Risk Thresholds ====")
    risk_system = EnhancedRiskAssessment()
    
    # Generate some sample risk history to populate thresholds
    for i in range(30):
        # Create fluctuating risk metrics
        cycle = np.sin(i/5) * 0.2 + 0.5  # Oscillating between ~0.3-0.7
        
        risk_entry = {
            'timestamp': (datetime.now() - timedelta(days=30-i)).isoformat(),
            'symbol': 'BTC/USD',
            'overall': cycle,
            'volatility': cycle * 1.1,
            'liquidity': cycle * 0.9,
            'market': cycle * 1.2,
            'technical': cycle * 0.8,
            'sentiment': cycle * 1.3,
            'concentration': cycle * 0.7,
            'correlation': cycle * 1.0,
            'drawdown': cycle * 0.5,
            'market_regime': 'VOLATILE' if cycle > 0.6 else 'NORMAL'
        }
        risk_system.risk_history.append(risk_entry)
    
    # Test calculation of dynamic thresholds
    factors = ['volatility', 'liquidity', 'market', 'technical', 'sentiment', 
               'correlation', 'concentration', 'drawdown']
    
    print("Dynamic risk thresholds vs baseline:")
    for factor in factors:
        dynamic = risk_system._calculate_dynamic_threshold(factor)
        baseline = risk_system.baseline_thresholds[factor]
        print(f"  {factor}: {dynamic:.3f} (baseline: {baseline:.3f}, "
              f"delta: {(dynamic-baseline)/baseline*100:.1f}%)")

async def test_correlation_analysis():
    """
    Test the enhanced correlation analysis functionality
    """
    print("\n==== Testing Enhanced Correlation Analysis ====")
    risk_system = EnhancedRiskAssessment()
    
    # Create synthetic return data for multiple assets
    np.random.seed(42)  # For reproducibility
    
    # Generate correlated return series
    n_days = 100
    
    # Base returns (market factor)
    market_returns = np.random.normal(0.0005, 0.01, n_days)
    
    # Asset-specific returns with varying correlation to market
    asset_returns = {
        'BTC/USD': market_returns * 1.2 + np.random.normal(0, 0.02, n_days),  # High correlation
        'ETH/USD': market_returns * 1.1 + np.random.normal(0, 0.025, n_days),  # High correlation
        'XRP/USD': market_returns * 0.7 + np.random.normal(0, 0.03, n_days),   # Medium correlation
        'SOL/USD': market_returns * 0.5 + np.random.normal(0, 0.035, n_days),  # Lower correlation
        'GOLD': market_returns * -0.3 + np.random.normal(0, 0.005, n_days),    # Negative correlation
    }
    
    portfolio_data = {
        'crypto_exposure': 0.8,
        'same_sector_exposure': 0.6,
        'cross_asset_correlation': 0.3,
        'asset_returns': asset_returns
    }
    
    # Test correlation calculation
    symbol = 'BTC/USD'
    correlation_risk = await risk_system._assess_correlation_risk(symbol, portfolio_data)
    
    print(f"Correlation risk score for {symbol}: {correlation_risk:.4f}")
    print(f"Portfolio correlation matrix:")
    if hasattr(risk_system, 'portfolio_correlation_matrix') and risk_system.portfolio_correlation_matrix:
        # Pretty print the correlation matrix
        df = pd.DataFrame(risk_system.portfolio_correlation_matrix)
        print(df.round(2))
    else:
        print("No correlation matrix was calculated")

async def test_market_regime_detection():
    """
    Test the market regime detection functionality
    """
    print("\n==== Testing Market Regime Detection ====")
    risk_system = EnhancedRiskAssessment()
    
    # Generate price series with different regimes
    n_days = 200
    base_price = 10000
    prices = [base_price]
    
    # Create different market regimes
    # Days 0-50: Bull market
    for i in range(50):
        daily_return = np.random.normal(0.008, 0.02)  # Positive drift, medium vol
        prices.append(prices[-1] * (1 + daily_return))
    
    # Days 50-100: Euphoria (stronger bull with increasing volatility)
    for i in range(50):
        daily_return = np.random.normal(0.015, 0.03)  # Stronger positive drift, higher vol
        prices.append(prices[-1] * (1 + daily_return))
    
    # Days 100-150: Crash/Bear
    for i in range(50):
        daily_return = np.random.normal(-0.012, 0.045)  # Negative drift, high vol
        prices.append(prices[-1] * (1 + daily_return))
    
    # Days 150-200: Recovery
    for i in range(50):
        daily_return = np.random.normal(0.005, 0.025)  # Mild positive drift, medium vol
        prices.append(prices[-1] * (1 + daily_return))
    
    # Test market regime detection at different points
    test_points = [40, 90, 140, 190]
    regimes = []
    
    for point in test_points:
        # Create market data with trailing price history
        market_data = {
            'price_history': prices[max(0, point-90):point+1],
            'fear_greed_index': 70 if point < 100 else 30
        }
        
        # Detect regime
        risk_system._detect_market_regime(market_data)
        regimes.append(risk_system.market_regime)
        
        # Print info about this period
        period_returns = np.diff(market_data['price_history']) / market_data['price_history'][:-1]
        vol = np.std(period_returns)
        avg_return = np.mean(period_returns)
        
        print(f"Day {point}:")
        print(f"  Average daily return: {avg_return*100:.2f}%")
        print(f"  Volatility: {vol*100:.2f}%")
        print(f"  Detected regime: {risk_system.market_regime}")
        print()
    
    # Test position size recommendations in different regimes
    print("Position size recommendations in different regimes:")
    risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    base_position = 1000  # $1000 base position
    
    for i, point in enumerate(test_points):
        risk_system.market_regime = regimes[i]
        print(f"\nRegime: {risk_system.market_regime}")
        
        for risk_level in risk_levels:
            # Create a simple risk metrics object
            from enhanced_risk_assessment import RiskMetrics
            risk_metrics = RiskMetrics(
                overall_score=0.5,
                volatility_risk=0.5,
                liquidity_risk=0.5,
                market_risk=0.5,
                technical_risk=0.5,
                sentiment_risk=0.5,
                concentration_risk=0.5,
                correlation_risk=0.5,
                drawdown_risk=0.5,
                risk_level=risk_level,
                confidence=0.85,
                recommendations=[]
            )
            
            recommendation = risk_system.get_position_size_recommendation(risk_metrics, base_position)
            print(f"  Risk Level {risk_level.name}:")
            print(f"    Position: ${recommendation['risk_adjusted_position']:.2f}")
            print(f"    Adjustment: {recommendation['regime_adjustment']:.2f}x due to {recommendation['market_regime']} regime")

async def main():
    """
    Run all tests
    """
    print("Testing Enhanced Risk Assessment System")
    print("======================================")
    
    await test_dynamic_risk_thresholds()
    await test_correlation_analysis()
    await test_market_regime_detection()
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    asyncio.run(main())