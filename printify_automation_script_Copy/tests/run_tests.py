#!/usr/bin/env python3
"""
Test runner for the Enhanced Printify Automation Tool
Runs all available tests and provides a summary
"""

import sys
import os
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_module(module_name, test_class_name):
    """Run all tests in a test module"""
    print(f"\n{'='*50}")
    print(f"Running {module_name} tests...")
    print(f"{'='*50}")
    
    try:
        # Import the test module
        module = __import__(f"tests.{module_name}", fromlist=[test_class_name])
        test_class = getattr(module, test_class_name)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        if not test_methods:
            print(f"⚠️  No test methods found in {test_class_name}")
            return 0, 0
        
        # Create test instance
        test_instance = test_class()
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                # Setup if available
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run the test
                method = getattr(test_instance, test_method)
                method()
                
                print(f"✅ {test_method}")
                passed += 1
                
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed += 1
                
            finally:
                # Teardown if available
                if hasattr(test_instance, 'teardown_method'):
                    try:
                        test_instance.teardown_method()
                    except:
                        pass
        
        print(f"\n{module_name} Results: {passed} passed, {failed} failed")
        return passed, failed
        
    except ImportError as e:
        print(f"❌ Could not import {module_name}: {e}")
        return 0, 1
    except Exception as e:
        print(f"❌ Error running {module_name} tests: {e}")
        traceback.print_exc()
        return 0, 1


def main():
    """Run all tests"""
    print("🧪 Enhanced Printify Automation Tool - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_passed = 0
    total_failed = 0
    
    # List of test modules to run
    test_modules = [
        ("test_tag_generator", "TestSmartTagGenerator"),
        ("test_config_manager", "TestConfigManager"),
        ("test_pricing_monitor", "TestPricingMonitor"),
        ("test_cost_analyzer", "TestCostAnalyzer"),
        ("test_price_adjuster", "TestPriceAdjuster"),
    ]
    
    for module_name, test_class_name in test_modules:
        passed, failed = run_test_module(module_name, test_class_name)
        total_passed += passed
        total_failed += failed
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")
    print(f"Success rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "No tests run")
    
    if total_failed == 0 and total_passed > 0:
        print("🎉 All tests passed!")
        return 0
    elif total_failed > 0:
        print("⚠️  Some tests failed")
        return 1
    else:
        print("⚠️  No tests were run")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)