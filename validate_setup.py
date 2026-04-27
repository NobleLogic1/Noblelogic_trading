#!/usr/bin/env python3
"""
Configuration validation script for NobleLogic Trading System
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_configuration():
    """Validate the configuration setup"""
    print("🔍 Validating NobleLogic Trading System Configuration...")

    # Check if config.py exists
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ config.py not found")
        return False

    try:
        from config import get_config, AppConfig
        config = get_config()
        print("✅ Configuration loaded successfully")

        # Validate critical settings
        if config.trading.risk_per_trade > 0.1:
            print("⚠️  Risk per trade is very high (>10%)")

        if config.trading.max_daily_loss > config.trading.initial_capital * 0.5:
            print("⚠️  Max daily loss exceeds 50% of initial capital")

        if config.system.environment == 'production' and not config.api.binance_us_api_key:
            print("❌ Production environment requires Binance API key")
            return False

        print("✅ Configuration validation passed")

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    return True

def validate_dependencies():
    """Validate Python dependencies"""
    print("\n🔍 Validating Python Dependencies...")

    required_packages = [
        'flask', 'tensorflow', 'pandas', 'numpy', 'sklearn'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run 'pip install -r requirements.txt' to install")
        return False

    print("✅ All required packages installed")
    return True

def validate_docker():
    """Validate Docker setup"""
    print("\n🔍 Validating Docker Configuration...")

    docker_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.dockerignore'
    ]

    for file in docker_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            return False

    print("✅ Docker configuration complete")
    return True

def validate_environment():
    """Validate environment setup"""
    print("\n🔍 Validating Environment Setup...")

    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (copy from .env.example)")

    # Check required directories
    directories = ['data', 'logs', 'models']
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️  {dir_name}/ directory missing")
            dir_path.mkdir(exist_ok=True)
            print(f"   Created {dir_name}/ directory")

    return True

def main():
    """Main validation function"""
    print("🚀 NobleLogic Trading System - Configuration Validator")
    print("=" * 60)

    results = []

    # Run all validations
    results.append(("Configuration", validate_configuration()))
    results.append(("Dependencies", validate_dependencies()))
    results.append(("Docker", validate_docker()))
    results.append(("Environment", validate_environment()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY:")

    all_passed = True
    for check, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check}: {status}")
        all_passed = all_passed and passed

    if all_passed:
        print("\n🎉 All validations passed! System is ready to deploy.")
        print("\nNext steps:")
        print("  Development: make docker-dev")
        print("  Production:  make docker-run")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())