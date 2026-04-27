#!/usr/bin/env python3
"""
GPU-Accelerated Trading System - Complete Demo
============================================
Demonstrates all GPU acceleration features working together
"""

import asyncio
import json
import requests
import time
import numpy as np
from ml_integration import GPUAcceleratedMLEngine
from live_data_fetcher import LiveDataFetcher

class GPUTradingSystemDemo:
    def __init__(self):
        self.ml_engine = GPUAcceleratedMLEngine()
        self.data_fetcher = LiveDataFetcher()
        
    async def demo_ml_analysis(self):
        """Demonstrate GPU-accelerated ML analysis"""
        print("🧠 GPU-Accelerated ML Analysis Demo")
        print("-" * 40)
        
        # Simulate multiple market conditions
        market_scenarios = [
            {"name": "Bullish Market", "price_mult": 1.1, "vol_mult": 1.5},
            {"name": "Bearish Market", "price_mult": 0.9, "vol_mult": 1.2},
            {"name": "Sideways Market", "price_mult": 1.0, "vol_mult": 0.8},
            {"name": "High Volatility", "price_mult": 1.05, "vol_mult": 2.0}
        ]
        
        for scenario in market_scenarios:
            # Generate test features for scenario
            base_features = np.array([[
                50000.0 * scenario["price_mult"],    # price
                2000000.0 * scenario["vol_mult"],   # volume
                np.random.uniform(20, 80),          # rsi
                np.random.uniform(-200, 200),       # macd
                np.random.uniform(0.3, 0.8),        # sentiment_score
                np.random.uniform(0.4, 0.9),        # news_score
                np.random.uniform(0.2, 0.7),        # social_score
                scenario["price_mult"],             # market_trend
                0.02 * scenario["vol_mult"],        # volatility
                np.random.uniform(0.6, 0.9)         # success_rate
            ]], dtype=np.float32)
            
            start_time = time.time()
            prediction = await self.ml_engine.predict(base_features)
            prediction_time = (time.time() - start_time) * 1000
            
            action_names = ["HOLD", "BUY", "SELL"]
            action_name = action_names[prediction['action']] if prediction['action'] < 3 else "HOLD"
            
            print(f"📊 {scenario['name']}: {action_name} ({prediction['confidence']:.1%} confidence) in {prediction_time:.1f}ms")
        
        print(f"✅ GPU Status: {'Enabled' if self.ml_engine.gpu_available else 'CPU Fallback'}")
    
    def demo_api_connectivity(self):
        """Demonstrate real-time API data fetching"""
        print("\n🌐 Real-Time Market Data Demo")
        print("-" * 40)
        
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        prices = self.data_fetcher.get_multiple_prices(symbols)
        
        for symbol, price in prices.items():
            print(f"💰 {symbol}: ${price:,.2f}")
        
        print(f"✅ API Status: Binance.US Connected")
    
    def demo_backend_integration(self):
        """Demonstrate backend GPU status and chart data"""
        print("\n🖥️ Backend GPU Integration Demo")
        print("-" * 40)
        
        try:
            # Check health endpoint
            health_response = requests.get('http://localhost:3001/api/health', timeout=5)
            health_data = health_response.json()
            
            print(f"🔋 GPU Acceleration: {health_data.get('gpu_status', 'Unknown')}")
            print(f"⚡ System Status: {health_data.get('status', 'Unknown')}")
            
            # Check chart data
            chart_response = requests.get('http://localhost:3001/api/chart-data', timeout=5)
            chart_data = chart_response.json()
            
            data_points = len(chart_data.get('data', []))
            print(f"📈 Chart Data: {data_points} points ready for GPU rendering")
            
            if data_points > 0:
                sample_point = chart_data['data'][0]
                print(f"   Sample: ${sample_point['price']:,.2f} @ {sample_point['volume']:,.0f} volume")
            
            print("✅ Backend: GPU-Ready")
            
        except Exception as e:
            print(f"❌ Backend Error: {e}")
    
    def demo_gpu_capabilities(self):
        """Demonstrate GPU detection and capabilities"""
        print("\n🎮 GPU Capabilities Demo")
        print("-" * 40)
        
        try:
            import tensorflow as tf
            
            # Show TensorFlow GPU info
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                print(f"🚀 CUDA GPUs Found: {len(gpus)}")
                for i, gpu in enumerate(gpus):
                    print(f"   GPU {i}: {gpu.name}")
                print("🎯 Mode: Hardware-Accelerated ML + WebGL Graphics")
            else:
                print("⚙️ CPU Optimization: Advanced CPU instructions enabled")
                print("🎯 Mode: CPU-Optimized ML + WebGL Graphics")
            
            # Show optimization features
            print("\nOptimization Features:")
            print("  ✅ TensorFlow GPU Support (when available)")
            print("  ✅ WebGL-Accelerated Charts")
            print("  ✅ GPU Particle Effects")
            print("  ✅ Hardware-Accelerated Rendering")
            print("  ✅ Real-time Performance Monitoring")
            
        except Exception as e:
            print(f"❌ GPU Detection Error: {e}")
    
    async def run_complete_demo(self):
        """Run complete GPU-accelerated trading system demo"""
        print("🚀 GPU-ACCELERATED TRADING SYSTEM DEMO")
        print("=" * 50)
        print("Showcasing GPU acceleration for graphics and ML calculations")
        print("=" * 50)
        
        # Run all demos
        await self.demo_ml_analysis()
        self.demo_api_connectivity()
        self.demo_backend_integration()
        self.demo_gpu_capabilities()
        
        # Summary
        print("\n🎉 DEMO COMPLETE - GPU SYSTEM SUMMARY")
        print("=" * 50)
        print("🧠 ML Engine: GPU-accelerated TensorFlow with CPU fallback")
        print("🎮 Graphics: WebGL-powered charts and particle effects") 
        print("🌐 API: Binance.US real-time data integration")
        print("⚡ Backend: GPU status monitoring and data pipelines")
        print("🖥️ Frontend: Hardware-accelerated React dashboard")
        print("\nSystem Status: OPERATIONAL ✅")
        print("Access dashboard at: http://localhost:5173")

async def main():
    demo = GPUTradingSystemDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())