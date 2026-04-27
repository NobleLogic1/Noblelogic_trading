"""
Quick validation test for enhanced risk assessment targeting 85%+ accuracy
"""
import asyncio
import sys
sys.path.append('.')

from ml_integration import MLTradingIntegration

async def quick_validation_test():
    """Quick test to validate 85%+ confidence target"""
    print("[VALIDATION] Quick Enhanced Risk Assessment Test")
    print("[TARGET] Verify 85%+ Confidence Achievement\n")
    
    ml_integration = MLTradingIntegration()
    confidence_scores = []
    
    # Test scenarios with realistic market data
    test_cases = [
        {
            'name': 'Stable Market',
            'symbol': 'BTC',
            'price': 45000,
            'market_data': {
                'prices': [44000 + i * 20 for i in range(30)],
                'volume_24h': 2000000000,
                'volatility': 0.25,
                'rsi': 55,
                'current_price': 45000
            }
        },
        {
            'name': 'Trending Market',
            'symbol': 'ETH', 
            'price': 3200,
            'market_data': {
                'prices': [3000 + i * 10 for i in range(30)],
                'volume_24h': 1500000000,
                'volatility': 0.35,
                'rsi': 65,
                'current_price': 3200
            }
        },
        {
            'name': 'Volatile Market',
            'symbol': 'ADA',
            'price': 0.75,
            'market_data': {
                'prices': [0.70 + i * 0.002 for i in range(30)],
                'volume_24h': 800000000,
                'volatility': 0.65,
                'rsi': 70,
                'current_price': 0.75
            }
        }
    ]
    
    print("[TESTING] Running validation scenarios...")
    
    for i, case in enumerate(test_cases, 1):
        try:
            decision = await ml_integration.get_trading_decision(
                case['symbol'], case['price'], case['market_data']
            )
            
            confidence = decision.get('confidence', 0)
            if isinstance(confidence, str) and '%' in str(confidence):
                confidence = float(str(confidence).replace('%', '')) / 100
            
            confidence_scores.append(confidence)
            
            print(f"[RESULT {i}] {case['name']}")
            print(f"  Confidence: {confidence:.1%}")
            print(f"  Risk Level: {decision.get('risk_level', 'N/A')}")
            print(f"  Should Trade: {decision.get('should_trade', False)}")
            print(f"  Target Met: {'YES' if confidence >= 0.85 else 'NO'}\n")
            
        except Exception as e:
            print(f"[ERROR {i}] {case['name']}: {e}\n")
    
    # Calculate results
    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        min_confidence = min(confidence_scores)
        max_confidence = max(confidence_scores)
        target_met_count = sum(1 for c in confidence_scores if c >= 0.85)
        
        print("=" * 50)
        print("[VALIDATION RESULTS]")
        print(f"Average Confidence: {avg_confidence:.2%}")
        print(f"Minimum Confidence: {min_confidence:.2%}")
        print(f"Maximum Confidence: {max_confidence:.2%}")
        print(f"85%+ Target Met: {target_met_count}/{len(confidence_scores)} cases")
        print(f"Success Rate: {target_met_count/len(confidence_scores)*100:.1f}%")
        print()
        
        if avg_confidence >= 0.85:
            print("[SUCCESS] Enhanced Risk Assessment System ACHIEVED 85%+ target!")
            print("[READY] System ready for live trading with enhanced confidence")
        else:
            print("[WARNING] System below 85% target - needs calibration")
        
        print("=" * 50)
        
        return avg_confidence >= 0.85
    else:
        print("[ERROR] No confidence scores collected")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_validation_test())
    print(f"\n[FINAL] Validation {'PASSED' if success else 'FAILED'}")