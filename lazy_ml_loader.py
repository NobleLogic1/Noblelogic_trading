"""
Lazy ML Library Loader for NobleLogic Trading System
Delays heavy ML library imports until actually needed
"""

import importlib
import importlib.util
import sys
from typing import Optional, Any


class LazyMLLoader:
    """Lazy loader for heavy ML libraries to speed up startup"""
    
    def __init__(self):
        self._tensorflow = None
        self._torch = None
        self._transformers = None
        self._sklearn = None
        
    @property
    def tensorflow(self):
        """Lazy load TensorFlow"""
        if self._tensorflow is None:
            print("🧠 Loading TensorFlow...")
            self._tensorflow = importlib.import_module('tensorflow')
        return self._tensorflow
    
    @property 
    def torch(self):
        """Lazy load PyTorch"""
        if self._torch is None:
            print("🔥 Loading PyTorch...")
            self._torch = importlib.import_module('torch')
        return self._torch
    
    @property
    def transformers(self):
        """Lazy load Transformers"""
        if self._transformers is None:
            print("🤖 Loading Transformers...")
            self._transformers = importlib.import_module('transformers')
        return self._transformers
    
    @property
    def sklearn(self):
        """Lazy load Scikit-learn"""
        if self._sklearn is None:
            print("📊 Loading Scikit-learn...")
            self._sklearn = importlib.import_module('sklearn')
        return self._sklearn
    
    def is_available(self, library: str) -> bool:
        """Check if library is available without loading it"""
        try:
            spec = importlib.util.find_spec(library)
            return spec is not None
        except (ImportError, ValueError):
            return False
    
    def get_available_ml_frameworks(self) -> dict:
        """Get dict of available ML frameworks without loading them"""
        return {
            'tensorflow': self.is_available('tensorflow'),
            'torch': self.is_available('torch'), 
            'transformers': self.is_available('transformers'),
            'sklearn': self.is_available('sklearn'),
        }


# Global lazy loader instance
ml_loader = LazyMLLoader()

# Convenience functions
def get_tensorflow():
    """Get TensorFlow module (lazy loaded)"""
    return ml_loader.tensorflow

def get_torch(): 
    """Get PyTorch module (lazy loaded)"""
    return ml_loader.torch

def get_transformers():
    """Get Transformers module (lazy loaded)"""
    return ml_loader.transformers

def get_sklearn():
    """Get Scikit-learn module (lazy loaded)"""
    return ml_loader.sklearn

def check_ml_availability() -> dict:
    """Fast check of ML library availability"""
    return ml_loader.get_available_ml_frameworks()


if __name__ == "__main__":
    # Test the lazy loader
    print("🔍 Checking ML framework availability...")
    availability = check_ml_availability()
    
    for framework, available in availability.items():
        status = "✅" if available else "❌"
        print(f"{status} {framework}")
    
    print(f"\n⚡ Check completed instantly!")
    
    if availability['tensorflow']:
        print("\nTesting lazy TensorFlow load...")
        tf = get_tensorflow()
        print(f"TensorFlow version: {tf.__version__}")