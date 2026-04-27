"""
Advanced ML Inference Utilities for NobleLogic Trading
Supports batch inference and mixed precision operations
"""

import numpy as np
import tensorflow as tf
import time
import asyncio
from typing import List, Dict, Any, Tuple, Union

class BatchInferenceEngine:
    def __init__(self, max_batch_size=32):
        """
        Initialize batch inference engine
        
        Args:
            max_batch_size (int): Maximum batch size for inference
        """
        self.max_batch_size = max_batch_size
        self.pending_requests = []
        self.is_processing = False
        self.results = {}
        self.request_id_counter = 0
        
    async def add_request(self, features):
        """
        Add inference request to batch queue
        
        Args:
            features: Feature vector for inference
            
        Returns:
            int: Request ID to retrieve results
        """
        request_id = self._get_next_id()
        self.pending_requests.append({
            'id': request_id,
            'features': features,
            'added_time': time.time()
        })
        
        # Trigger batch processing if we have enough requests or after a delay
        if len(self.pending_requests) >= self.max_batch_size and not self.is_processing:
            asyncio.create_task(self._process_batch())
        elif not self.is_processing:
            # Schedule processing after a short delay to collect more requests
            asyncio.create_task(self._delayed_processing())
            
        return request_id
    
    async def get_result(self, request_id, timeout=5.0):
        """
        Get result for a specific request
        
        Args:
            request_id: ID from add_request
            timeout: Maximum time to wait for result
            
        Returns:
            dict: Inference result or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if request_id in self.results:
                result = self.results[request_id]
                # Clean up after retrieval
                del self.results[request_id]
                return result
            
            # Wait a bit before checking again
            await asyncio.sleep(0.05)
        
        # If we get here, we timed out
        return None
    
    def _get_next_id(self):
        """Generate a unique request ID"""
        self.request_id_counter += 1
        return self.request_id_counter
    
    async def _delayed_processing(self, delay=0.1):
        """Wait a short time before processing to collect more requests"""
        await asyncio.sleep(delay)
        if not self.is_processing and self.pending_requests:
            await self._process_batch()
    
    async def _process_batch(self):
        """Process all pending requests in a batch"""
        if self.is_processing or not self.pending_requests:
            return
            
        self.is_processing = True
        
        try:
            # Take current batch (up to max_batch_size)
            current_batch = self.pending_requests[:self.max_batch_size]
            self.pending_requests = self.pending_requests[self.max_batch_size:]
            
            # Extract features and IDs
            batch_features = [req['features'] for req in current_batch]
            batch_ids = [req['id'] for req in current_batch]
            
            # Convert to proper format for batch processing
            batch_features_array = self._prepare_batch(batch_features)
            
            # This would be replaced by the actual model inference
            # The implementation depends on how the model is designed to handle batches
            batch_results = await self._run_model_inference(batch_features_array)
            
            # Store results by request ID
            for i, request_id in enumerate(batch_ids):
                if i < len(batch_results):
                    self.results[request_id] = batch_results[i]
                
        finally:
            self.is_processing = False
            
            # If there are still pending requests, process the next batch
            if self.pending_requests:
                asyncio.create_task(self._process_batch())
    
    def _prepare_batch(self, features_list):
        """Prepare features for batch inference"""
        # Handle different input formats
        if all(isinstance(f, np.ndarray) for f in features_list):
            # Stack numpy arrays
            return np.vstack(features_list)
        elif all(isinstance(f, tf.Tensor) for f in features_list):
            # Stack tensors
            return tf.concat(features_list, axis=0)
        else:
            # Convert to numpy array
            try:
                return np.vstack(features_list)
            except:
                # Fallback for heterogeneous inputs
                processed = []
                for f in features_list:
                    if isinstance(f, np.ndarray):
                        processed.append(f)
                    elif isinstance(f, tf.Tensor):
                        processed.append(f.numpy())
                    else:
                        processed.append(np.array(f))
                return np.vstack(processed)
    
    async def _run_model_inference(self, batch_features):
        """
        Process batch through model
        This is a placeholder - actual implementation depends on the model
        """
        # This would be replaced with actual model inference
        return [{'placeholder': 'result'} for _ in range(len(batch_features))]


class MixedPrecisionOptimizer:
    """Utility class for mixed precision training and inference"""
    
    @staticmethod
    def enable_mixed_precision():
        """
        Enable mixed precision training/inference
        Returns True if successfully enabled
        """
        try:
            policy = tf.keras.mixed_precision.Policy('mixed_float16')
            tf.keras.mixed_precision.set_global_policy(policy)
            print("[ML] Mixed precision policy set to:", policy.name)
            return True
        except Exception as e:
            print(f"[ML] Could not enable mixed precision: {e}")
            return False
    
    @staticmethod
    def disable_mixed_precision():
        """Disable mixed precision and return to default float32"""
        try:
            policy = tf.keras.mixed_precision.Policy('float32')
            tf.keras.mixed_precision.set_global_policy(policy)
            print("[ML] Mixed precision disabled, using:", policy.name)
            return True
        except Exception as e:
            print(f"[ML] Could not disable mixed precision: {e}")
            return False
    
    @staticmethod
    def get_current_policy():
        """Get current precision policy"""
        return tf.keras.mixed_precision.global_policy().name
    
    @staticmethod
    def optimize_model_for_mixed_precision(model):
        """
        Optimize a model for mixed precision
        
        Args:
            model: Keras model to optimize
            
        Returns:
            Optimized model
        """
        try:
            # Check if already using mixed precision
            if tf.keras.mixed_precision.global_policy().name != 'mixed_float16':
                MixedPrecisionOptimizer.enable_mixed_precision()
            
            # Get the original optimizer
            original_optimizer = model.optimizer
            
            # Wrap optimizer with LossScaleOptimizer for mixed precision
            if not isinstance(original_optimizer, tf.keras.mixed_precision.LossScaleOptimizer):
                optimizer = tf.keras.mixed_precision.LossScaleOptimizer(original_optimizer)
                
                # Recompile model with the new optimizer
                model.compile(
                    optimizer=optimizer,
                    loss=model.loss,
                    metrics=model.metrics
                )
                
            return model
        
        except Exception as e:
            print(f"[ML] Error optimizing model for mixed precision: {e}")
            return model