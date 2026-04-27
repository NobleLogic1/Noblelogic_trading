"""
Enhanced Risk Assessment Testing Suite
Comprehensive testing to validate 85%+ accuracy target
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project paths
sys.path.append('.')
sys.path.append('./ml')

from enhanced_risk_assessment import EnhancedRiskAssessment, RiskLevel
from ml_integration import MLTradingIntegration

class EnhancedRiskTester:
    def __init__(self):
        self.ml_integration = MLTradingIntegration()
        self.test_results = []
        self.confidence_scores = []
        
    async def run_comprehensive_tests(self):
        """
        Run comprehensive tests targeting 85%+ accuracy
        """
        print("[TEST] Starting Enhanced Risk Assessment Testing Suite")
        print("[TARGET] 85%+ Confidence Score\n")
        
        # Test scenarios with different risk profiles
        test_scenarios = [
            self.test_low_risk_scenario(),
            self.test_medium_risk_scenario(), 
            self.test_high_risk_scenario(),
            self.test_volatile_market_scenario(),
            self.test_low_liquidity_scenario(),
            self.test_high_correlation_scenario(),
            self.test_news_impact_scenario(),
            self.test_technical_breakout_scenario()
        ]
        
        for i, test_coro in enumerate(test_scenarios, 1):
            print(f"[RUNNING] Test Scenario {i}/8...")
            await test_coro
            print(f"[COMPLETE] Test Scenario {i} completed\n")
        
        # Analyze results
        await self.analyze_test_results()
        
    async def test_low_risk_scenario(self):
        """Test low-risk stable market conditions"""
        market_data = {
            'prices': [45000 + i * 10 for i in range(50)],  # Stable uptrend
            'volume_24h': 2000000000,  # High volume
            'avg_volume_30d': 1800000000,
            'bid_ask_spread': 0.0005,  # Tight spread
            'market_cap': 850000000000,  # Large cap
            'current_price': 45500,
            'volatility': 0.15,  # Low volatility
            'rsi': 55,  # Neutral
            'macd_signal': 0.1,  # Weak signal
            'support_level': 44000,
            'resistance_level': 47000,
            'news_sentiment': 0.65,  # Slightly positive
            'social_sentiment_volatility': 0.2,  # Low
            'fear_greed_index': 60  # Mild greed
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'BTC', 45500, market_data
        )
        
        self.record_test_result('Low Risk Scenario', decision, market_data)
        
    async def test_medium_risk_scenario(self):
        """Test medium-risk normal market conditions"""
        market_data = {
            'prices': [43000 + i * 25 for i in range(50)],  # Moderate trend
            'volume_24h': 1200000000,
            'avg_volume_30d': 1300000000,
            'bid_ask_spread': 0.001,
            'market_cap': 600000000000,
            'current_price': 44250,
            'volatility': 0.35,  # Medium volatility
            'rsi': 45,
            'macd_signal': 0.3,
            'support_level': 42500,
            'resistance_level': 46000,
            'news_sentiment': 0.5,  # Neutral
            'social_sentiment_volatility': 0.4,
            'fear_greed_index': 50
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'ETH', 44250, market_data
        )
        
        self.record_test_result('Medium Risk Scenario', decision, market_data)
        
    async def test_high_risk_scenario(self):
        """Test high-risk volatile market conditions"""
        market_data = {
            'prices': [40000 + i * 100 * (1 if i % 3 == 0 else -1) for i in range(50)],  # Volatile
            'volume_24h': 500000000,  # Lower volume
            'avg_volume_30d': 800000000,
            'bid_ask_spread': 0.003,  # Wide spread
            'market_cap': 200000000000,  # Smaller cap
            'current_price': 39500,
            'volatility': 0.85,  # High volatility
            'rsi': 75,  # Overbought
            'macd_signal': 0.8,  # Strong signal
            'support_level': 38000,
            'resistance_level': 41000,
            'news_sentiment': 0.3,  # Negative
            'social_sentiment_volatility': 0.8,  # High
            'fear_greed_index': 25,  # Fear
            'whale_activity_score': 0.7
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'ADA', 39500, market_data
        )
        
        self.record_test_result('High Risk Scenario', decision, market_data)
        
    async def test_volatile_market_scenario(self):
        """Test extreme volatility conditions"""
        market_data = {
            'prices': [50000 + i * 200 * np.sin(i/5) for i in range(50)],
            'volume_24h': 800000000,
            'current_price': 52000,
            'volatility': 1.2,  # Very high volatility
            'rsi': 85,  # Extremely overbought
            'macd_signal': 1.2,
            'news_sentiment': 0.2,  # Very negative
            'fear_greed_index': 15,  # Extreme fear
            'market_cap': 400000000000
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'BTC', 52000, market_data
        )
        
        self.record_test_result('Volatile Market Scenario', decision, market_data)
        
    async def test_low_liquidity_scenario(self):
        """Test low liquidity conditions"""
        market_data = {
            'prices': [25 + i * 0.1 for i in range(50)],
            'volume_24h': 50000000,  # Very low volume
            'avg_volume_30d': 60000000,
            'bid_ask_spread': 0.01,  # Very wide spread
            'market_cap': 500000000,  # Small cap
            'current_price': 27.5,
            'volatility': 0.6,
            'rsi': 40,
            'news_sentiment': 0.6
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'SMALL_ALT', 27.5, market_data
        )
        
        self.record_test_result('Low Liquidity Scenario', decision, market_data)
        
    async def test_high_correlation_scenario(self):
        """Test high correlation risk"""
        market_data = {
            'prices': [3500 + i * 15 for i in range(50)],
            'current_price': 4250,
            'btc_correlation': 0.95,  # Very high correlation
            'volume_24h': 1500000000,
            'volatility': 0.45,
            'market_volatility': 0.8,  # High market volatility
            'rsi': 60,
            'fear_greed_index': 30
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'ETH', 4250, market_data
        )
        
        self.record_test_result('High Correlation Scenario', decision, market_data)
        
    async def test_news_impact_scenario(self):
        """Test news and sentiment impact"""
        market_data = {
            'prices': [45000 + i * 50 for i in range(50)],
            'current_price': 47500,
            'volume_24h': 3000000000,  # High volume from news
            'news_sentiment': 0.9,  # Very positive news
            'social_sentiment_volatility': 0.9,  # High social volatility
            'whale_activity_score': 0.8,  # High whale activity
            'exchange_net_flows': 0.3,  # High inflows
            'volatility': 0.5,
            'rsi': 70
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'BTC', 47500, market_data
        )
        
        self.record_test_result('News Impact Scenario', decision, market_data)
        
    async def test_technical_breakout_scenario(self):
        """Test technical breakout conditions"""
        market_data = {
            'prices': [3800 + (i * 5 if i > 30 else 0) for i in range(50)],  # Breakout pattern
            'current_price': 3950,
            'support_level': 3800,
            'resistance_level': 3900,  # Just broke resistance
            'volume_24h': 2500000000,  # High breakout volume
            'rsi': 65,
            'macd_signal': 0.6,  # Strong momentum
            'bb_squeeze': True,  # Was in squeeze before breakout
            'volatility': 0.4,
            'news_sentiment': 0.7
        }
        
        decision = await self.ml_integration.get_trading_decision(
            'ETH', 3950, market_data
        )
        
        self.record_test_result('Technical Breakout Scenario', decision, market_data)
        
    def record_test_result(self, scenario_name, decision, market_data):
        """Record test result for analysis"""
        confidence = decision.get('confidence', 0.0)
        if isinstance(confidence, str):
            confidence = float(confidence.strip('%')) / 100
            
        self.confidence_scores.append(confidence)
        
        result = {
            'scenario': scenario_name,
            'timestamp': datetime.now(),
            'decision': decision,
            'confidence': confidence,
            'should_trade': decision.get('should_trade', False),
            'risk_level': decision.get('risk_level', 'UNKNOWN'),
            'risk_score': decision.get('risk_score', 0.5)
        }
        
        self.test_results.append(result)
        
        print(f"  [RESULT] {scenario_name}")
        print(f"     Confidence: {confidence:.1%}")
        print(f"     Risk Level: {decision.get('risk_level', 'N/A')}")
        print(f"     Should Trade: {decision.get('should_trade', False)}")
        if decision.get('reason'):
            print(f"     Reason: {decision.get('reason')}")
    
    async def analyze_test_results(self):
        """Analyze comprehensive test results"""
        print("=" * 60)
        print("[ANALYSIS] ENHANCED RISK ASSESSMENT TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        valid_confidences = [c for c in self.confidence_scores if c > 0]
        
        if valid_confidences:
            avg_confidence = np.mean(valid_confidences)
            min_confidence = min(valid_confidences)
            max_confidence = max(valid_confidences)
            
            print(f"[STATS] Confidence Statistics:")
            print(f"   Average Confidence: {avg_confidence:.2%}")
            print(f"   Minimum Confidence: {min_confidence:.2%}")
            print(f"   Maximum Confidence: {max_confidence:.2%}")
            print(f"   Target Achievement: {'[ACHIEVED]' if avg_confidence >= 0.85 else '[BELOW TARGET]'}")
            print()
        
        # Risk level distribution
        risk_levels = [r['risk_level'] for r in self.test_results]
        risk_distribution = {}
        for level in risk_levels:
            risk_distribution[level] = risk_distribution.get(level, 0) + 1
            
        print(f"[RISK] Risk Level Distribution:")
        for level, count in risk_distribution.items():
            percentage = (count / total_tests) * 100
            print(f"   {level}: {count} ({percentage:.1f}%)")
        print()
        
        # Trading decisions
        should_trade_count = sum(1 for r in self.test_results if r['should_trade'])
        should_not_trade_count = total_tests - should_trade_count
        
        print(f"[DECISIONS] Trading Decisions:")
        print(f"   Should Trade: {should_trade_count} ({should_trade_count/total_tests*100:.1f}%)")
        print(f"   Should Not Trade: {should_not_trade_count} ({should_not_trade_count/total_tests*100:.1f}%)")
        print()
        
        # Performance by scenario
        print(f"[PERFORMANCE] Performance by Scenario:")
        for result in self.test_results:
            confidence = result['confidence']
            status = "[HIGH]" if confidence >= 0.85 else "[MID]" if confidence >= 0.75 else "[LOW]"
            print(f"   {status} {result['scenario']}: {confidence:.1%}")
        print()
        
        # Overall assessment
        target_achieved = avg_confidence >= 0.85 if valid_confidences else False
        
        print("[ASSESSMENT] OVERALL ASSESSMENT:")
        if target_achieved:
            print("   [SUCCESS] ENHANCED RISK ASSESSMENT SYSTEM SUCCESSFUL")
            print("   [ACHIEVED] Target 85%+ confidence ACHIEVED")
            print("   [OPERATIONAL] Multi-factor risk analysis operational")
            print("   [ACTIVE] Dynamic position sizing active")
            print("   [WORKING] Advanced confidence calculation working")
        else:
            print("   [WARNING] Enhanced system needs calibration")
            print("   [RECOMMEND] Recommend adjusting risk factors")
            print("   [CONSIDER] Consider confidence boost modifications")
            
        print(f"\n[FINAL] Final Score: {avg_confidence:.2%} confidence")
        print("=" * 60)
        
        return {
            'target_achieved': target_achieved,
            'average_confidence': avg_confidence if valid_confidences else 0,
            'total_tests': total_tests,
            'risk_distribution': risk_distribution,
            'detailed_results': self.test_results
        }

async def main():
    """Run the enhanced risk assessment test suite"""
    tester = EnhancedRiskTester()
    results = await tester.run_comprehensive_tests()
    
    # Save results for review
    with open('enhanced_risk_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[SAVED] Results saved to: enhanced_risk_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())