#!/usr/bin/env python3
"""
Fast dependency checker for NobleLogic Trading System
Uses lightweight imports to avoid loading heavy ML libraries
"""

import sys
import importlib.util
import time

def check_package_installed(package_name):
    """Check if a package is installed without importing it"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def fast_dependency_check():
    """Fast dependency check without heavy imports"""
    print("🔍 Fast dependency check...")
    start_time = time.time()
    
    # Core dependencies (safe to import)
    safe_imports = {
        'flask': 'Flask web framework',
        'requests': 'HTTP requests',
        'numpy': 'NumPy arrays',
        'pandas': 'Data analysis',
    }
    
    # Heavy ML dependencies (check without importing)
    heavy_packages = {
        'tensorflow': 'TensorFlow ML framework',
        'torch': 'PyTorch ML framework', 
        'transformers': 'Hugging Face Transformers',
        'sklearn': 'Scikit-learn ML library',
    }
    
    all_good = True
    
    # Check safe imports
    print("\n📦 Checking core dependencies...")
    for package, description in safe_imports.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description}")
            all_good = False
    
    # Check heavy packages without importing
    print("\n🧠 Checking ML dependencies (fast check)...")
    for package, description in heavy_packages.items():
        if check_package_installed(package):
            print(f"✅ {package} - {description}")
        else:
            print(f"❌ {package} - {description}")
            all_good = False
    
    elapsed = time.time() - start_time
    print(f"\n⚡ Dependency check completed in {elapsed:.2f} seconds")
    
    return all_good

if __name__ == "__main__":
    success = fast_dependency_check()
    if success:
        print("\n🎉 All dependencies available!")
        sys.exit(0)
    else:
        print("\n⚠️  Some dependencies missing. Run: pip install -r requirements.txt")
        sys.exit(1)