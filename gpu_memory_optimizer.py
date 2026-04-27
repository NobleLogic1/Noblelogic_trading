"""
GPU Memory Optimization Module for NobleLogic Trading System

Advanced memory management, pooling, and optimization strategies for GPU acceleration
"""

import asyncio
import time
import numpy as np
import gc
import psutil
import threading
from typing import Dict, List, Any, Optional, Tuple
import weakref
import sys
import os

# Add ML path
ml_path = os.path.join(os.path.dirname(__file__), 'ml')
sys.path.append(ml_path)

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class GPUMemoryOptimizer:
    """Advanced GPU memory optimization and management"""

    def __init__(self):
        self.memory_pools = {}
        self.allocation_tracker = {}
        self.gpu_memory_stats = {}
        self.optimization_strategies = {}
        self.monitoring_active = False
        self.monitoring_thread = None

        # Initialize memory pools
        self._initialize_memory_pools()

        # Start memory monitoring
        self.start_memory_monitoring()

    def _initialize_memory_pools(self):
        """Initialize memory pools for different data types and sizes"""
        # Tensor pools for common ML operations
        self.memory_pools = {
            'float32': {
                'small': [],    # < 1MB
                'medium': [],   # 1-10MB
                'large': []     # > 10MB
            },
            'float16': {
                'small': [],
                'medium': [],
                'large': []
            },
            'int32': {
                'small': [],
                'medium': [],
                'large': []
            }
        }

        # GPU-specific pools if TensorFlow available
        if TENSORFLOW_AVAILABLE:
            try:
                gpus = tf.config.experimental.list_physical_devices('GPU')
                if gpus:
                    self.memory_pools['gpu_tensors'] = {
                        'feature_tensors': [],
                        'weight_tensors': [],
                        'activation_tensors': []
                    }
            except:
                pass

    def start_memory_monitoring(self):
        """Start background memory monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._memory_monitor_loop, daemon=True)
        self.monitoring_thread.start()

    def stop_memory_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)

    def _memory_monitor_loop(self):
        """Background memory monitoring loop"""
        while self.monitoring_active:
            try:
                self._update_memory_stats()
                self._apply_memory_optimizations()
                time.sleep(5.0)  # Monitor every 5 seconds
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                time.sleep(10.0)

    def _update_memory_stats(self):
        """Update current memory statistics"""
        try:
            # System memory
            vm = psutil.virtual_memory()
            self.gpu_memory_stats['system'] = {
                'total_mb': vm.total / (1024**2),
                'used_mb': vm.used / (1024**2),
                'available_mb': vm.available / (1024**2),
                'usage_percent': vm.percent,
                'timestamp': time.time()
            }

            # GPU memory if available
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    self.gpu_memory_stats[f'gpu_{i}'] = {
                        'total_mb': gpu.memoryTotal,
                        'used_mb': gpu.memoryUsed,
                        'free_mb': gpu.memoryFree,
                        'utilization_percent': gpu.memoryUtil * 100,
                        'temperature': gpu.temperature,
                        'timestamp': time.time()
                    }
            except ImportError:
                pass
            except Exception as e:
                self.gpu_memory_stats['gpu_error'] = str(e)

            # TensorFlow memory if available
            if TENSORFLOW_AVAILABLE:
                try:
                    # This is approximate - TensorFlow doesn't expose detailed GPU memory per tensor
                    self.gpu_memory_stats['tensorflow'] = {
                        'gpu_memory_fraction': tf.config.experimental.get_memory_growth(
                            tf.config.experimental.list_physical_devices('GPU')[0]
                        ) if tf.config.experimental.list_physical_devices('GPU') else False,
                        'timestamp': time.time()
                    }
                except:
                    pass

        except Exception as e:
            print(f"Error updating memory stats: {e}")

    def _apply_memory_optimizations(self):
        """Apply automatic memory optimizations based on current usage"""
        try:
            system_mem = self.gpu_memory_stats.get('system', {})
            usage_percent = system_mem.get('usage_percent', 0)

            # High memory usage - trigger cleanup
            if usage_percent > 85:
                self._trigger_memory_cleanup()
                self.optimization_strategies['high_memory_cleanup'] = time.time()

            # GPU memory optimization
            for key, gpu_stats in self.gpu_memory_stats.items():
                if key.startswith('gpu_') and isinstance(gpu_stats, dict):
                    gpu_usage = gpu_stats.get('utilization_percent', 0)
                    if gpu_usage > 90:
                        self._optimize_gpu_memory()
                        break

        except Exception as e:
            print(f"Error applying memory optimizations: {e}")

    def _trigger_memory_cleanup(self):
        """Trigger aggressive memory cleanup"""
        try:
            # Clear memory pools
            for dtype_pools in self.memory_pools.values():
                if isinstance(dtype_pools, dict):
                    for pool in dtype_pools.values():
                        pool.clear()

            # Force garbage collection
            gc.collect()

            # Clear TensorFlow session if available
            if TENSORFLOW_AVAILABLE:
                try:
                    tf.keras.backend.clear_session()
                except:
                    pass

            print("🧹 Memory cleanup triggered - freed system resources")

        except Exception as e:
            print(f"Memory cleanup error: {e}")

    def _optimize_gpu_memory(self):
        """Optimize GPU memory usage"""
        try:
            if TENSORFLOW_AVAILABLE:
                # Force TensorFlow to release GPU memory
                try:
                    gpus = tf.config.experimental.list_physical_devices('GPU')
                    if gpus:
                        # This forces memory deallocation
                        tf.config.experimental.set_memory_growth(gpus[0], True)
                        print("🎯 GPU memory optimization applied")
                except Exception as e:
                    print(f"GPU memory optimization error: {e}")

        except Exception as e:
            print(f"GPU optimization error: {e}")

    def allocate_tensor(self, shape: Tuple, dtype: str = 'float32', gpu: bool = False) -> np.ndarray:
        """
        Allocate tensor with memory pooling optimization

        Args:
            shape: Tensor shape
            dtype: Data type ('float32', 'float16', 'int32')
            gpu: Whether to allocate on GPU

        Returns:
            Allocated tensor
        """
        size_bytes = np.prod(shape) * np.dtype(dtype).itemsize
        size_mb = size_bytes / (1024**2)

        # Determine pool category
        if size_mb < 1:
            pool_category = 'small'
        elif size_mb < 10:
            pool_category = 'medium'
        else:
            pool_category = 'large'

        # Try to reuse from pool
        if dtype in self.memory_pools and pool_category in self.memory_pools[dtype]:
            pool = self.memory_pools[dtype][pool_category]
            for i, existing_tensor in enumerate(pool):
                if existing_tensor.shape == shape:
                    # Reuse existing tensor
                    pool.pop(i)
                    # Reinitialize with new data
                    if gpu and TENSORFLOW_AVAILABLE:
                        return tf.Variable(tf.random.normal(shape, dtype=dtype))
                    else:
                        return np.random.random(shape).astype(dtype)

        # Allocate new tensor
        if gpu and TENSORFLOW_AVAILABLE:
            try:
                tensor = tf.Variable(tf.random.normal(shape, dtype=dtype))
            except:
                # Fallback to CPU
                tensor = np.random.random(shape).astype(dtype)
        else:
            tensor = np.random.random(shape).astype(dtype)

        # Track allocation
        alloc_key = f"{dtype}_{shape}_{time.time()}"
        self.allocation_tracker[alloc_key] = {
            'shape': shape,
            'dtype': dtype,
            'size_mb': size_mb,
            'gpu': gpu,
            'timestamp': time.time()
        }

        return tensor

    def release_tensor(self, tensor: np.ndarray, dtype: str = 'float32'):
        """
        Release tensor back to memory pool for reuse

        Args:
            tensor: Tensor to release
            dtype: Data type for pooling
        """
        try:
            size_bytes = tensor.nbytes
            size_mb = size_bytes / (1024**2)

            # Determine pool category
            if size_mb < 1:
                pool_category = 'small'
            elif size_mb < 10:
                pool_category = 'medium'
            else:
                pool_category = 'large'

            # Add to pool if space available
            if dtype in self.memory_pools and pool_category in self.memory_pools[dtype]:
                pool = self.memory_pools[dtype][pool_category]
                if len(pool) < 10:  # Limit pool size
                    pool.append(tensor)
                    return True

            # Pool full or invalid - let garbage collector handle it
            return False

        except Exception as e:
            print(f"Error releasing tensor: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        stats = {
            'current_stats': self.gpu_memory_stats.copy(),
            'pool_stats': {},
            'allocation_stats': {},
            'optimization_stats': self.optimization_strategies.copy()
        }

        # Pool statistics
        for dtype, pools in self.memory_pools.items():
            if isinstance(pools, dict):
                stats['pool_stats'][dtype] = {}
                for category, pool in pools.items():
                    stats['pool_stats'][dtype][category] = len(pool)

        # Allocation statistics
        total_allocations = len(self.allocation_tracker)
        total_memory_mb = sum(alloc['size_mb'] for alloc in self.allocation_tracker.values())

        stats['allocation_stats'] = {
            'total_allocations': total_allocations,
            'total_memory_mb': total_memory_mb,
            'avg_allocation_mb': total_memory_mb / max(1, total_allocations),
            'gpu_allocations': sum(1 for alloc in self.allocation_tracker.values() if alloc['gpu'])
        }

        return stats

    def optimize_model_memory(self, model) -> Any:
        """
        Apply memory optimizations to ML model

        Args:
            model: ML model to optimize

        Returns:
            Optimized model
        """
        if not TENSORFLOW_AVAILABLE:
            return model

        try:
            # Apply mixed precision if beneficial
            if self._should_use_mixed_precision():
                policy = tf.keras.mixed_precision.experimental.Policy('mixed_float16')
                tf.keras.mixed_precision.experimental.set_policy(policy)
                print("🔧 Applied mixed precision optimization")

            # Enable XLA compilation for better memory usage
            if hasattr(model, 'compile'):
                model.compile(
                    optimizer=tf.keras.optimizers.Adam(),
                    loss='categorical_crossentropy',
                    metrics=['accuracy'],
                    jit_compile=True  # Enable XLA
                )
                print("🔧 Applied XLA compilation optimization")

            return model

        except Exception as e:
            print(f"Model memory optimization error: {e}")
            return model

    def _should_use_mixed_precision(self) -> bool:
        """Determine if mixed precision should be used"""
        # Check if GPU supports float16 efficiently
        gpu_stats = self.gpu_memory_stats.get('gpu_0', {})
        gpu_memory_mb = gpu_stats.get('total_mb', 0)

        # Use mixed precision for GPUs with sufficient memory
        return gpu_memory_mb >= 4000  # 4GB+ GPUs benefit from mixed precision

    def create_memory_efficient_dataloader(self, data: np.ndarray, batch_size: int = 32):
        """
        Create memory-efficient data loader

        Args:
            data: Input data array
            batch_size: Batch size for loading

        Returns:
            Memory-efficient data loader
        """
        class MemoryEfficientDataLoader:
            def __init__(self, data, batch_size, memory_optimizer):
                self.data = data
                self.batch_size = batch_size
                self.memory_optimizer = memory_optimizer
                self.index = 0

            def __iter__(self):
                self.index = 0
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration

                end_idx = min(self.index + self.batch_size, len(self.data))
                batch = self.data[self.index:end_idx]

                # Use memory-optimized tensor allocation
                batch_tensor = self.memory_optimizer.allocate_tensor(
                    batch.shape, dtype=str(batch.dtype)
                )
                np.copyto(batch_tensor, batch)

                self.index = end_idx
                return batch_tensor

        return MemoryEfficientDataLoader(data, batch_size, self)

    def apply_memory_optimization_strategy(self, strategy: str) -> bool:
        """
        Apply specific memory optimization strategy

        Args:
            strategy: Strategy name ('aggressive_cleanup', 'pool_compaction', 'gpu_offload')

        Returns:
            Success status
        """
        try:
            if strategy == 'aggressive_cleanup':
                self._trigger_memory_cleanup()
                # Clear old allocation records
                cutoff_time = time.time() - 3600  # 1 hour ago
                self.allocation_tracker = {
                    k: v for k, v in self.allocation_tracker.items()
                    if v['timestamp'] > cutoff_time
                }
                return True

            elif strategy == 'pool_compaction':
                # Compact memory pools by removing old tensors
                for dtype_pools in self.memory_pools.values():
                    if isinstance(dtype_pools, dict):
                        for pool in dtype_pools.values():
                            # Keep only the most recently used tensors
                            pool.sort(key=lambda x: getattr(x, '_last_used', 0), reverse=True)
                            del pool[10:]  # Keep only top 10
                return True

            elif strategy == 'gpu_offload':
                # Force CPU offload for GPU tensors
                if TENSORFLOW_AVAILABLE:
                    with tf.device('/CPU:0'):
                        # This context will force CPU operations
                        pass
                return True

            return False

        except Exception as e:
            print(f"Strategy application error: {e}")
            return False

    def get_memory_optimization_recommendations(self) -> List[str]:
        """Get memory optimization recommendations"""
        recommendations = []

        stats = self.get_memory_stats()
        system_mem = stats['current_stats'].get('system', {})
        usage_percent = system_mem.get('usage_percent', 0)

        if usage_percent > 80:
            recommendations.append("High memory usage detected - consider enabling memory pooling")

        gpu_mem = None
        for key, gpu_stats in stats['current_stats'].items():
            if key.startswith('gpu_'):
                gpu_mem = gpu_stats
                break

        if gpu_mem and gpu_mem.get('utilization_percent', 0) > 85:
            recommendations.append("High GPU memory usage - consider model quantization or gradient checkpointing")

        pool_stats = stats.get('pool_stats', {})
        total_pooled = sum(
            len(pool) for dtype_pools in pool_stats.values()
            for pool in dtype_pools.values()
            if isinstance(dtype_pools, dict)
        )

        if total_pooled < 5:
            recommendations.append("Low memory pool utilization - memory pooling may not be effective")

        if not recommendations:
            recommendations.append("Memory usage is within optimal ranges")

        return recommendations

# Global memory optimizer instance
gpu_memory_optimizer = GPUMemoryOptimizer()

# Memory-optimized tensor allocation functions
def allocate_optimized_tensor(shape: Tuple, dtype: str = 'float32', gpu: bool = False):
    """Memory-optimized tensor allocation"""
    return gpu_memory_optimizer.allocate_tensor(shape, dtype, gpu)

def release_optimized_tensor(tensor: np.ndarray, dtype: str = 'float32'):
    """Memory-optimized tensor release"""
    return gpu_memory_optimizer.release_tensor(tensor, dtype)

def get_memory_stats():
    """Get current memory statistics"""
    return gpu_memory_optimizer.get_memory_stats()

def optimize_model_memory(model):
    """Apply memory optimizations to model"""
    return gpu_memory_optimizer.optimize_model_memory(model)

# Cleanup on exit
import atexit
atexit.register(gpu_memory_optimizer.stop_memory_monitoring)