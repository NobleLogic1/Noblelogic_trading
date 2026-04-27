#!/usr/bin/env python3
"""
GPU/CUDA Test Script for NobleLogic Trading System
Tests PyTorch and TensorFlow GPU acceleration capabilities
"""

import torch
import tensorflow as tf
import time
import numpy as np

def test_pytorch_cuda():
    """Test PyTorch CUDA functionality"""
    print("="*60)
    print("🔥 PYTORCH CUDA TEST")
    print("="*60)
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"Device Count: {torch.cuda.device_count()}")
        print(f"Current Device: {torch.cuda.current_device()}")
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        print(f"Memory Allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        print(f"Memory Reserved: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB")
        
        # Performance test
        print("\n🚀 Running PyTorch GPU Performance Test...")
        device = torch.device('cuda')
        
        # Create large tensors on GPU
        start_time = time.time()
        a = torch.randn(5000, 5000, device=device)
        b = torch.randn(5000, 5000, device=device)
        c = torch.matmul(a, b)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        
        print(f"GPU Matrix Multiplication (5000x5000): {gpu_time:.4f} seconds")
        
        # CPU comparison
        start_time = time.time()
        a_cpu = torch.randn(5000, 5000)
        b_cpu = torch.randn(5000, 5000)
        c_cpu = torch.matmul(a_cpu, b_cpu)
        cpu_time = time.time() - start_time
        
        print(f"CPU Matrix Multiplication (5000x5000): {cpu_time:.4f} seconds")
        print(f"GPU Speedup: {cpu_time/gpu_time:.2f}x faster")
        
    else:
        print("❌ CUDA not available for PyTorch")

def test_tensorflow_gpu():
    """Test TensorFlow GPU functionality"""
    print("\n" + "="*60)
    print("🔥 TENSORFLOW GPU TEST")
    print("="*60)
    
    try:
        import tensorflow as tf
        print("✅ TensorFlow imported successfully")
        
        # Skip detailed tests for now due to installation issues
        print("⚠️  TensorFlow GPU testing skipped - installation needs verification")
        
    except ImportError as e:
        print(f"❌ TensorFlow not available: {e}")

def test_gpu_memory():
    """Test GPU memory usage"""
    print("\n" + "="*60)
    print("💾 GPU MEMORY TEST")
    print("="*60)
    
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        
        for gpu in gpus:
            print(f"GPU {gpu.id}: {gpu.name}")
            print(f"Memory Total: {gpu.memoryTotal} MB")
            print(f"Memory Used: {gpu.memoryUsed} MB")
            print(f"Memory Free: {gpu.memoryFree} MB")
            print(f"GPU Load: {gpu.load*100:.1f}%")
            print(f"Temperature: {gpu.temperature}°C")
            
    except ImportError:
        print("GPUtil not available for detailed memory stats")

if __name__ == "__main__":
    print("🎮 NobleLogic Trading System - GPU/CUDA Test")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_pytorch_cuda()
    test_tensorflow_gpu()
    test_gpu_memory()
    
    print("\n" + "="*60)
    print("✅ GPU/CUDA Test Complete!")
    print("="*60)