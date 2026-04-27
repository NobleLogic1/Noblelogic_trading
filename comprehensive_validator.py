#!/usr/bin/env python3
"""
Comprehensive Validation Framework for NobleLogic Trading System
Provides thorough testing and validation of all system components
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import sys
import os
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lazy imports to avoid initialization issues
def get_progressive_exposure_system():
    from progressive_exposure import ProgressiveExposureSystem, ExposureLevel
    return ProgressiveExposureSystem, ExposureLevel

def get_risk_assessment():
    from enhanced_risk_assessment import EnhancedRiskAssessment, RiskMetrics, RiskLevel
    return EnhancedRiskAssessment, RiskMetrics, RiskLevel

def get_ml_integration():
    from ml_integration import MLTradingIntegration
    return MLTradingIntegration

def get_shared_utils():
    from shared_utils import TradingState
    return TradingState

@dataclass
class ValidationResult:
    """Result of a validation test"""
    component: str
    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    execution_time: float
    error_message: str = ""

class ComprehensiveValidator:
    """Comprehensive validation framework for the trading system"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def start_validation(self):
        """Start the validation process"""
        self.start_time = time.time()
        print("🚀 Starting Comprehensive Validation Suite")
        print("=" * 80)

    def end_validation(self):
        """End the validation process and generate report"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        print("\n" + "=" * 80)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("=" * 80)

        # Calculate overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        avg_score = sum(r.score for r in self.results) / total_tests if total_tests > 0 else 0

        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🧪 Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {total_tests - passed_tests}")
        print(f"📈 Average Score: {avg_score:.2%}")

        # Component breakdown
        components = {}
        for result in self.results:
            if result.component not in components:
                components[result.component] = []
            components[result.component].append(result)

        print("\n📋 COMPONENT BREAKDOWN:")
        for component, comp_results in components.items():
            comp_passed = sum(1 for r in comp_results if r.passed)
            comp_score = sum(r.score for r in comp_results) / len(comp_results)
            print(f"  {component}: {comp_passed}/{len(comp_results)} passed ({comp_score:.1%})")

        # Generate detailed report
        self._generate_detailed_report()

        return passed_tests == total_tests

    def _generate_detailed_report(self):
        """Generate detailed validation report"""
        report_path = "validation_report.json"
        report_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "duration_seconds": self.end_time - self.start_time,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "average_score": sum(r.score for r in self.results) / len(self.results) if self.results else 0,
            "results": [
                {
                    "component": r.component,
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "score": r.score,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "error_message": r.error_message
                } for r in self.results
            ]
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_path}")

    def validate_component(self, component: str, test_name: str, test_func):
        """Run a validation test and record results"""
        start_time = time.time()

        try:
            result = test_func()
            execution_time = time.time() - start_time

            if isinstance(result, dict) and 'passed' in result:
                passed = result['passed']
                score = result.get('score', 1.0 if passed else 0.0)
                details = result.get('details', {})
                error_msg = result.get('error_message', '')
            else:
                # Assume boolean return
                passed = bool(result)
                score = 1.0 if passed else 0.0
                details = {}
                error_msg = ''

            validation_result = ValidationResult(
                component=component,
                test_name=test_name,
                passed=passed,
                score=score,
                details=details,
                execution_time=execution_time,
                error_message=error_msg
            )

            self.results.append(validation_result)

            status = "✅" if passed else "❌"
            print(f"{status} {component}.{test_name}: {score:.1%} ({execution_time:.3f}s)")

            if not passed and error_msg:
                print(f"   Error: {error_msg}")

            return passed

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Exception: {str(e)}"

            validation_result = ValidationResult(
                component=component,
                test_name=test_name,
                passed=False,
                score=0.0,
                details={},
                execution_time=execution_time,
                error_message=error_msg
            )

            self.results.append(validation_result)

            print(f"❌ {component}.{test_name}: 0.0% ({execution_time:.3f}s)")
            print(f"   Exception: {str(e)}")

            return False

        except Exception as e:
            execution_time = time.time() - start_time
            validation_result = ValidationResult(
                component=component,
                test_name=test_name,
                passed=False,
                score=0.0,
                details={"exception": str(e)},
                execution_time=execution_time,
                error_message=str(e)
            )
            self.results.append(validation_result)
            print(f"❌ {component}.{test_name}: FAILED ({execution_time:.3f}s)")
            print(f"   Exception: {e}")
            return False

# Global validator instance
validator = ComprehensiveValidator()