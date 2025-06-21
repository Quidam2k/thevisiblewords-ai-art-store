#!/usr/bin/env python3
"""
MCP-Compatible Test Runner
Designed for automated testing with MCP tools
Provides JSON output and standardized exit codes
"""

import sys
import os
import json
import traceback
import importlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class TestResult:
    """Standardized test result"""
    name: str
    module: str
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None

@dataclass
class TestSuiteResult:
    """Test suite execution result"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration_ms: float
    success_rate: float
    results: List[TestResult]
    timestamp: str

class MCPTestRunner:
    def __init__(self):
        self.test_modules = {
            'test_pricing_monitor': 'test_pricing_monitor.TestPricingMonitor',
            'test_cost_analyzer': 'test_cost_analyzer.TestCostAnalyzer', 
            'test_price_adjuster': 'test_price_adjuster.TestPriceAdjuster',
            'test_tag_generator': 'test_tag_generator.TestSmartTagGenerator',
            'test_config_manager': 'test_config_manager.TestConfigManager'
        }
        
        self.verbose = False
        self.json_output = False

    def run_single_test(self, module_name: str, test_class_name: str, test_method: str) -> TestResult:
        """Run a single test method and return result"""
        start_time = datetime.now()
        
        try:
            # Import the test module - remove tests prefix since we're already in tests directory
            module = importlib.import_module(module_name)
            test_class = getattr(module, test_class_name)
            
            # Create test instance
            test_instance = test_class()
            
            # Setup if available
            if hasattr(test_instance, 'setup_method'):
                test_instance.setup_method()
            
            # Run the test
            test_func = getattr(test_instance, test_method)
            test_func()
            
            # Teardown if available
            if hasattr(test_instance, 'teardown_method'):
                test_instance.teardown_method()
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                name=test_method,
                module=module_name,
                passed=True,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                name=test_method,
                module=module_name,
                passed=False,
                duration_ms=duration,
                error_message=str(e),
                error_traceback=traceback.format_exc()
            )

    def run_test_class(self, module_name: str, test_class_name: str) -> List[TestResult]:
        """Run all tests in a test class"""
        results = []
        
        try:
            # Import the test module - remove tests prefix since we're already in tests directory
            module = importlib.import_module(module_name)
            test_class = getattr(module, test_class_name)
            
            # Get all test methods
            test_methods = [method for method in dir(test_class) if method.startswith('test_')]
            
            for test_method in test_methods:
                result = self.run_single_test(module_name, test_class_name, test_method)
                results.append(result)
                
                if self.verbose:
                    status = "✅ PASS" if result.passed else "❌ FAIL"
                    print(f"{status} {module_name}.{test_method} ({result.duration_ms:.1f}ms)")
                    if not result.passed:
                        print(f"    Error: {result.error_message}")
                        
        except ImportError as e:
            results.append(TestResult(
                name="module_import",
                module=module_name,
                passed=False,
                duration_ms=0,
                error_message=f"Could not import module: {e}"
            ))
            
        return results

    def run_test_suite(self, suite_name: str, modules: List[str] = None) -> TestSuiteResult:
        """Run a complete test suite"""
        start_time = datetime.now()
        all_results = []
        
        # Use specified modules or all available
        modules_to_test = modules or list(self.test_modules.keys())
        
        for module_name in modules_to_test:
            if module_name in self.test_modules:
                test_class_name = self.test_modules[module_name].split('.')[-1]
                results = self.run_test_class(module_name, test_class_name)
                all_results.extend(results)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        passed_tests = sum(1 for r in all_results if r.passed)
        failed_tests = len(all_results) - passed_tests
        success_rate = (passed_tests / len(all_results)) * 100 if all_results else 0
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(all_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            duration_ms=duration,
            success_rate=success_rate,
            results=all_results,
            timestamp=datetime.now().isoformat()
        )

    def run_pricing_tests(self) -> TestSuiteResult:
        """Run all pricing-related tests"""
        pricing_modules = ['test_pricing_monitor', 'test_cost_analyzer', 'test_price_adjuster']
        return self.run_test_suite("Pricing System Tests", pricing_modules)

    def run_core_tests(self) -> TestSuiteResult:
        """Run core system tests"""
        core_modules = ['test_tag_generator', 'test_config_manager']
        return self.run_test_suite("Core System Tests", core_modules)

    def run_all_tests(self) -> TestSuiteResult:
        """Run all available tests"""
        return self.run_test_suite("Complete Test Suite")

    def output_results(self, suite_result: TestSuiteResult):
        """Output test results in appropriate format"""
        if self.json_output:
            # JSON output for MCP tools
            result_dict = asdict(suite_result)
            print(json.dumps(result_dict, indent=2))
        else:
            # Human-readable output
            print(f"\n{'='*60}")
            print(f"TEST SUITE: {suite_result.suite_name}")
            print(f"{'='*60}")
            print(f"Timestamp: {suite_result.timestamp}")
            print(f"Duration: {suite_result.duration_ms:.1f}ms")
            print(f"Total Tests: {suite_result.total_tests}")
            print(f"Passed: {suite_result.passed_tests}")
            print(f"Failed: {suite_result.failed_tests}")
            print(f"Success Rate: {suite_result.success_rate:.1f}%")
            
            if suite_result.failed_tests > 0:
                print(f"\n{'='*60}")
                print("FAILED TESTS:")
                print(f"{'='*60}")
                
                for result in suite_result.results:
                    if not result.passed:
                        print(f"\n❌ {result.module}.{result.name}")
                        print(f"   Error: {result.error_message}")
                        if self.verbose and result.error_traceback:
                            print(f"   Traceback:\n{result.error_traceback}")
            
            print(f"\n{'='*60}")
            if suite_result.success_rate == 100:
                print("🎉 ALL TESTS PASSED!")
            elif suite_result.success_rate >= 80:
                print("⚠️  MOSTLY PASSING - Some issues found")
            else:
                print("❌ SIGNIFICANT FAILURES - Review required")
            print(f"{'='*60}\n")

def main():
    """Main entry point for MCP test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP-Compatible Test Runner")
    parser.add_argument('--suite', choices=['pricing', 'core', 'all'], default='all',
                       help='Test suite to run')
    parser.add_argument('--module', help='Run tests for specific module')
    parser.add_argument('--test', help='Run specific test method (requires --module)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--list', action='store_true', help='List available test modules')
    
    args = parser.parse_args()
    
    runner = MCPTestRunner()
    runner.verbose = args.verbose
    runner.json_output = args.json
    
    if args.list:
        print("Available test modules:")
        for module, class_path in runner.test_modules.items():
            print(f"  {module}: {class_path}")
        return 0
    
    try:
        if args.test and args.module:
            # Run specific test
            if args.module not in runner.test_modules:
                print(f"Error: Module '{args.module}' not found")
                return 1
            
            test_class_name = runner.test_modules[args.module].split('.')[-1]
            result = runner.run_single_test(args.module, test_class_name, args.test)
            
            if args.json:
                print(json.dumps(asdict(result), indent=2))
            else:
                status = "PASSED" if result.passed else "FAILED"
                print(f"Test {args.module}.{args.test}: {status}")
                if not result.passed:
                    print(f"Error: {result.error_message}")
            
            return 0 if result.passed else 1
            
        elif args.module:
            # Run all tests in a module
            if args.module not in runner.test_modules:
                print(f"Error: Module '{args.module}' not found")
                return 1
            
            suite_result = runner.run_test_suite(f"{args.module} tests", [args.module])
            
        elif args.suite == 'pricing':
            suite_result = runner.run_pricing_tests()
        elif args.suite == 'core':
            suite_result = runner.run_core_tests()
        else:
            suite_result = runner.run_all_tests()
        
        runner.output_results(suite_result)
        
        # Return appropriate exit code
        if suite_result.success_rate == 100:
            return 0  # All tests passed
        elif suite_result.success_rate >= 50:
            return 1  # Some tests failed
        else:
            return 2  # Many tests failed
            
    except Exception as e:
        if args.json:
            error_result = {
                "error": True,
                "message": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Test runner error: {e}")
            if args.verbose:
                traceback.print_exc()
        
        return 3  # Test runner error

# Additional MCP-friendly functions for programmatic use
def run_tests_json(suite: str = 'all') -> str:
    """Run tests and return JSON result string"""
    runner = MCPTestRunner()
    runner.json_output = True
    
    if suite == 'pricing':
        result = runner.run_pricing_tests()
    elif suite == 'core':
        result = runner.run_core_tests()
    else:
        result = runner.run_all_tests()
    
    return json.dumps(asdict(result), indent=2)

def validate_pricing_system() -> Dict[str, Any]:
    """Validate pricing system and return status"""
    runner = MCPTestRunner()
    result = runner.run_pricing_tests()
    
    return {
        "valid": result.success_rate >= 90,
        "success_rate": result.success_rate,
        "issues": [r.error_message for r in result.results if not r.passed],
        "timestamp": result.timestamp
    }

def run_smoke_test() -> bool:
    """Run basic smoke test - returns True if core functionality works"""
    runner = MCPTestRunner()
    
    # Test core modules only
    core_result = runner.run_core_tests()
    
    # Require 100% pass rate for smoke test
    return core_result.success_rate == 100

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)