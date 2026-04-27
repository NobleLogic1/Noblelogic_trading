#!/usr/bin/env python3
"""
ML Engine Test Script
Tests model checkpointing, versioning, batch inference, and mixed precision
"""

import asyncio
import time
import numpy as np
from ml_integration import GPUAcceleratedMLEngine
import os
import json

async def test_ml_engine_features():
    """Test all new ML engine features"""
    print("\n🚀 TESTING ENHANCED ML ENGINE FEATURES")
    print("=" * 50)
    
    # Initialize ML engine
    ml_engine = GPUAcceleratedMLEngine()
    
    # Test single prediction
    print("\n1. TESTING SINGLE PREDICTION")
    print("-" * 40)
    
    features = np.random.uniform(0, 1, (1, 10)).astype(np.float32)
    prediction = await ml_engine.predict(features)
    print(f"Single prediction result: {prediction}")
    
    # Test batch prediction
    print("\n2. TESTING BATCH PREDICTION")
    print("-" * 40)
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
    batch_results = await ml_engine.batch_predict_multiple_symbols(symbols)
    
    print(f"Batch prediction meta: {batch_results.get('_meta', {})}")
    for symbol in symbols:
        if symbol in batch_results:
            print(f"{symbol}: {batch_results[symbol].get('action')} with {batch_results[symbol].get('confidence'):.1%} confidence")
    
    # Test model updating and checkpointing
    print("\n3. TESTING MODEL UPDATING & CHECKPOINTING")
    print("-" * 40)
    
    for i in range(15):  # Simulate 15 trades to trigger checkpointing
        # Create simulated trade result
        trade_result = {
            'profit': (i % 3) * 10,  # Some trades win, some lose
            'trade_id': f"test_trade_{i}",
            'symbol': 'BTC/USDT'
        }
        
        # Update model with trade result
        await ml_engine.update_model(features, 1 if trade_result['profit'] > 0 else 0, trade_result)
        
        # Small delay between updates
        await asyncio.sleep(0.1)
        
        if i % 5 == 0:
            print(f"Processed {i+1} updates")
    
    # Test mixed precision
    print("\n4. TESTING MIXED PRECISION")
    print("-" * 40)
    
    # Show current precision policy
    precision_mode = "Mixed Precision" if ml_engine.mixed_precision_enabled else "Full Precision (float32)"
    print(f"Current precision mode: {precision_mode}")
    
    # Measure performance
    start_time = time.time()
    for _ in range(10):
        features = np.random.uniform(0, 1, (1, 10)).astype(np.float32)
        await ml_engine.predict(features)
    end_time = time.time()
    
    avg_time = (end_time - start_time) * 100  # ms
    print(f"Average prediction time: {avg_time:.2f}ms (for 10 predictions)")
    
    # Show model info
    print("\n5. MODEL VERSIONING INFORMATION")
    print("-" * 40)
    
    print(f"Current model version: v{ml_engine.version}")
    print(f"Performance history entries: {len(ml_engine.performance_history)}")
    
    print("\n✅ ML ENGINE TESTING COMPLETE\n")
    
if __name__ == "__main__":
    asyncio.run(test_ml_engine_features())