"""
Model Management Utilities for NobleLogic Trading
Advanced model versioning, checkpointing, and mixed precision training
"""

import os
import json
import time
from datetime import datetime
import tensorflow as tf
import numpy as np
from pathlib import Path

class ModelManager:
    def __init__(self, base_path=None):
        """
        Initialize ModelManager with specified paths for versioning and checkpoints
        
        Args:
            base_path (str): Base path for model storage
        """
        if base_path is None:
            # Set default path based on project structure
            self.base_path = os.path.join(os.path.dirname(__file__), 'models')
        else:
            self.base_path = base_path
            
        # Set up paths
        self.checkpoint_path = os.path.join(self.base_path, 'checkpoints')
        self.versioned_path = os.path.join(self.base_path, 'versioned')
        self.config_path = os.path.join(self.base_path, 'config')
        
        # Create directories if they don't exist
        os.makedirs(self.checkpoint_path, exist_ok=True)
        os.makedirs(self.versioned_path, exist_ok=True)
        os.makedirs(self.config_path, exist_ok=True)
        
        # Initialize versioning
        self.current_version = self._get_latest_version()
        
        print(f"[MODEL] ModelManager initialized: version {self.current_version}")
    
    def _get_latest_version(self):
        """Get the latest model version number"""
        versions = [0]  # Default to 0 if no versions found
        
        # Look for versioned models
        for item in os.listdir(self.versioned_path):
            if os.path.isdir(os.path.join(self.versioned_path, item)) and item.startswith('v'):
                try:
                    version_num = int(item[1:])  # Extract number from 'v123'
                    versions.append(version_num)
                except ValueError:
                    pass
                    
        return max(versions)
    
    def save_checkpoint(self, model, custom_metrics=None):
        """
        Save a checkpoint of the current model
        
        Args:
            model: TensorFlow model to checkpoint
            custom_metrics (dict): Additional metrics to store
            
        Returns:
            str: Path to the saved checkpoint
        """
        timestamp = int(time.time())
        checkpoint_filename = f"checkpoint_{timestamp}"
        checkpoint_dir = os.path.join(self.checkpoint_path, checkpoint_filename)
        
        # Save model weights
        model.save_weights(checkpoint_dir)
        
        # Save additional metrics
        if custom_metrics:
            metrics_file = os.path.join(checkpoint_dir, 'metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(custom_metrics, f, indent=2)
        
        print(f"[MODEL] Checkpoint saved: {checkpoint_filename}")
        return checkpoint_dir
    
    def save_versioned_model(self, model, performance_metrics=None, bump_version=True):
        """
        Save a versioned copy of the model
        
        Args:
            model: TensorFlow model to version
            performance_metrics (dict): Performance metrics for this version
            bump_version (bool): Whether to increment the version number
            
        Returns:
            int: New version number
        """
        if bump_version:
            self.current_version += 1
            
        version_str = f"v{self.current_version}"
        version_dir = os.path.join(self.versioned_path, version_str)
        
        # Create version directory
        os.makedirs(version_dir, exist_ok=True)
        
        # Save full model with architecture
        model_path = os.path.join(version_dir, 'model.keras')
        model.save(model_path)
        
        # Save metadata
        metadata = {
            'version': self.current_version,
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': performance_metrics or {},
            'architecture': model.to_json()
        }
        
        metadata_path = os.path.join(version_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[MODEL] Saved versioned model: {version_str}")
        return self.current_version
    
    def load_latest_model(self):
        """Load the latest versioned model"""
        version_str = f"v{self.current_version}"
        version_dir = os.path.join(self.versioned_path, version_str)
        
        if not os.path.exists(version_dir):
            print(f"[MODEL] No versioned model found at {version_dir}")
            return None
        
        model_path = os.path.join(version_dir, 'model.keras')
        try:
            model = tf.keras.models.load_model(model_path)
            print(f"[MODEL] Loaded versioned model: {version_str}")
            return model
        except Exception as e:
            print(f"[MODEL] Error loading model: {e}")
            return None
    
    def load_specific_version(self, version):
        """Load a specific model version"""
        version_str = f"v{version}"
        version_dir = os.path.join(self.versioned_path, version_str)
        
        if not os.path.exists(version_dir):
            print(f"[MODEL] Model version {version_str} not found")
            return None
        
        model_path = os.path.join(version_dir, 'model.keras')
        try:
            model = tf.keras.models.load_model(model_path)
            print(f"[MODEL] Loaded model version: {version_str}")
            return model
        except Exception as e:
            print(f"[MODEL] Error loading model version {version_str}: {e}")
            return None
    
    def get_model_metadata(self, version=None):
        """Get metadata for a specific version or current version"""
        if version is None:
            version = self.current_version
            
        version_str = f"v{version}"
        metadata_path = os.path.join(self.versioned_path, version_str, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            return None
            
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def list_available_versions(self):
        """List all available model versions"""
        versions = []
        
        for item in os.listdir(self.versioned_path):
            if os.path.isdir(os.path.join(self.versioned_path, item)) and item.startswith('v'):
                try:
                    version_num = int(item[1:])
                    metadata = self.get_model_metadata(version_num)
                    versions.append({
                        'version': version_num,
                        'created_at': metadata.get('timestamp', 'Unknown') if metadata else 'Unknown',
                        'performance': metadata.get('performance_metrics', {}) if metadata else {}
                    })
                except (ValueError, FileNotFoundError):
                    pass
        
        # Sort by version number
        versions.sort(key=lambda x: x['version'])
        return versions