#!/usr/bin/env python3
"""
GPU-Accelerated Trading System Validation Test
============================================
Comprehensive test of GPU acceleration, ML integration, and API connectivity
"""

import asyncio
import json
import time
import requests
from ml_integration import GPUAcceleratedMLEngine
from live_data_fetcher import LiveDataFetcher
import numpy as np

class GPUSystemValidator:
    def __init__(self):
        self.results = {}
        
    async def test_gpu_ml_system(self):
        """Test GPU-accelerated ML system"""
        print("🧠 Testing GPU-Accelerated ML System...")
        
        try:
            # Initialize GPU ML engine
            ml_engine = GPUAcceleratedMLEngine()
            
            # Generate test data
            test_data = {
                'price': np.random.uniform(45000, 55000, 100),
                'volume': np.random.uniform(1000000, 10000000, 100),
                'rsi': np.random.uniform(20, 80, 100),
                'macd': np.random.uniform(-500, 500, 100)
            }
            
            # Test ML prediction
            start_time = time.time()
            prediction = await ml_engine.predict(test_data)
            prediction_time = time.time() - start_time
            
            self.results['gpu_ml'] = {
                'status': 'success',
                'prediction_confidence': prediction.get('confidence', 0),
                'prediction_time_ms': prediction_time * 1000,
                'gpu_available': ml_engine.gpu_available,
                'signal': prediction.get('signal', 'hold')
            }
            
            print(f"✅ GPU ML System: {prediction['confidence']:.2f}% confidence in {prediction_time*1000:.1f}ms")
            
        except Exception as e:
            self.results['gpu_ml'] = {'status': 'error', 'error': str(e)}
            print(f"❌ GPU ML System Error: {e}")
    
    def test_api_connectivity(self):
        """Test Binance.US API connectivity"""
        print("🌐 Testing Binance.US API Connectivity...")
        
        try:
            fetcher = LiveDataFetcher()
            # Test getting multiple prices
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            data = fetcher.get_multiple_prices(symbols)
            
            self.results['api_binance'] = {
                'status': 'success',
                'symbols_count': len(data),
                'sample_prices': {k: v for k, v in list(data.items())[:3]},
                'connectivity': 'operational'
            }
            
            print(f"✅ Binance.US API: {len(data)} symbols retrieved")
            if data:
                for symbol, price in list(data.items())[:2]:
                    print(f"   └─ {symbol}: ${price:.2f}")
            
        except Exception as e:
            self.results['api_binance'] = {'status': 'error', 'error': str(e)}
            print(f"❌ Binance.US API Error: {e}")
    
    def test_backend_endpoints(self):
        """Test backend GPU status and endpoints"""
        print("🖥️ Testing Backend GPU Integration...")
        
        try:
            # Test health endpoint
            health_response = requests.get('http://localhost:3001/api/health', timeout=5)
            health_data = health_response.json()
            
            # Test chart data endpoint
            chart_response = requests.get('http://localhost:3001/api/chart-data', timeout=5)
            chart_data = chart_response.json()
            
            self.results['backend'] = {
                'status': 'success',
                'gpu_acceleration': health_data.get('gpu_acceleration', False),
                'gpu_status': health_data.get('gpu_status', 'Unknown'),
                'chart_data_points': len(chart_data.get('data', [])),
                'health_status': health_data.get('status', 'unknown')
            }
            
            print(f"✅ Backend: GPU={health_data.get('gpu_status', 'Unknown')}, Chart points={len(chart_data.get('data', []))}")
            
        except Exception as e:
            self.results['backend'] = {'status': 'error', 'error': str(e)}
            print(f"❌ Backend Error: {e}")
    
    def test_gpu_capabilities(self):
        """Test GPU detection and capabilities"""
        print("🎮 Testing GPU Detection...")
        
        try:
            # Test TensorFlow GPU detection
            import tensorflow as tf
            
            gpu_devices = tf.config.experimental.list_physical_devices('GPU')
            cpu_devices = tf.config.experimental.list_physical_devices('CPU')
            
            # Test WebGL capabilities (simulation)
            webgl_support = True  # In real browser this would be detected via JavaScript
            
            self.results['gpu_capabilities'] = {
                'tensorflow_gpus': len(gpu_devices),
                'tensorflow_cpus': len(cpu_devices),
                'webgl_support': webgl_support,
                'gpu_names': [device.name for device in gpu_devices] if gpu_devices else ['No GPU detected']
            }
            
            if gpu_devices:
                print(f"✅ GPU Detection: {len(gpu_devices)} GPU(s) found")
                for gpu in gpu_devices:
                    print(f"   └─ {gpu.name}")
            else:
                print("⚠️ GPU Detection: No CUDA GPUs found, using CPU optimization")
            
        except Exception as e:
            self.results['gpu_capabilities'] = {'status': 'error', 'error': str(e)}
            print(f"❌ GPU Detection Error: {e}")
    
    async def run_comprehensive_test(self):
        """Run complete system validation"""
        print("🚀 GPU-Accelerated Trading System Validation")
        print("=" * 50)
        
        # Run all tests
        await self.test_gpu_ml_system()
        self.test_api_connectivity()
        self.test_backend_endpoints()
        self.test_gpu_capabilities()
        
        # Generate summary report
        print("\n📊 SYSTEM VALIDATION REPORT")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result.get('status') == 'success')
        
        print(f"Overall Status: {successful_tests}/{total_tests} tests passed")
        
        if self.results.get('gpu_ml', {}).get('status') == 'success':
            ml_result = self.results['gpu_ml']
            print(f"ML Confidence: {ml_result['prediction_confidence']:.1f}%")
            print(f"GPU Acceleration: {'Enabled' if ml_result['gpu_available'] else 'CPU Fallback'}")
        
        if self.results.get('backend', {}).get('status') == 'success':
            backend_result = self.results['backend']
            print(f"Backend GPU Status: {backend_result['gpu_status']}")
        
        # Save results
        with open('gpu_system_validation_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n✅ Validation complete! Results saved to 'gpu_system_validation_results.json'")
        
        return successful_tests == total_tests

if __name__ == "__main__":
    validator = GPUSystemValidator()
    success = asyncio.run(validator.run_comprehensive_test())
    
    if success:
        print("\n🎉 ALL SYSTEMS OPERATIONAL - GPU-ACCELERATED TRADING SYSTEM READY!")
    else:
        print("\n⚠️ Some components need attention - Check validation results")