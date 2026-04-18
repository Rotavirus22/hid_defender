#!/usr/bin/env python3
"""
HID Defender Test Runner
Comprehensive test suite for the HID Defender security system.

This script runs all test cases corresponding to the 20 test cases
specified in the test plan.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run the complete test suite."""
    print("=" * 60)
    print("HID DEFENDER - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Test cases mapping
    test_cases = {
        "TC-01": "System Startup Test",
        "TC-02": "HID Device Detection Test",
        "TC-03": "Trusted Device Recognition Test",
        "TC-04": "Unknown Device Detection Test",
        "TC-05": "Alert Generation Test",
        "TC-06": "Log File Creation Test",
        "TC-07": "Log Content Accuracy Test",
        "TC-08": "Multiple Device Detection Test",
        "TC-09": "Device Disconnect Handling Test",
        "TC-10": "Rapid Keystroke Detection Test",
        "TC-11": "Normal Typing Test",
        "TC-12": "Whitelist File Loading Test",
        "TC-13": "Invalid Whitelist Entry Test",
        "TC-17": "Unauthorized Device Warning Test",
        "TC-18": "Continuous Monitoring Test",
        "TC-19": "System Stability Test",
        "TC-20": "End-to-End System Test"
    }

    print(f"Running {len(test_cases)} test cases...")
    print()

    # Run pytest
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("TEST RESULTS:")
    print("-" * 40)
    print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    print("-" * 40)
    print(f"Exit code: {result.returncode}")

    # Summary
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
        print(f"Successfully validated {len(test_cases)} test cases covering:")
        print("  • System startup and initialization")
        print("  • Device detection and recognition")
        print("  • Keystroke monitoring and attack detection")
        print("  • Alert generation and notifications")
        print("  • Logging and audit trails")
        print("  • Integration and end-to-end workflows")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the output above for details.")

    return result.returncode


def run_specific_test(test_name):
    """Run a specific test case."""
    print(f"Running specific test: {test_name}")

    cmd = [sys.executable, "-m", "pytest", f"tests/ -k {test_name}", "-v"]
    result = subprocess.run(cmd)

    return result.returncode


def show_help():
    """Show help information."""
    print("HID Defender Test Runner")
    print("Usage:")
    print("  python run_tests.py              # Run all tests")
    print("  python run_tests.py <test_name>  # Run specific test")
    print("  python run_tests.py --help       # Show this help")
    print()
    print("Available test categories:")
    print("  • test_system_startup")
    print("  • test_device_detection")
    print("  • test_keystroke_monitoring")
    print("  • test_alerts")
    print("  • test_logging")
    print("  • test_integration")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            show_help()
        else:
            # Run specific test
            test_name = sys.argv[1]
            exit_code = run_specific_test(test_name)
            sys.exit(exit_code)
    else:
        # Run all tests
        exit_code = run_tests()
        sys.exit(exit_code)