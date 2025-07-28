#!/usr/bin/env python3
"""
Test runner for availability functionality
Runs all availability-related tests with proper reporting
"""
import subprocess
import sys
import os

def run_availability_tests():
    """Run all availability tests"""
    print("Running Availability Test Suite")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    test_commands = [
        {
            "name": "Unit Tests - Availability Model & Schema",
            "command": ["python", "-m", "pytest", "smart_buddy/tests/test_availability_model.py", "-v", "--tb=short"],
            "time_estimate": "1.5 hours"
        },
        {
            "name": "API Tests - CRUD Endpoints",
            "command": ["python", "-m", "pytest", "smart_buddy/tests/test_availability_api.py", "-v", "--tb=short"],
            "time_estimate": "2 hours"
        },
        {
            "name": "Integration Tests - Calendar UI Mock",
            "command": ["python", "-m", "pytest", "smart_buddy/tests/test_calendar_integration.py", "-v", "--tb=short"],
            "time_estimate": "2 hours"
        }
    ]
    
    total_tests_passed = 0
    total_tests_failed = 0
    
    for test_suite in test_commands:
        print(f"\n[TEST] {test_suite['name']}")
        print(f"[TIME] Estimated time: {test_suite['time_estimate']}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                test_suite["command"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test suite
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("[PASS] Test suite passed!")
                # Count passed tests (rough estimate)
                passed_count = result.stdout.count(" PASSED")
                total_tests_passed += passed_count
            else:
                print("[FAIL] Test suite failed!")
                failed_count = result.stdout.count(" FAILED")
                total_tests_failed += failed_count
                
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Test suite timed out!")
            total_tests_failed += 1
        except Exception as e:
            print(f"[ERROR] Error running test suite: {e}")
            total_tests_failed += 1
    
    print("\n" + "=" * 50)
    print("AVAILABILITY TEST SUMMARY")
    print("=" * 50)
    print(f"[PASS] Tests Passed: {total_tests_passed}")
    print(f"[FAIL] Tests Failed: {total_tests_failed}")
    
    if total_tests_failed == 0:
        print("SUCCESS: All availability tests passed!")
        return 0
    else:
        print("WARNING: Some tests failed. Please review the output above.")
        return 1

def run_coverage_report():
    """Run tests with coverage reporting"""
    print("\n[COVERAGE] Generating Coverage Report")
    print("-" * 30)
    
    coverage_command = [
        "python", "-m", "pytest",
        "smart_buddy/tests/test_availability_model.py",
        "smart_buddy/tests/test_availability_api.py", 
        "smart_buddy/tests/test_calendar_integration.py",
        "--cov=smart_buddy",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(coverage_command, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] Coverage report generated in htmlcov/index.html")
        else:
            print("[FAIL] Coverage report generation failed")
            
    except Exception as e:
        print(f"[ERROR] Error generating coverage report: {e}")

def run_specific_test(test_file=None):
    """Run a specific test file"""
    if not test_file:
        print("Available test files:")
        print("1. test_availability_model.py - Unit tests for data model & schema")
        print("2. test_availability_api.py - API tests for CRUD endpoints")
        print("3. test_calendar_integration.py - Integration tests with calendar UI mock")
        
        choice = input("\nEnter test file number (1-3) or filename: ").strip()
        
        test_map = {
            "1": "test_availability_model.py",
            "2": "test_availability_api.py", 
            "3": "test_calendar_integration.py"
        }
        
        test_file = test_map.get(choice, choice)
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file += ".py"
    
    test_path = f"smart_buddy/tests/{test_file}"
    
    if not os.path.exists(test_path):
        print(f"[ERROR] Test file not found: {test_path}")
        return 1
    
    print(f"[RUNNING] Running {test_file}")
    command = ["python", "-m", "pytest", test_path, "-v", "--tb=long"]
    
    try:
        result = subprocess.run(command)
        return result.returncode
    except Exception as e:
        print(f"[ERROR] Error running test: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coverage":
            run_coverage_report()
        elif sys.argv[1] == "--specific":
            test_file = sys.argv[2] if len(sys.argv) > 2 else None
            sys.exit(run_specific_test(test_file))
        elif sys.argv[1] == "--help":
            print("Availability Test Runner")
            print("Usage:")
            print("  python run_availability_tests.py           # Run all tests")
            print("  python run_availability_tests.py --coverage # Run with coverage")
            print("  python run_availability_tests.py --specific # Run specific test")
            print("  python run_availability_tests.py --help    # Show this help")
        else:
            print("Unknown option. Use --help for usage information.")
    else:
        sys.exit(run_availability_tests())
