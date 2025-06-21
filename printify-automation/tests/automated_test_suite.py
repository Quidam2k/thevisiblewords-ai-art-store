#!/usr/bin/env python3
"""
Automated Test Suite for MCP Tools
Comprehensive testing with CI/CD compatibility
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class AutomatedTestSuite:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        
        # Test configuration
        self.test_timeout = 300  # 5 minutes
        self.parallel_tests = False  # Can be enabled for faster execution
        
        # Results tracking
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def check_environment(self) -> Dict[str, Any]:
        """Check if test environment is ready"""
        checks = {
            "python_version": sys.version_info[:2],
            "project_root_exists": self.project_root.exists(),
            "src_directory_exists": self.src_dir.exists(),
            "test_directory_exists": self.test_dir.exists(),
            "required_modules": [],
            "missing_modules": []
        }
        
        # Check for required source modules
        required_modules = [
            "pricing_monitor.py",
            "cost_analyzer.py", 
            "price_adjuster.py",
            "tag_generator.py",
            "config_manager.py"
        ]
        
        for module in required_modules:
            module_path = self.src_dir / module
            if module_path.exists():
                checks["required_modules"].append(module)
            else:
                checks["missing_modules"].append(module)
        
        # Check Python version
        checks["python_compatible"] = sys.version_info >= (3, 7)
        
        # Overall status
        checks["environment_ready"] = (
            checks["project_root_exists"] and
            checks["src_directory_exists"] and
            checks["test_directory_exists"] and
            checks["python_compatible"] and
            len(checks["missing_modules"]) == 0
        )
        
        return checks

    def run_mcp_test_runner(self, suite: str = "all", format_json: bool = True) -> Dict[str, Any]:
        """Run the MCP test runner and parse results"""
        try:
            cmd = [
                sys.executable,
                str(self.test_dir / "mcp_test_runner.py"),
                "--suite", suite
            ]
            
            if format_json:
                cmd.append("--json")
            
            # Run the test command
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.test_timeout
            )
            
            if format_json:
                try:
                    output = json.loads(result.stdout)
                    output["exit_code"] = result.returncode
                    output["stderr"] = result.stderr
                    return output
                except json.JSONDecodeError:
                    return {
                        "error": True,
                        "message": "Could not parse JSON output",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_code": result.returncode
                    }
            else:
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "message": f"Tests timed out after {self.test_timeout} seconds",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "exit_code": -1
            }

    def run_individual_tests(self) -> Dict[str, Any]:
        """Run individual test modules for detailed analysis"""
        test_modules = [
            ("pricing_monitor", "TestPricingMonitor"),
            ("cost_analyzer", "TestCostAnalyzer"),
            ("price_adjuster", "TestPriceAdjuster"),
            ("tag_generator", "TestSmartTagGenerator"),
            ("config_manager", "TestConfigManager")
        ]
        
        results = {}
        
        for module_name, test_class in test_modules:
            try:
                result = self.run_mcp_test_runner("all", format_json=True)
                # Filter results for this specific module
                if "results" in result:
                    module_results = [r for r in result["results"] if r["module"] == module_name]
                    results[module_name] = {
                        "total_tests": len(module_results),
                        "passed": sum(1 for r in module_results if r["passed"]),
                        "failed": sum(1 for r in module_results if not r["passed"]),
                        "results": module_results
                    }
                else:
                    results[module_name] = {"error": "No results found"}
                    
            except Exception as e:
                results[module_name] = {"error": str(e)}
        
        return results

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-focused tests"""
        performance_results = {}
        
        # Test import times
        import_times = {}
        modules_to_test = ["pricing_monitor", "cost_analyzer", "price_adjuster", "tag_generator", "config_manager"]
        
        for module in modules_to_test:
            start_time = time.time()
            try:
                # Test import time
                cmd = [
                    sys.executable, 
                    "-c", 
                    f"import sys; sys.path.insert(0, 'src'); import {module}"
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=30
                )
                
                import_time = time.time() - start_time
                import_times[module] = {
                    "import_time_ms": import_time * 1000,
                    "success": result.returncode == 0,
                    "error": result.stderr if result.returncode != 0 else None
                }
                
            except Exception as e:
                import_times[module] = {
                    "import_time_ms": -1,
                    "success": False,
                    "error": str(e)
                }
        
        performance_results["import_times"] = import_times
        
        # Test memory usage (if psutil available)
        try:
            import psutil
            process = psutil.Process()
            performance_results["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024
            performance_results["cpu_percent"] = process.cpu_percent()
        except ImportError:
            performance_results["memory_usage_mb"] = -1
            performance_results["cpu_percent"] = -1
        
        return performance_results

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests between modules"""
        integration_results = {}
        
        # Test 1: Pricing Monitor + Cost Analyzer integration
        try:
            cmd = [
                sys.executable,
                "-c",
                """
import sys
sys.path.insert(0, 'src')
from pricing_monitor import PricingMonitor, CostData
from cost_analyzer import CostAnalyzer, CostBreakdown

# Test integration
monitor = PricingMonitor()
analyzer = CostAnalyzer()

# Create test data
cost_data = CostData(variant_id=123, base_cost=800, shipping_cost=200, processing_fee=100, total_cost=1100)
breakdown = analyzer.analyze_cost_structure(800, 1999)

print("Integration test passed")
"""
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            integration_results["pricing_monitor_cost_analyzer"] = {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            integration_results["pricing_monitor_cost_analyzer"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 2: Price Adjuster + Pricing Monitor integration
        try:
            cmd = [
                sys.executable,
                "-c",
                """
import sys
sys.path.insert(0, 'src')
from pricing_monitor import PricingMonitor, PriceAlert
from price_adjuster import PriceAdjuster

# Test integration
monitor = PricingMonitor()
adjuster = PriceAdjuster(monitor)

# Create test alert
alert = PriceAlert(
    product_id="test",
    variant_id=123,
    alert_type="cost_increase",
    old_value=1100,
    new_value=1210,
    threshold=5.0,
    severity="medium",
    message="Test"
)

# Process alert
adjustment = adjuster.process_cost_change_alert(alert)
print("Integration test passed")
"""
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            integration_results["price_adjuster_pricing_monitor"] = {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            integration_results["price_adjuster_pricing_monitor"] = {
                "success": False,
                "error": str(e)
            }
        
        return integration_results

    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete automated test suite"""
        self.start_time = datetime.now()
        
        print("🧪 Starting Automated Test Suite...")
        print(f"Project Root: {self.project_root}")
        print(f"Start Time: {self.start_time}")
        
        # Step 1: Environment Check
        print("\n1️⃣ Checking Environment...")
        env_check = self.check_environment()
        
        if not env_check["environment_ready"]:
            return {
                "success": False,
                "stage": "environment_check",
                "error": "Environment not ready",
                "details": env_check
            }
        
        print("✅ Environment check passed")
        
        # Step 2: Core Tests
        print("\n2️⃣ Running Core Tests...")
        core_tests = self.run_mcp_test_runner("core", format_json=True)
        
        # Step 3: Pricing Tests
        print("\n3️⃣ Running Pricing Tests...")
        pricing_tests = self.run_mcp_test_runner("pricing", format_json=True)
        
        # Step 4: All Tests
        print("\n4️⃣ Running Complete Test Suite...")
        all_tests = self.run_mcp_test_runner("all", format_json=True)
        
        # Step 5: Performance Tests
        print("\n5️⃣ Running Performance Tests...")
        performance_tests = self.run_performance_tests()
        
        # Step 6: Integration Tests
        print("\n6️⃣ Running Integration Tests...")
        integration_tests = self.run_integration_tests()
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Compile results
        results = {
            "success": True,
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": duration,
            "environment_check": env_check,
            "core_tests": core_tests,
            "pricing_tests": pricing_tests,
            "all_tests": all_tests,
            "performance_tests": performance_tests,
            "integration_tests": integration_tests,
            "summary": self._generate_summary(core_tests, pricing_tests, all_tests, integration_tests)
        }
        
        return results

    def _generate_summary(self, core_tests: Dict, pricing_tests: Dict, 
                         all_tests: Dict, integration_tests: Dict) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            "overall_success": True,
            "total_test_count": 0,
            "total_passed": 0,
            "total_failed": 0,
            "success_rate": 0.0,
            "stage_results": {}
        }
        
        # Analyze core tests
        if "total_tests" in core_tests:
            summary["stage_results"]["core"] = {
                "success": core_tests.get("success_rate", 0) >= 90,
                "tests": core_tests.get("total_tests", 0),
                "passed": core_tests.get("passed_tests", 0),
                "success_rate": core_tests.get("success_rate", 0)
            }
        
        # Analyze pricing tests
        if "total_tests" in pricing_tests:
            summary["stage_results"]["pricing"] = {
                "success": pricing_tests.get("success_rate", 0) >= 90,
                "tests": pricing_tests.get("total_tests", 0),
                "passed": pricing_tests.get("passed_tests", 0),
                "success_rate": pricing_tests.get("success_rate", 0)
            }
        
        # Analyze all tests
        if "total_tests" in all_tests:
            summary["total_test_count"] = all_tests.get("total_tests", 0)
            summary["total_passed"] = all_tests.get("passed_tests", 0)
            summary["total_failed"] = all_tests.get("failed_tests", 0)
            summary["success_rate"] = all_tests.get("success_rate", 0)
        
        # Analyze integration tests
        integration_success = all(
            result.get("success", False) 
            for result in integration_tests.values()
        )
        summary["stage_results"]["integration"] = {
            "success": integration_success,
            "tests": len(integration_tests),
            "passed": sum(1 for r in integration_tests.values() if r.get("success", False))
        }
        
        # Overall success
        summary["overall_success"] = (
            summary["success_rate"] >= 80 and
            integration_success and
            summary["stage_results"].get("core", {}).get("success", False)
        )
        
        return summary

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        results_file = self.project_root / filename
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        return str(results_file)

