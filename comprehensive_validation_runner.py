#!/usr/bin/env python3
"""
Comprehensive Validation Runner for NobleLogic Trading System
Executes all validation tests and generates comprehensive reports
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_validator import validator

def analyze_performance():
    """Analyze system performance from validation results"""

    # Extract performance-related results
    performance_tests = [
        result for result in validator.results
        if 'performance' in result.test_name.lower() or 'speed' in result.test_name.lower()
    ]

    if not performance_tests:
        return {"status": "No performance tests found"}

    avg_execution_time = sum(r.execution_time for r in performance_tests) / len(performance_tests)
    slowest_test = max(performance_tests, key=lambda r: r.execution_time)
    fastest_test = min(performance_tests, key=lambda r: r.execution_time)

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "performance_tests_count": len(performance_tests),
        "average_execution_time": avg_execution_time,
        "slowest_test": {
            "component": slowest_test.component,
            "test_name": slowest_test.test_name,
            "execution_time": slowest_test.execution_time
        },
        "fastest_test": {
            "component": fastest_test.component,
            "test_name": fastest_test.test_name,
            "execution_time": fastest_test.execution_time
        },
        "performance_score": 1.0 - min(1.0, avg_execution_time / 10.0)  # Penalize slow tests
    }

def analyze_risk_assessment():
    """Analyze risk assessment from validation results"""

    risk_tests = [
        result for result in validator.results
        if 'risk' in result.component.lower() or 'exposure' in result.component.lower()
    ]

    if not risk_tests:
        return {"status": "No risk-related tests found"}

    risk_passed = sum(1 for r in risk_tests if r.passed)
    risk_score = sum(r.score for r in risk_tests) / len(risk_tests)

    # Analyze exposure limits
    exposure_tests = [
        result for result in validator.results
        if 'exposure' in result.test_name.lower()
    ]

    exposure_compliance = all(r.passed for r in exposure_tests) if exposure_tests else True

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "risk_tests_count": len(risk_tests),
        "risk_tests_passed": risk_passed,
        "risk_score": risk_score,
        "exposure_compliance": exposure_compliance,
        "risk_components_tested": list(set(r.component for r in risk_tests)),
        "recommendations": [
            "Regular risk limit reviews",
            "Continuous exposure monitoring",
            "Automated risk alerts" if risk_score > 0.9 else "Risk assessment improvements needed"
        ]
    }

def analyze_system_health():
    """Analyze overall system health from validation results"""

    total_tests = len(validator.results)
    passed_tests = sum(1 for r in validator.results if r.passed)
    failed_tests = total_tests - passed_tests

    # Component health
    components = {}
    for result in validator.results:
        if result.component not in components:
            components[result.component] = []
        components[result.component].append(result)

    component_health = {}
    for comp, results in components.items():
        comp_passed = sum(1 for r in results if r.passed)
        comp_score = sum(r.score for r in results) / len(results)
        component_health[comp] = {
            "tests_run": len(results),
            "tests_passed": comp_passed,
            "health_score": comp_score,
            "status": "Healthy" if comp_score >= 0.9 else "Needs Attention" if comp_score >= 0.7 else "Critical"
        }

    # Error analysis
    errors = [r for r in validator.results if not r.passed]
    error_categories = {}
    for error in errors:
        category = error.error_message.split(':')[0] if ':' in error.error_message else "Unknown"
        error_categories[category] = error_categories.get(category, 0) + 1

    # Overall health assessment
    overall_score = sum(r.score for r in validator.results) / total_tests if total_tests > 0 else 0

    if overall_score >= 0.95:
        health_status = "Excellent"
        recommendations = ["Maintain current standards", "Consider advanced features"]
    elif overall_score >= 0.85:
        health_status = "Good"
        recommendations = ["Monitor for improvements", "Address minor issues"]
    elif overall_score >= 0.70:
        health_status = "Fair"
        recommendations = ["Prioritize critical fixes", "Improve test coverage"]
    else:
        health_status = "Poor"
        recommendations = ["Immediate attention required", "Comprehensive system review"]

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "overall_health_score": overall_score,
        "health_status": health_status,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "component_health": component_health,
        "error_categories": error_categories,
        "recommendations": recommendations,
        "next_validation_suggested": (datetime.now() + timedelta(days=7)).isoformat()
    }

def run_comprehensive_validation():
    """Run the complete validation suite using direct function calls"""

    # Define test suites to run
    test_suites = [
        ("Progressive Exposure", "tests.test_progressive_exposure_validation", "run_progressive_exposure_validation"),
        ("Risk Assessment", "tests.test_risk_assessment_validation", "run_risk_assessment_validation"),
        ("ML Integration", "tests.test_ml_integration_validation", "run_ml_integration_validation"),
        ("System Integration", "tests.test_system_integration_validation", "run_system_integration_validation"),
    ]

    # Start comprehensive validation
    validator.start_validation()

    print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏗️  System: NobleLogic Trading System")
    print(f"🎯 Target: Complete system validation with proper setup_method initialization")
    print("=" * 80)

    total_tests_run = 0
    total_passed = 0
    total_failed = 0
    suite_results = []

    # Run all validation suites using direct function calls (ensures setup_method is called)
    for suite_name, module_name, function_name in test_suites:
        print(f"\n🔍 Running {suite_name} Validation Suite")
        print("-" * 60)

        try:
            # Import the module and run the validation function
            module = __import__(module_name, fromlist=[function_name])
            validation_func = getattr(module, function_name)
            validation_func()

            # Count results for this suite
            suite_results_all = [r for r in validator.results if r.component == suite_name.replace(" ", "") or suite_name in r.component]
            suite_passed = sum(1 for r in suite_results_all if r.passed)
            suite_total = len(suite_results_all)

            suite_results.append({
                "suite_name": suite_name,
                "success": suite_passed == suite_total,
                "tests_run": suite_total,
                "passed": suite_passed,
                "failed": suite_total - suite_passed,
                "errors": []
            })

            total_tests_run += suite_total
            total_passed += suite_passed
            total_failed += (suite_total - suite_passed)

            if suite_total > 0:
                success_rate = suite_passed / suite_total
                print(f"✅ {suite_name} validation completed")
                print(f"   📊 Tests run: {suite_total}, Passed: {suite_passed}, Failed: {suite_total - suite_passed} ({success_rate:.1%})")
            else:
                print(f"⚠️  {suite_name} validation completed but no tests were recorded")

        except Exception as e:
            print(f"❌ {suite_name} validation failed: {e}")
            suite_results.append({
                "suite_name": suite_name,
                "success": False,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": [str(e)]
            })

    # Summary of all suites
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUITE SUMMARY")
    print("=" * 80)
    print(f"🎯 Total Test Suites: {len(test_suites)}")
    print(f"🧪 Total Tests Run: {total_tests_run}")
    print(f"✅ Total Tests Passed: {total_passed}")
    print(f"❌ Total Tests Failed: {total_failed}")
    if total_tests_run > 0:
        print(f"📈 Overall Success Rate: {total_passed/total_tests_run:.1%}")
    else:
        print("📈 Overall Success Rate: N/A (no tests run)")

    for result in suite_results:
        status_icon = "✅" if result["success"] else "⚠️"
        if result["tests_run"] > 0:
            print(f"   {status_icon} {result['suite_name']}: {result['passed']}/{result['tests_run']} passed")
        else:
            print(f"   {status_icon} {result['suite_name']}: No tests executed")

    # End validation and generate report
    success = validator.end_validation()

    # Generate additional reports
    generate_additional_reports()

    return success

def generate_additional_reports():
    """Generate additional validation reports"""

    # Performance analysis report
    performance_report = analyze_performance()
    with open("performance_analysis.json", 'w') as f:
        json.dump(performance_report, f, indent=2, default=str)

    # Risk assessment report
    risk_report = analyze_risk_assessment()
    with open("risk_assessment_report.json", 'w') as f:
        json.dump(risk_report, f, indent=2, default=str)

    # System health report
    health_report = analyze_system_health()
    with open("system_health_report.json", 'w') as f:
        json.dump(health_report, f, indent=2, default=str)

    print("\n📊 Additional Reports Generated:")
    print("   📈 performance_analysis.json")
    print("   🛡️  risk_assessment_report.json")
    print("   ❤️  system_health_report.json")

def analyze_performance():
    """Analyze system performance from validation results"""

    # Extract performance-related results
    performance_tests = [
        result for result in validator.results
        if 'performance' in result.test_name.lower() or 'speed' in result.test_name.lower()
    ]

    if not performance_tests:
        return {"status": "No performance tests found"}

    avg_execution_time = sum(r.execution_time for r in performance_tests) / len(performance_tests)
    slowest_test = max(performance_tests, key=lambda r: r.execution_time)
    fastest_test = min(performance_tests, key=lambda r: r.execution_time)

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "performance_tests_count": len(performance_tests),
        "average_execution_time": avg_execution_time,
        "slowest_test": {
            "component": slowest_test.component,
            "test_name": slowest_test.test_name,
            "execution_time": slowest_test.execution_time
        },
        "fastest_test": {
            "component": fastest_test.component,
            "test_name": fastest_test.test_name,
            "execution_time": fastest_test.execution_time
        },
        "performance_score": 1.0 - min(1.0, avg_execution_time / 10.0)  # Penalize slow tests
    }

def analyze_risk_assessment():
    """Analyze risk assessment from validation results"""

    risk_tests = [
        result for result in validator.results
        if 'risk' in result.component.lower() or 'exposure' in result.component.lower()
    ]

    if not risk_tests:
        return {"status": "No risk-related tests found"}

    risk_passed = sum(1 for r in risk_tests if r.passed)
    risk_score = sum(r.score for r in risk_tests) / len(risk_tests)

    # Analyze exposure limits
    exposure_tests = [
        result for result in validator.results
        if 'exposure' in result.test_name.lower()
    ]

    exposure_compliance = all(r.passed for r in exposure_tests) if exposure_tests else True

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "risk_tests_count": len(risk_tests),
        "risk_tests_passed": risk_passed,
        "risk_score": risk_score,
        "exposure_compliance": exposure_compliance,
        "risk_components_tested": list(set(r.component for r in risk_tests)),
        "recommendations": [
            "Regular risk limit reviews",
            "Continuous exposure monitoring",
            "Automated risk alerts" if risk_score > 0.9 else "Risk assessment improvements needed"
        ]
    }

def analyze_system_health():
    """Analyze overall system health from validation results"""

    total_tests = len(validator.results)
    passed_tests = sum(1 for r in validator.results if r.passed)
    failed_tests = total_tests - passed_tests

    # Component health
    components = {}
    for result in validator.results:
        if result.component not in components:
            components[result.component] = []
        components[result.component].append(result)

    component_health = {}
    for comp, results in components.items():
        comp_passed = sum(1 for r in results if r.passed)
        comp_score = sum(r.score for r in results) / len(results)
        component_health[comp] = {
            "tests_run": len(results),
            "tests_passed": comp_passed,
            "health_score": comp_score,
            "status": "Healthy" if comp_score >= 0.9 else "Needs Attention" if comp_score >= 0.7 else "Critical"
        }

    # Error analysis
    errors = [r for r in validator.results if not r.passed]
    error_categories = {}
    for error in errors:
        category = error.error_message.split(':')[0] if ':' in error.error_message else "Unknown"
        error_categories[category] = error_categories.get(category, 0) + 1

    # Overall health assessment
    overall_score = sum(r.score for r in validator.results) / total_tests if total_tests > 0 else 0

    if overall_score >= 0.95:
        health_status = "Excellent"
        recommendations = ["Maintain current standards", "Consider advanced features"]
    elif overall_score >= 0.85:
        health_status = "Good"
        recommendations = ["Monitor for improvements", "Address minor issues"]
    elif overall_score >= 0.70:
        health_status = "Fair"
        recommendations = ["Prioritize critical fixes", "Improve test coverage"]
    else:
        health_status = "Poor"
        recommendations = ["Immediate attention required", "Comprehensive system review"]

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "overall_health_score": overall_score,
        "health_status": health_status,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "component_health": component_health,
        "error_categories": error_categories,
        "recommendations": recommendations,
        "next_validation_suggested": (datetime.now() + timedelta(days=7)).isoformat()
    }

def main():
    """Main validation execution"""
    print("🎯 NobleLogic Trading System - Comprehensive Validation")
    print("=" * 80)

    try:
        success = run_comprehensive_validation()

        print("\n" + "=" * 80)
        if success:
            print("🎉 COMPREHENSIVE VALIDATION COMPLETED SUCCESSFULLY!")
            print("✅ All critical systems validated and operational")
            print("📊 Detailed reports available in project root")
            return 0
        else:
            print("⚠️  COMPREHENSIVE VALIDATION COMPLETED WITH ISSUES")
            print("❌ Some systems require attention")
            print("📊 Check detailed reports for specific issues")
            return 1

    except Exception as e:
        print(f"\n❌ VALIDATION SUITE FAILED: {e}")
        print("🔍 Check system configuration and dependencies")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)