"""
Hardware-Specific GPU Optimizations for NobleLogic Trading System

Platform-aware optimizations for different GPU architectures, CPU configurations, and hardware capabilities
"""

import asyncio
import time
import numpy as np
import platform
import cpuinfo as py_cpuinfo
import psutil
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
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

class HardwareSpecificOptimizer:
    """Hardware-aware optimization system"""

    def __init__(self):
        self.hardware_profile = self._detect_hardware_profile()
        self.optimization_strategies = {}
        self.performance_metrics = {}
        self.adaptive_settings = {}

        # Initialize hardware-specific optimizations
        self._initialize_hardware_optimizations()

    def _detect_hardware_profile(self) -> Dict[str, Any]:
        """Detect and profile hardware capabilities"""
        profile = {
            'platform': platform.system().lower(),
            'architecture': platform.machine(),
            'cpu': {},
            'gpu': {},
            'memory': {},
            'optimizations': {}
        }

        # CPU profiling
        try:
            cpu_info = py_cpuinfo.get_cpu_info()
            profile['cpu'] = {
                'brand': cpu_info.get('brand_raw', 'Unknown'),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency_mhz': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'cache_size': cpu_info.get('l3_cache_size', 0),
                'supports_avx': 'avx' in cpu_info.get('flags', []),
                'supports_avx2': 'avx2' in cpu_info.get('flags', []),
                'supports_avx512': 'avx512' in cpu_info.get('flags', [])
            }
        except Exception as e:
            profile['cpu']['error'] = str(e)

        # GPU profiling
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                profile['gpu'][f'gpu_{i}'] = {
                    'name': gpu.name,
                    'memory_mb': gpu.memoryTotal,
                    'compute_capability': self._get_compute_capability(gpu.name),
                    'is_integrated': self._is_integrated_gpu(gpu.name),
                    'supports_tensor_cores': self._supports_tensor_cores(gpu.name),
                    'optimal_batch_size': self._calculate_optimal_batch_size(gpu.memoryTotal)
                }
        except ImportError:
            profile['gpu']['not_available'] = 'GPUtil not installed'
        except Exception as e:
            profile['gpu']['error'] = str(e)

        # Memory profiling
        vm = psutil.virtual_memory()
        profile['memory'] = {
            'total_gb': vm.total / (1024**3),
            'has_large_memory': vm.total > 16 * (1024**3),  # > 16GB
            'is_high_bandwidth': self._detect_high_bandwidth_memory()
        }

        return profile

    def _get_compute_capability(self, gpu_name: str) -> str:
        """Get CUDA compute capability for GPU"""
        gpu_name = gpu_name.lower()

        # RTX 30-series
        if 'rtx 30' in gpu_name or 'rtx 40' in gpu_name:
            return '8.6' if '3090' in gpu_name or '4090' in gpu_name else '8.0'

        # RTX 20-series
        elif 'rtx 20' in gpu_name:
            return '7.5' if '2080' in gpu_name else '7.0'

        # GTX 10-series
        elif 'gtx 10' in gpu_name:
            return '6.1' if '1080' in gpu_name else '6.0'

        # Tesla/Quadro
        elif 'tesla' in gpu_name or 'quadro' in gpu_name:
            return '7.0'  # Conservative estimate

        return '6.0'  # Default

    def _is_integrated_gpu(self, gpu_name: str) -> bool:
        """Check if GPU is integrated"""
        gpu_name = gpu_name.lower()
        return any(term in gpu_name for term in ['intel', 'uhd', 'iris', 'integrated'])

    def _supports_tensor_cores(self, gpu_name: str) -> bool:
        """Check if GPU supports tensor cores"""
        gpu_name = gpu_name.lower()

        # RTX series and newer
        if 'rtx' in gpu_name:
            return True

        # Tesla V100, T4, A100
        if any(model in gpu_name for model in ['v100', 't4', 'a100', 'a6000']):
            return True

        return False

    def _calculate_optimal_batch_size(self, memory_mb: int) -> int:
        """Calculate optimal batch size based on GPU memory"""
        if memory_mb >= 8192:  # 8GB+
            return 64
        elif memory_mb >= 4096:  # 4GB+
            return 32
        elif memory_mb >= 2048:  # 2GB+
            return 16
        else:
            return 8

    def _detect_high_bandwidth_memory(self) -> bool:
        """Detect if system has high-bandwidth memory"""
        # This is a simplified check - in practice, you'd check SPD info
        total_memory = psutil.virtual_memory().total / (1024**3)
        return total_memory >= 32  # Assume 32GB+ systems have better memory

    def _initialize_hardware_optimizations(self):
        """Initialize hardware-specific optimizations"""
        # CPU optimizations
        self._setup_cpu_optimizations()

        # GPU optimizations
        self._setup_gpu_optimizations()

        # Memory optimizations
        self._setup_memory_optimizations()

        # Platform-specific optimizations
        self._setup_platform_optimizations()

    def _setup_cpu_optimizations(self):
        """Setup CPU-specific optimizations"""
        cpu_profile = self.hardware_profile['cpu']

        # AVX optimizations
        if cpu_profile.get('supports_avx512'):
            self.optimization_strategies['cpu_avx512'] = {
                'enabled': True,
                'vector_width': 512,
                'optimal_threads': cpu_profile.get('cores', 4)
            }
        elif cpu_profile.get('supports_avx2'):
            self.optimization_strategies['cpu_avx2'] = {
                'enabled': True,
                'vector_width': 256,
                'optimal_threads': cpu_profile.get('cores', 4)
            }

        # Threading optimizations
        cores = cpu_profile.get('cores', 4)
        threads = cpu_profile.get('threads', cores)

        self.optimization_strategies['cpu_threading'] = {
            'physical_cores': cores,
            'logical_threads': threads,
            'hyperthreading': threads > cores,
            'optimal_thread_pool_size': cores if not self._memory_constrained() else cores // 2
        }

    def _setup_gpu_optimizations(self):
        """Setup GPU-specific optimizations"""
        gpu_profiles = self.hardware_profile['gpu']

        for gpu_key, gpu_profile in gpu_profiles.items():
            if gpu_key.startswith('gpu_'):
                gpu_opts = {}

                # Tensor core optimizations
                if gpu_profile.get('supports_tensor_cores'):
                    gpu_opts['tensor_cores'] = {
                        'enabled': True,
                        'precision': 'float16' if gpu_profile.get('memory_mb', 0) >= 4096 else 'float32'
                    }

                # Memory optimizations
                memory_mb = gpu_profile.get('memory_mb', 2048)
                if memory_mb >= 8192:  # 8GB+
                    gpu_opts['memory_strategy'] = 'aggressive_prefetch'
                elif memory_mb >= 4096:  # 4GB+
                    gpu_opts['memory_strategy'] = 'balanced'
                else:
                    gpu_opts['memory_strategy'] = 'memory_efficient'

                # Compute capability optimizations
                compute_cap = gpu_profile.get('compute_capability', '6.0')
                if float(compute_cap) >= 8.0:
                    gpu_opts['async_compute'] = True
                    gpu_opts['concurrent_kernels'] = True

                self.optimization_strategies[f'gpu_{gpu_key}'] = gpu_opts

    def _setup_memory_optimizations(self):
        """Setup memory-specific optimizations"""
        memory_profile = self.hardware_profile['memory']

        if memory_profile.get('has_large_memory'):
            self.optimization_strategies['memory_large'] = {
                'pool_size_multiplier': 2.0,
                'prefetch_enabled': True,
                'cache_strategy': 'aggressive'
            }
        else:
            self.optimization_strategies['memory_constrained'] = {
                'pool_size_multiplier': 0.5,
                'prefetch_enabled': False,
                'cache_strategy': 'conservative'
            }

    def _setup_platform_optimizations(self):
        """Setup platform-specific optimizations"""
        platform_name = self.hardware_profile['platform']

        if platform_name == 'windows':
            self.optimization_strategies['platform_windows'] = {
                'memory_alignment': 4096,  # Page size
                'thread_priority': 'high',
                'affinity_enabled': True
            }
        elif platform_name == 'linux':
            self.optimization_strategies['platform_linux'] = {
                'memory_alignment': 4096,
                'thread_priority': 'normal',
                'affinity_enabled': True,
                'huge_pages': self._check_huge_pages_support()
            }
        elif platform_name == 'darwin':  # macOS
            self.optimization_strategies['platform_macos'] = {
                'memory_alignment': 16384,  # macOS page size
                'thread_priority': 'normal',
                'affinity_enabled': False  # Limited support on macOS
            }

    def _memory_constrained(self) -> bool:
        """Check if system is memory constrained"""
        vm = psutil.virtual_memory()
        return vm.available / vm.total < 0.2  # Less than 20% memory available

    def _check_huge_pages_support(self) -> bool:
        """Check if huge pages are supported (Linux only)"""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('HugePages_Total:'):
                        total = int(line.split()[1])
                        return total > 0
        except:
            pass
        return False

    def get_optimal_batch_size(self, operation_type: str = 'inference') -> int:
        """
        Get optimal batch size for current hardware

        Args:
            operation_type: Type of operation ('inference', 'training', 'preprocessing')

        Returns:
            Optimal batch size
        """
        gpu_profiles = self.hardware_profile['gpu']

        # Default batch sizes
        defaults = {
            'inference': 32,
            'training': 16,
            'preprocessing': 64
        }

        base_size = defaults.get(operation_type, 32)

        # Adjust based on GPU memory
        for gpu_key, gpu_profile in gpu_profiles.items():
            if gpu_key.startswith('gpu_'):
                optimal = gpu_profile.get('optimal_batch_size', base_size)

                # Adjust for operation type
                if operation_type == 'training':
                    optimal = max(1, optimal // 2)  # Smaller batches for training
                elif operation_type == 'preprocessing':
                    optimal = optimal * 2  # Larger batches for preprocessing

                # Adjust for memory constraints
                if self._memory_constrained():
                    optimal = max(1, optimal // 2)

                return optimal

        return base_size

    def get_optimal_thread_count(self, operation_type: str = 'cpu') -> int:
        """
        Get optimal thread count for current hardware

        Args:
            operation_type: Type of operation

        Returns:
            Optimal thread count
        """
        cpu_profile = self.hardware_profile['cpu']
        cores = cpu_profile.get('cores', 4)

        if operation_type == 'io_bound':
            return cores * 2  # More threads for I/O
        elif operation_type == 'memory_bound':
            return cores  # Physical cores for memory operations
        else:  # CPU bound
            return cores if not self._memory_constrained() else cores // 2

    def apply_hardware_optimizations(self, model=None, data_loader=None):
        """
        Apply all applicable hardware optimizations

        Args:
            model: ML model to optimize
            data_loader: Data loader to optimize

        Returns:
            Optimized components
        """
        optimized = {}

        # Apply CPU optimizations
        optimized['cpu_settings'] = self._apply_cpu_optimizations()

        # Apply GPU optimizations
        if TENSORFLOW_AVAILABLE and model is not None:
            optimized['gpu_model'] = self._apply_gpu_optimizations(model)
        else:
            optimized['gpu_model'] = model

        # Apply memory optimizations
        optimized['memory_settings'] = self._apply_memory_optimizations()

        # Apply data loader optimizations
        if data_loader is not None:
            optimized['data_loader'] = self._apply_dataloader_optimizations(data_loader)
        else:
            optimized['data_loader'] = data_loader

        return optimized

    def _apply_cpu_optimizations(self) -> Dict[str, Any]:
        """Apply CPU-specific optimizations"""
        settings = {}

        # Set optimal thread pool size
        threading_settings = self.optimization_strategies.get('cpu_threading', {})
        settings['thread_pool_size'] = threading_settings.get('optimal_thread_pool_size', 4)

        # Set NumPy thread settings
        import os
        os.environ['OMP_NUM_THREADS'] = str(settings['thread_pool_size'])
        os.environ['MKL_NUM_THREADS'] = str(settings['thread_pool_size'])

        # Enable OpenMP optimizations if available
        if hasattr(np, 'show_config'):
            config = np.show_config()
            if 'openmp' in str(config).lower():
                settings['openmp_enabled'] = True

        return settings

    def _apply_gpu_optimizations(self, model):
        """Apply GPU-specific optimizations to model"""
        if not TENSORFLOW_AVAILABLE:
            return model

        try:
            gpu_opts = self.optimization_strategies.get('gpu_gpu_0', {})

            # Apply mixed precision if supported
            if gpu_opts.get('tensor_cores', {}).get('enabled'):
                precision = gpu_opts['tensor_cores'].get('precision', 'float32')
                if precision == 'float16':
                    policy = tf.keras.mixed_precision.experimental.Policy('mixed_float16')
                    tf.keras.mixed_precision.experimental.set_policy(policy)

            # Enable XLA compilation
            if hasattr(model, 'compile'):
                model.compile(
                    optimizer=tf.keras.optimizers.Adam(),
                    loss='categorical_crossentropy',
                    metrics=['accuracy'],
                    jit_compile=True
                )

            # Set memory growth
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                tf.config.experimental.set_memory_growth(gpus[0], True)

            return model

        except Exception as e:
            print(f"GPU optimization error: {e}")
            return model

    def _apply_memory_optimizations(self) -> Dict[str, Any]:
        """Apply memory-specific optimizations"""
        settings = {}

        memory_opts = self.optimization_strategies.get('memory_large') or \
                     self.optimization_strategies.get('memory_constrained', {})

        settings['pool_size_multiplier'] = memory_opts.get('pool_size_multiplier', 1.0)
        settings['prefetch_enabled'] = memory_opts.get('prefetch_enabled', True)
        settings['cache_strategy'] = memory_opts.get('cache_strategy', 'balanced')

        return settings

    def _apply_dataloader_optimizations(self, data_loader):
        """Apply data loader optimizations"""
        # Set optimal batch size
        optimal_batch = self.get_optimal_batch_size('preprocessing')

        # Set optimal number of workers
        optimal_workers = self.get_optimal_thread_count('io_bound')

        # Apply settings if data loader supports them
        if hasattr(data_loader, 'batch_size'):
            data_loader.batch_size = optimal_batch

        if hasattr(data_loader, 'num_workers'):
            data_loader.num_workers = optimal_workers

        return data_loader

    def benchmark_hardware_performance(self) -> Dict[str, Any]:
        """Benchmark hardware-specific performance"""
        results = {}

        # CPU benchmark
        results['cpu'] = self._benchmark_cpu_performance()

        # GPU benchmark
        results['gpu'] = self._benchmark_gpu_performance()

        # Memory benchmark
        results['memory'] = self._benchmark_memory_performance()

        return results

    def _benchmark_cpu_performance(self) -> Dict[str, Any]:
        """Benchmark CPU performance"""
        results = {}

        try:
            # Vectorized operations benchmark
            data = np.random.random(1000000)

            start = time.time()
            result1 = np.sum(data ** 2)
            vectorized_time = time.time() - start

            start = time.time()
            result2 = sum(x ** 2 for x in data)
            loop_time = time.time() - start

            results['vectorization_speedup'] = loop_time / vectorized_time
            results['vectorized_gflops'] = (2e6 / vectorized_time) / 1e9  # Approximate GFLOPS

        except Exception as e:
            results['error'] = str(e)

        return results

    def _benchmark_gpu_performance(self) -> Dict[str, Any]:
        """Benchmark GPU performance"""
        results = {}

        if not TENSORFLOW_AVAILABLE:
            results['tensorflow_not_available'] = True
            return results

        try:
            # Simple GPU computation benchmark
            with tf.device('/GPU:0' if tf.config.experimental.list_physical_devices('GPU') else '/CPU:0'):
                data = tf.random.normal((1000, 1000))

                start = time.time()
                result = tf.reduce_sum(data ** 2)
                gpu_time = time.time() - start

                results['gpu_compute_time'] = gpu_time
                results['gpu_gflops'] = (2e6 / gpu_time) / 1e9  # Approximate GFLOPS

        except Exception as e:
            results['error'] = str(e)

        return results

    def _benchmark_memory_performance(self) -> Dict[str, Any]:
        """Benchmark memory performance"""
        results = {}

        try:
            # Memory bandwidth benchmark
            size = 100000000  # 100M elements
            data = np.random.random(size, dtype=np.float32)

            # Sequential access
            start = time.time()
            result = np.sum(data)
            sequential_time = time.time() - start

            # Calculate bandwidth (approximate)
            bytes_accessed = size * 4  # float32 = 4 bytes
            results['memory_bandwidth_gb_s'] = bytes_accessed / sequential_time / 1e9

        except Exception as e:
            results['error'] = str(e)

        return results

    def get_hardware_recommendations(self) -> List[str]:
        """Get hardware-specific recommendations"""
        recommendations = []

        # CPU recommendations
        cpu_profile = self.hardware_profile['cpu']
        if not cpu_profile.get('supports_avx2'):
            recommendations.append("Consider upgrading to a CPU with AVX2 support for better vectorized performance")

        # GPU recommendations
        gpu_profiles = self.hardware_profile['gpu']
        has_good_gpu = False
        for gpu_key, gpu_profile in gpu_profiles.items():
            if gpu_key.startswith('gpu_'):
                memory_mb = gpu_profile.get('memory_mb', 0)
                if memory_mb >= 4096:
                    has_good_gpu = True
                    break

        if not has_good_gpu and TENSORFLOW_AVAILABLE:
            recommendations.append("GPU with 4GB+ memory recommended for optimal ML performance")

        # Memory recommendations
        memory_profile = self.hardware_profile['memory']
        if not memory_profile.get('has_large_memory'):
            recommendations.append("16GB+ RAM recommended for complex ML workloads")

        if not recommendations:
            recommendations.append("Hardware configuration is suitable for ML workloads")

        return recommendations

# Global hardware optimizer instance
hardware_optimizer = HardwareSpecificOptimizer()

# Convenience functions
def get_optimal_batch_size(operation_type: str = 'inference') -> int:
    """Get optimal batch size for current hardware"""
    return hardware_optimizer.get_optimal_batch_size(operation_type)

def get_optimal_thread_count(operation_type: str = 'cpu') -> int:
    """Get optimal thread count for current hardware"""
    return hardware_optimizer.get_optimal_thread_count(operation_type)

def apply_hardware_optimizations(model=None, data_loader=None):
    """Apply hardware-specific optimizations"""
    return hardware_optimizer.apply_hardware_optimizations(model, data_loader)

def benchmark_hardware_performance() -> Dict[str, Any]:
    """Benchmark hardware performance"""
    return hardware_optimizer.benchmark_hardware_performance()

def get_hardware_recommendations() -> List[str]:
    """Get hardware recommendations"""
    return hardware_optimizer.get_hardware_recommendations()