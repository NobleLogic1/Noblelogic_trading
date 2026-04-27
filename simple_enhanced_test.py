"""
Simple Enhanced Risk Assessment Test
Test the enhanced system without Unicode characters
"""

import asyncio
import sys
sys.path.append('.')

async def test_enhanced_system():
    """Test the enhanced risk assessment system"""
    try:
        from ml_integration import MLTradingIntegration
        
        print("[TEST] Testing Enhanced Risk Assessment System")
        print("[TARGET] 85%+ Confidence Achievement")
        
        # Initialize ML integration with enhanced risk assessment
        ml_system = MLTradingIntegration()
        
        # Test with sample market data
        market_data = {
            'prices': [45000, 45100, 45200, 45300, 45400],
            'volume_24h': 2000000000,
            'current_price': 45400,
            'volatility': 0.35,
            'rsi': 55,
            'macd_signal': 0.2,
            'news_sentiment': 0.6,
            'fear_greed_index': 60,
            'market_cap': 850000000000
        }
        
        # Get trading decision
        print("\n[PROCESSING] Getting enhanced trading decision...")
        decision = await ml_system.get_trading_decision('BTC', 45400, market_data)
        
        print(f"[RESULT] Trading Decision:")
        print(f"  Should Trade: {decision.get('should_trade', False)}")
        print(f"  Confidence: {decision.get('confidence', 0):.2%}")
        print(f"  Risk Level: {decision.get('risk_level', 'N/A')}")
        print(f"  Reason: {decision.get('reason', 'N/A')}")
        
        # Check if we achieved 85%+ confidence
        confidence = decision.get('confidence', 0)
        if isinstance(confidence, str):
            confidence = float(confidence.strip('%')) / 100
            
        target_achieved = confidence >= 0.85
        print(f"\n[ASSESSMENT] Target Achievement: {'SUCCESS' if target_achieved else 'NEEDS IMPROVEMENT'}")
        print(f"[FINAL] Confidence Score: {confidence:.2%}")
        
        return {
            'success': True,
            'confidence': confidence,
            'target_achieved': target_achieved,
            'decision': decision
        }
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

# Run the test
result = asyncio.run(test_enhanced_system())
print(f"\n[COMPLETE] Test result: {result}")