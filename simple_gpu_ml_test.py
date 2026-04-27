#!/usr/bin/env python3
"""
Quick GPU ML System Test
========================
Simple test of our GPU-accelerated ML system
"""

import asyncio
import numpy as np
import tensorflow as tf
from ml_integration import GPUAcceleratedMLEngine

async def test_gpu_ml_simple():
    """Simple test of GPU ML system with proper data format"""
    print("🧠 Testing GPU-Accelerated ML System (Simple)")
    
    # Initialize ML engine
    ml_engine = GPUAcceleratedMLEngine()
    
    # Test with proper tensor format (10 features as expected by model)
    test_features = np.array([[
        50000.0,    # price
        5000000.0,  # volume
        45.0,       # rsi
        100.0,      # macd
        0.6,        # sentiment_score
        0.7,        # news_score
        0.5,        # social_score
        0.6,        # market_trend
        0.025,      # volatility
        0.75        # success_rate
    ]], dtype=np.float32)
    
    print(f"Input features shape: {test_features.shape}")
    print(f"Sample values: {test_features[0][:5]}...")  # Show first 5 values
    
    try:
        # Test prediction (async)
        prediction = await ml_engine.predict(test_features)
        print(f"✅ Prediction successful!")
        print(f"   Action: {prediction.get('action', 'N/A')}")
        print(f"   Confidence: {prediction.get('confidence', 0):.1f}")
        print(f"   GPU Used: {prediction.get('gpu_used', False)}")
        print(f"   Reasoning: {prediction.get('reasoning', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gpu_ml_simple())
    if success:
        print("\n🎉 GPU ML System Test PASSED!")
    else:
        print("\n⚠️ GPU ML System Test FAILED!")