def main():
    """Main entry point for automated testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Test Suite")
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--quick', action='store_true', help='Run quick test suite only')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    # Initialize test suite
    suite = AutomatedTestSuite(args.project_root)
    
    try:
        if args.quick:
            # Quick test: just run core tests
            results = suite.run_mcp_test_runner("core", format_json=True)
        else:
            # Full test suite
            results = suite.run_full_test_suite()
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Human-readable summary
            if "summary" in results:
                summary = results["summary"]
                print(f"\n{'='*60}")
                print("AUTOMATED TEST SUITE SUMMARY")
                print(f"{'='*60}")
                print(f"Overall Success: {'✅ YES' if summary.get('overall_success') else '❌ NO'}")
                print(f"Total Tests: {summary.get('total_test_count', 0)}")
                print(f"Passed: {summary.get('total_passed', 0)}")
                print(f"Failed: {summary.get('total_failed', 0)}")
                print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
                
                if "stage_results" in summary:
                    print(f"\nStage Results:")
                    for stage, data in summary["stage_results"].items():
                        status = "✅" if data.get("success") else "❌"
                        print(f"  {status} {stage.capitalize()}: {data.get('passed', 0)}/{data.get('tests', 0)} passed")
                
                print(f"{'='*60}")
        
        # Save results if requested
        if args.save:
            suite.save_results(results)
        
        # Return appropriate exit code
        if "summary" in results:
            return 0 if results["summary"].get("overall_success") else 1
        else:
            return 0 if results.get("success", False) else 1
            
    except Exception as e:
        if args.json:
            error_result = {
                "error": True,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Test suite failed: {e}")
        
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)