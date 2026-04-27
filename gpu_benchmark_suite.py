"""
GPU Benchmarking Suite for NobleLogic Trading System

Comprehensive benchmarking for GPU acceleration, memory usage, and performance metrics
"""

import asyncio
import time
import numpy as np
import psutil
import GPUtil
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import gc
import sys

# Add ML path for imports
ml_path = os.path.join(os.path.dirname(__file__), 'ml')
sys.path.append(ml_path)

try:
    # Try to import the ML engine
    import sys
    ml_path = os.path.join(os.path.dirname(__file__), 'ml')
    sys.path.append(ml_path)
    import tensorflow as tf
    # Only import if syntax is valid
    import ast
    with open('ml_integration.py', 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    ast.parse(source)  # Check if syntax is valid
    from ml_integration import GPUAcceleratedMLEngine
    TENSORFLOW_AVAILABLE = True
except (ImportError, SyntaxError, UnicodeDecodeError):
    # Create a mock GPUAcceleratedMLEngine for benchmarking
    try:
        import tensorflow as tf
        TENSORFLOW_AVAILABLE = True
    except ImportError:
        TENSORFLOW_AVAILABLE = False
    
    class GPUAcceleratedMLEngine:
        def __init__(self):
            self.gpu_available = TENSORFLOW_AVAILABLE and len(tf.config.experimental.list_physical_devices('GPU')) > 0 if TENSORFLOW_AVAILABLE else False
        
        async def predict(self, features):
            # Mock prediction
            import numpy as np
            return np.random.random(len(features))
    
    print("⚠️ ML integration syntax error - using mock GPU engine for benchmarks")

class GPUBenchmarkSuite:
    """Comprehensive GPU benchmarking suite"""

    def __init__(self):
        self.results = {}
        self.system_info = self._get_system_info()
        self.baseline_metrics = {}

    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {
            'cpu': {
                'cores': psutil.cpu_count(),
                'cores_logical': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'usage_percent': psutil.cpu_percent(interval=1)
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3),
                'usage_percent': psutil.virtual_memory().percent
            },
            'gpu': {}
        }

        # Get GPU information
        try:
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                info['gpu'][f'gpu_{i}'] = {
                    'name': gpu.name,
                    'memory_total_mb': gpu.memoryTotal,
                    'memory_free_mb': gpu.memoryFree,
                    'memory_used_mb': gpu.memoryUsed,
                    'temperature': gpu.temperature,
                    'uuid': gpu.uuid
                }
        except Exception as e:
            info['gpu']['error'] = str(e)

        # TensorFlow GPU info
        if TENSORFLOW_AVAILABLE:
            try:
                gpus = tf.config.experimental.list_physical_devices('GPU')
                info['tensorflow'] = {
                    'gpu_count': len(gpus),
                    'gpu_devices': [gpu.name for gpu in gpus],
                    'cpu_devices': [cpu.name for cpu in tf.config.experimental.list_physical_devices('CPU')]
                }
            except Exception as e:
                info['tensorflow'] = {'error': str(e)}

        return info

    async def run_full_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("🚀 Starting GPU Benchmark Suite...")
        print("=" * 60)

        start_time = time.time()

        # System baseline
        await self.benchmark_system_baseline()

        # ML benchmarks
        if TENSORFLOW_AVAILABLE:
            await self.benchmark_ml_inference()
            await self.benchmark_ml_training()
            await self.benchmark_batch_processing()

        # Memory benchmarks
        await self.benchmark_memory_usage()

        # Hardware-specific benchmarks
        await self.benchmark_hardware_specific()

        # Performance benchmarks
        await self.benchmark_performance_scaling()

        # Stress tests
        await self.benchmark_stress_test()

        total_time = time.time() - start_time

        # Generate report
        report = self.generate_benchmark_report(total_time)

        print(f"\n✅ Benchmark Suite Complete in {total_time:.1f} seconds")
        print(f"📄 Results saved to gpu_benchmark_results.json")

        return report

    async def benchmark_system_baseline(self):
        """Establish system baseline performance"""
        print("📊 Benchmarking System Baseline...")

        # CPU baseline
        cpu_times = []
        for _ in range(10):
            start = time.time()
            # Simulate CPU workload
            result = sum(i * i for i in range(100000))
            cpu_times.append(time.time() - start)

        # Memory baseline
        memory_usage = []
        for _ in range(5):
            # Allocate and free memory
            data = np.random.random((1000, 1000))
            memory_usage.append(psutil.virtual_memory().percent)
            del data
            gc.collect()

        self.baseline_metrics['cpu'] = {
            'avg_time': np.mean(cpu_times),
            'std_time': np.std(cpu_times),
            'min_time': min(cpu_times),
            'max_time': max(cpu_times)
        }

        self.baseline_metrics['memory'] = {
            'avg_usage': np.mean(memory_usage),
            'peak_usage': max(memory_usage)
        }

        print(f"📊 Baseline CPU: {self.baseline_metrics['cpu']['avg_time']:.4f}s avg, Memory: {self.baseline_metrics['memory']['avg_usage']:.1f}% avg")
    async def benchmark_ml_inference(self):
        """Benchmark ML inference performance"""
        print("🧠 Benchmarking ML Inference Performance...")

        try:
            ml_engine = GPUAcceleratedMLEngine()

            # Test different batch sizes
            batch_sizes = [1, 10, 50, 100]
            inference_results = {}

            for batch_size in batch_sizes:
                print(f"   Testing batch size: {batch_size}")

                # Generate test data
                test_features = np.random.random((batch_size, 10)).astype(np.float32)

                # Warm up
                await ml_engine.predict(test_features[:1])

                # Benchmark
                times = []
                for _ in range(10):
                    start = time.time()
                    predictions = await ml_engine.predict(test_features)
                    times.append(time.time() - start)

                inference_results[batch_size] = {
                    'avg_time_ms': np.mean(times) * 1000,
                    'std_time_ms': np.std(times) * 1000,
                    'min_time_ms': min(times) * 1000,
                    'max_time_ms': max(times) * 1000,
                    'throughput': batch_size / np.mean(times),  # predictions per second
                    'gpu_available': ml_engine.gpu_available
                }

                print(f"   Batch {batch_size}: {inference_results[batch_size]['avg_time_ms']:.1f}ms avg, {inference_results[batch_size]['throughput']:.1f} pred/s")
            self.results['ml_inference'] = inference_results

        except Exception as e:
            print(f"❌ ML Inference benchmark failed: {e}")
            self.results['ml_inference'] = {'error': str(e)}

    async def benchmark_ml_training(self):
        """Benchmark ML training performance"""
        print("🎓 Benchmarking ML Training Performance...")

        try:
            # Create simple training data
            n_samples = 1000
            n_features = 10
            X = np.random.random((n_samples, n_features)).astype(np.float32)
            y = np.random.randint(0, 3, n_samples)  # 3 classes

            # Simple neural network
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(n_features,)),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(3, activation='softmax')
            ])

            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            # Benchmark training
            start_time = time.time()
            history = model.fit(X, y, epochs=5, batch_size=32, verbose=0)
            training_time = time.time() - start_time

            final_accuracy = history.history['accuracy'][-1]
            final_loss = history.history['loss'][-1]

            self.results['ml_training'] = {
                'training_time_seconds': training_time,
                'final_accuracy': final_accuracy,
                'final_loss': final_loss,
                'epochs': 5,
                'samples': n_samples,
                'samples_per_second': n_samples * 5 / training_time
            }

            print(f"🎓 Training: {training_time:.1f}s, Acc: {final_accuracy:.3f}, Loss: {final_loss:.3f}")
        except Exception as e:
            print(f"❌ ML Training benchmark failed: {e}")
            self.results['ml_training'] = {'error': str(e)}

    async def benchmark_batch_processing(self):
        """Benchmark batch processing capabilities"""
        print("📦 Benchmarking Batch Processing...")

        try:
            ml_engine = GPUAcceleratedMLEngine()

            # Test concurrent predictions
            batch_sizes = [10, 50, 100, 200]
            concurrency_results = {}

            for batch_size in batch_sizes:
                print(f"   Testing concurrent batch size: {batch_size}")

                # Create multiple concurrent tasks
                tasks = []
                for _ in range(5):  # 5 concurrent batches
                    features = np.random.random((batch_size, 10)).astype(np.float32)
                    task = ml_engine.predict(features)
                    tasks.append(task)

                # Measure concurrent execution
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                concurrent_time = time.time() - start_time

                # Measure sequential execution for comparison
                start_time = time.time()
                for task in tasks:
                    await task
                sequential_time = time.time() - start_time

                concurrency_results[batch_size] = {
                    'concurrent_time': concurrent_time,
                    'sequential_time': sequential_time,
                    'speedup': sequential_time / concurrent_time,
                    'efficiency': (sequential_time / concurrent_time) / 5  # normalized
                }

                print(f"   Batch {batch_size}: {concurrency_results[batch_size]['speedup']:.2f}x speedup")
            self.results['batch_processing'] = concurrency_results

        except Exception as e:
            print(f"❌ Batch processing benchmark failed: {e}")
            self.results['batch_processing'] = {'error': str(e)}

    async def benchmark_memory_usage(self):
        """Benchmark memory usage patterns"""
        print("💾 Benchmarking Memory Usage...")

        try:
            initial_memory = psutil.virtual_memory().used

            # Test memory allocation patterns
            memory_tests = []

            # Small allocations
            small_data = []
            for i in range(100):
                data = np.random.random((100, 100))
                small_data.append(data)
            small_memory = psutil.virtual_memory().used - initial_memory
            memory_tests.append({
                'test': 'small_allocations',
                'memory_mb': small_memory / (1024**2),
                'allocations': 100
            })

            # Clear memory
            del small_data
            gc.collect()

            # Large allocations
            large_data = []
            for i in range(10):
                data = np.random.random((1000, 1000))
                large_data.append(data)
            large_memory = psutil.virtual_memory().used - initial_memory
            memory_tests.append({
                'test': 'large_allocations',
                'memory_mb': large_memory / (1024**2),
                'allocations': 10
            })

            # Clear memory
            del large_data
            gc.collect()

            # GPU memory if available
            gpu_memory_info = {}
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_memory_info[f'gpu_{i}'] = {
                        'used_mb': gpu.memoryUsed,
                        'free_mb': gpu.memoryFree,
                        'total_mb': gpu.memoryTotal,
                        'utilization_percent': gpu.memoryUtil * 100
                    }
            except Exception as e:
                gpu_memory_info['error'] = str(e)

            self.results['memory_usage'] = {
                'system_memory_tests': memory_tests,
                'gpu_memory': gpu_memory_info,
                'memory_efficiency_score': self._calculate_memory_efficiency(memory_tests)
            }

            print(f"✅ Memory benchmarks complete - Efficiency Score: {self._calculate_memory_efficiency(memory_tests):.2f}")

        except Exception as e:
            print(f"❌ Memory benchmark failed: {e}")
            self.results['memory_usage'] = {'error': str(e)}

    def _calculate_memory_efficiency(self, memory_tests: List[Dict]) -> float:
        """Calculate memory efficiency score"""
        if not memory_tests:
            return 0.0

        # Simple efficiency metric based on memory per allocation
        efficiencies = []
        for test in memory_tests:
            if test['allocations'] > 0:
                mb_per_allocation = test['memory_mb'] / test['allocations']
                # Lower is better - normalize to 0-1 scale (assuming < 10MB/alloc is good)
                efficiency = max(0, 1 - (mb_per_allocation / 10.0))
                efficiencies.append(efficiency)

        return np.mean(efficiencies) if efficiencies else 0.0

    async def benchmark_hardware_specific(self):
        """Benchmark hardware-specific optimizations"""
        print("🔧 Benchmarking Hardware-Specific Optimizations...")

        hardware_results = {}

        # CPU-specific optimizations
        hardware_results['cpu'] = await self._benchmark_cpu_optimizations()

        # GPU-specific optimizations
        hardware_results['gpu'] = await self._benchmark_gpu_optimizations()

        # Memory-specific optimizations
        hardware_results['memory'] = await self._benchmark_memory_optimizations()

        self.results['hardware_specific'] = hardware_results

        print("✅ Hardware-specific benchmarks complete")

    async def _benchmark_cpu_optimizations(self) -> Dict[str, Any]:
        """Benchmark CPU-specific optimizations"""
        results = {}

        try:
            # SIMD operations benchmark
            import math

            # Test vectorized operations
            data = np.random.random(1000000)

            start = time.time()
            result1 = np.sum(data ** 2)  # Vectorized
            vectorized_time = time.time() - start

            start = time.time()
            result2 = sum(x ** 2 for x in data)  # Non-vectorized
            loop_time = time.time() - start

            results['vectorization'] = {
                'vectorized_time': vectorized_time,
                'loop_time': loop_time,
                'speedup': loop_time / vectorized_time,
                'results_match': abs(result1 - result2) < 1e-6
            }

            # Test parallel processing
            import concurrent.futures

            def cpu_intensive_task(n):
                return sum(math.sin(i) * math.cos(i) for i in range(n))

            # Sequential
            start = time.time()
            sequential_results = [cpu_intensive_task(10000) for _ in range(8)]
            sequential_time = time.time() - start

            # Parallel
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                parallel_results = list(executor.map(cpu_intensive_task, [10000] * 8))
            parallel_time = time.time() - start

            results['parallelization'] = {
                'sequential_time': sequential_time,
                'parallel_time': parallel_time,
                'speedup': sequential_time / parallel_time,
                'results_match': sequential_results == parallel_results
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    async def _benchmark_gpu_optimizations(self) -> Dict[str, Any]:
        """Benchmark GPU-specific optimizations"""
        results = {}

        if not TENSORFLOW_AVAILABLE:
            results['tensorflow_available'] = False
            return results

        try:
            # Test different TensorFlow optimizations
            optimizations = {}

            # Mixed precision
            if tf.config.experimental.list_physical_devices('GPU'):
                policy = tf.keras.mixed_precision.experimental.Policy('mixed_float16')
                tf.keras.mixed_precision.experimental.set_policy(policy)
                optimizations['mixed_precision'] = 'enabled'
            else:
                optimizations['mixed_precision'] = 'cpu_only'

            # XLA compilation
            @tf.function
            def compiled_function(x):
                return tf.reduce_sum(x ** 2)

            data = tf.random.normal((1000, 1000))

            # Non-compiled
            start = time.time()
            result1 = tf.reduce_sum(data ** 2)
            non_compiled_time = time.time() - start

            # Compiled
            start = time.time()
            result2 = compiled_function(data)
            compiled_time = time.time() - start

            optimizations['xla_compilation'] = {
                'non_compiled_time': non_compiled_time,
                'compiled_time': compiled_time,
                'speedup': non_compiled_time / compiled_time if compiled_time > 0 else 0
            }

            results['tensorflow_optimizations'] = optimizations

        except Exception as e:
            results['error'] = str(e)

        return results

    async def _benchmark_memory_optimizations(self) -> Dict[str, Any]:
        """Benchmark memory-specific optimizations"""
        results = {}

        try:
            # Test memory pooling
            import sys

            # Create objects and measure memory
            initial_objects = len(gc.get_objects())

            # Test with memory pooling (reuse objects)
            pooled_data = []
            for i in range(100):
                if pooled_data:
                    # Reuse existing object
                    data = pooled_data.pop()
                    data.fill(np.random.random())
                else:
                    data = np.random.random(1000)
                pooled_data.append(data)

            pooled_objects = len(gc.get_objects()) - initial_objects

            # Test without pooling
            non_pooled_data = []
            for i in range(100):
                data = np.random.random(1000)
                non_pooled_data.append(data)

            non_pooled_objects = len(gc.get_objects()) - pooled_objects - initial_objects

            results['object_pooling'] = {
                'pooled_objects_created': pooled_objects,
                'non_pooled_objects_created': non_pooled_objects,
                'memory_savings_percent': (non_pooled_objects - pooled_objects) / non_pooled_objects * 100
            }

            # Clean up
            del pooled_data, non_pooled_data
            gc.collect()

        except Exception as e:
            results['error'] = str(e)

        return results

    async def benchmark_performance_scaling(self):
        """Benchmark performance scaling with load"""
        print("📈 Benchmarking Performance Scaling...")

        try:
            if not TENSORFLOW_AVAILABLE:
                self.results['performance_scaling'] = {'error': 'TensorFlow not available'}
                return

            ml_engine = GPUAcceleratedMLEngine()

            # Test scaling with increasing load
            load_levels = [1, 5, 10, 20, 50]
            scaling_results = {}

            for load in load_levels:
                print(f"   Testing load level: {load}")

                # Create concurrent tasks
                tasks = []
                for _ in range(load):
                    features = np.random.random((10, 10)).astype(np.float32)
                    tasks.append(ml_engine.predict(features))

                start_time = time.time()
                results = await asyncio.gather(*tasks)
                total_time = time.time() - start_time

                scaling_results[load] = {
                    'total_time': total_time,
                    'avg_time_per_task': total_time / load,
                    'tasks_per_second': load / total_time,
                    'success_rate': sum(1 for r in results if r is not None) / len(results)
                }

                print(f"   Load {load}: {scaling_results[load]['tasks_per_second']:.1f} tasks/s")
            self.results['performance_scaling'] = scaling_results

        except Exception as e:
            print(f"❌ Performance scaling benchmark failed: {e}")
            self.results['performance_scaling'] = {'error': str(e)}

    async def benchmark_stress_test(self):
        """Run stress test with maximum load"""
        print("🔥 Running Stress Test...")

        try:
            if not TENSORFLOW_AVAILABLE:
                self.results['stress_test'] = {'error': 'TensorFlow not available'}
                return

            ml_engine = GPUAcceleratedMLEngine()

            # Maximum concurrent load test
            max_concurrent = 100
            stress_results = {}

            print(f"   Testing maximum concurrent load: {max_concurrent} tasks")

            # Create maximum load
            tasks = []
            for _ in range(max_concurrent):
                features = np.random.random((10, 10)).astype(np.float32)
                tasks.append(ml_engine.predict(features))

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time

            successful_tasks = sum(1 for r in results if not isinstance(r, Exception))
            failed_tasks = len(results) - successful_tasks

            stress_results = {
                'max_concurrent_tasks': max_concurrent,
                'total_time': total_time,
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': successful_tasks / max_concurrent,
                'avg_time_per_task': total_time / max_concurrent,
                'tasks_per_second': max_concurrent / total_time,
                'memory_peak_mb': psutil.virtual_memory().percent
            }

            # Check for memory leaks
            gc.collect()
            final_memory = psutil.virtual_memory().used
            stress_results['memory_leak_mb'] = (final_memory - psutil.virtual_memory().used) / (1024**2)

            self.results['stress_test'] = stress_results

            print(f"🔥 Stress Test: {stress_results['total_time']:.1f}s, {stress_results['successful_operations']} ops")
        except Exception as e:
            print(f"❌ Stress test failed: {e}")
            self.results['stress_test'] = {'error': str(e)}

    def generate_benchmark_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_duration_seconds': total_time,
            'system_info': self.system_info,
            'results': self.results,
            'summary': self._generate_summary(),
            'recommendations': self._generate_recommendations()
        }

        # Save to file
        with open('gpu_benchmark_results.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return report

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary"""
        summary = {
            'overall_score': 0.0,
            'performance_rating': 'Unknown',
            'key_metrics': {}
        }

        scores = []

        # ML inference score
        if 'ml_inference' in self.results:
            inference = self.results['ml_inference']
            if isinstance(inference, dict) and 'error' not in inference:
                # Score based on inference speed (lower is better)
                avg_time = inference.get(1, {}).get('avg_time_ms', 1000)
                score = max(0, min(100, 1000 / avg_time))  # Normalize to 0-100
                scores.append(score)
                summary['key_metrics']['ml_inference_score'] = score

        # Memory efficiency score
        if 'memory_usage' in self.results:
            mem = self.results['memory_usage']
            if isinstance(mem, dict) and 'memory_efficiency_score' in mem:
                efficiency = mem['memory_efficiency_score'] * 100
                scores.append(efficiency)
                summary['key_metrics']['memory_efficiency_score'] = efficiency

        # Hardware optimization score
        if 'hardware_specific' in self.results:
            hw = self.results['hardware_specific']
            hw_score = 0
            count = 0

            for category in ['cpu', 'gpu', 'memory']:
                if category in hw and isinstance(hw[category], dict):
                    if 'vectorization' in hw[category]:
                        speedup = hw[category]['vectorization'].get('speedup', 1)
                        hw_score += min(100, speedup * 20)  # Cap at 100
                        count += 1
                    if 'parallelization' in hw[category]:
                        speedup = hw[category]['parallelization'].get('speedup', 1)
                        hw_score += min(100, speedup * 20)
                        count += 1

            if count > 0:
                avg_hw_score = hw_score / count
                scores.append(avg_hw_score)
                summary['key_metrics']['hardware_optimization_score'] = avg_hw_score

        # Overall score
        if scores:
            summary['overall_score'] = np.mean(scores)

            # Rating based on score
            if summary['overall_score'] >= 90:
                summary['performance_rating'] = 'Excellent'
            elif summary['overall_score'] >= 75:
                summary['performance_rating'] = 'Good'
            elif summary['overall_score'] >= 60:
                summary['performance_rating'] = 'Fair'
            else:
                summary['performance_rating'] = 'Needs Optimization'

        return summary

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Check ML performance
        if 'ml_inference' in self.results:
            inference = self.results['ml_inference']
            if isinstance(inference, dict) and 1 in inference:
                avg_time = inference[1].get('avg_time_ms', 1000)
                if avg_time > 100:
                    recommendations.append("Consider optimizing ML model architecture for faster inference")
                if not inference[1].get('gpu_available', False):
                    recommendations.append("Enable GPU acceleration for ML inference if CUDA GPU is available")

        # Check memory usage
        if 'memory_usage' in self.results:
            mem = self.results['memory_usage']
            if isinstance(mem, dict) and 'memory_efficiency_score' in mem:
                efficiency = mem['memory_efficiency_score']
                if efficiency < 0.7:
                    recommendations.append("Implement memory pooling and object reuse to improve memory efficiency")

        # Check hardware optimizations
        if 'hardware_specific' in self.results:
            hw = self.results['hardware_specific']
            if 'cpu' in hw and isinstance(hw['cpu'], dict):
                cpu_opt = hw['cpu']
                if 'vectorization' in cpu_opt:
                    speedup = cpu_opt['vectorization'].get('speedup', 1)
                    if speedup < 2:
                        recommendations.append("Use NumPy vectorized operations instead of Python loops for better CPU performance")

        # General recommendations
        if not any('gpu' in str(result) for result in self.results.values()):
            recommendations.append("Install CUDA and TensorFlow GPU support for hardware acceleration")

        if not recommendations:
            recommendations.append("System performance is optimal - no major optimizations needed")

        return recommendations

async def main():
    """Run benchmark suite"""
    suite = GPUBenchmarkSuite()
    report = await suite.run_full_benchmark_suite()

    # Print summary
    summary = report.get('summary', {})
    print("\n🎯 Benchmark Summary:")
    print(f"Overall Score: {summary.get('overall_score', 0):.1f}/100")
    print(f"Performance Rating: {summary.get('performance_rating', 'Unknown')}")

    print("\n📊 Key Metrics:")
    for metric, value in summary.get('key_metrics', {}).items():
        print(f"  {metric}: {value:.1f}")

    print("\n💡 Recommendations:")
    for rec in report.get('recommendations', []):
        print(f"  • {rec}")

if __name__ == "__main__":
    asyncio.run(main())