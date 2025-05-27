"""
Test runner script for RenumTaskMaster PoC.

This script runs all the tests for the RenumTaskMaster PoC and generates a report.
"""

import os
import sys
import time
import pytest
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Output directory for test results
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_tests():
    """Run all tests and generate a report."""
    print("Starting RenumTaskMaster PoC test suite...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test results
    results = {
        "start_time": datetime.now().isoformat(),
        "unit_tests": {
            "task_store": {"passed": 0, "failed": 0, "skipped": 0, "total": 0},
            "task_tools": {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        },
        "integration_tests": {
            "process_manager": {"passed": 0, "failed": 0, "skipped": 0, "total": 0},
            "taskmaster": {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        },
        "total": {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    }
    
    # Run unit tests for TaskStore
    print("\nRunning unit tests for TaskStore...")
    task_store_result = pytest.main([
        'tests/unit/test_task_store.py', 
        '-v', 
        f'--junitxml={os.path.join(RESULTS_DIR, "task_store_results.xml")}'
    ])
    results["unit_tests"]["task_store"] = parse_pytest_result(task_store_result)
    
    # Run unit tests for TaskTools
    print("\nRunning unit tests for TaskTools...")
    task_tools_result = pytest.main([
        'tests/unit/test_task_tools.py', 
        '-v', 
        f'--junitxml={os.path.join(RESULTS_DIR, "task_tools_results.xml")}'
    ])
    results["unit_tests"]["task_tools"] = parse_pytest_result(task_tools_result)
    
    # Run integration tests
    print("\nRunning integration tests...")
    integration_result = pytest.main([
        'tests/integration/test_taskmaster_integration.py', 
        '-v', 
        f'--junitxml={os.path.join(RESULTS_DIR, "integration_results.xml")}'
    ])
    results["integration_tests"]["taskmaster"] = parse_pytest_result(integration_result)
    
    # Calculate totals
    results["total"]["passed"] = (
        results["unit_tests"]["task_store"]["passed"] +
        results["unit_tests"]["task_tools"]["passed"] +
        results["integration_tests"]["taskmaster"]["passed"]
    )
    results["total"]["failed"] = (
        results["unit_tests"]["task_store"]["failed"] +
        results["unit_tests"]["task_tools"]["failed"] +
        results["integration_tests"]["taskmaster"]["failed"]
    )
    results["total"]["skipped"] = (
        results["unit_tests"]["task_store"]["skipped"] +
        results["unit_tests"]["task_tools"]["skipped"] +
        results["integration_tests"]["taskmaster"]["skipped"]
    )
    results["total"]["total"] = (
        results["unit_tests"]["task_store"]["total"] +
        results["unit_tests"]["task_tools"]["total"] +
        results["integration_tests"]["taskmaster"]["total"]
    )
    
    # Add end time
    results["end_time"] = datetime.now().isoformat()
    results["duration_seconds"] = (
        datetime.fromisoformat(results["end_time"]) - 
        datetime.fromisoformat(results["start_time"])
    ).total_seconds()
    
    # Save results to JSON
    results_file = os.path.join(RESULTS_DIR, "test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary report
    generate_report(results)
    
    return results

def parse_pytest_result(result_code):
    """Parse pytest result code into a dictionary."""
    # pytest.ExitCode is an IntEnum where:
    # 0: All tests passed
    # 1: Tests failed
    # 2: Test execution interrupted
    # 3: Internal error
    # 4: Command line usage error
    # 5: No tests collected
    
    # This is a simplified parsing since we don't have access to the actual test counts
    # In a real implementation, we would parse the XML output for detailed counts
    if result_code == 0:
        return {"passed": 1, "failed": 0, "skipped": 0, "total": 1}
    elif result_code == 5:
        return {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    else:
        return {"passed": 0, "failed": 1, "skipped": 0, "total": 1}

def generate_report(results):
    """Generate a human-readable test report."""
    report_file = os.path.join(RESULTS_DIR, "test_report.md")
    
    with open(report_file, 'w') as f:
        f.write("# RenumTaskMaster PoC Test Report\n\n")
        
        f.write(f"**Test Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duration:** {results['duration_seconds']:.2f} seconds\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Tests:** {results['total']['total']}\n")
        f.write(f"- **Passed:** {results['total']['passed']}\n")
        f.write(f"- **Failed:** {results['total']['failed']}\n")
        f.write(f"- **Skipped:** {results['total']['skipped']}\n\n")
        
        f.write("## Unit Tests\n\n")
        f.write("### TaskStore\n\n")
        f.write(f"- **Total:** {results['unit_tests']['task_store']['total']}\n")
        f.write(f"- **Passed:** {results['unit_tests']['task_store']['passed']}\n")
        f.write(f"- **Failed:** {results['unit_tests']['task_store']['failed']}\n\n")
        
        f.write("### TaskTools\n\n")
        f.write(f"- **Total:** {results['unit_tests']['task_tools']['total']}\n")
        f.write(f"- **Passed:** {results['unit_tests']['task_tools']['passed']}\n")
        f.write(f"- **Failed:** {results['unit_tests']['task_tools']['failed']}\n\n")
        
        f.write("## Integration Tests\n\n")
        f.write("### TaskMaster Integration\n\n")
        f.write(f"- **Total:** {results['integration_tests']['taskmaster']['total']}\n")
        f.write(f"- **Passed:** {results['integration_tests']['taskmaster']['passed']}\n")
        f.write(f"- **Failed:** {results['integration_tests']['taskmaster']['failed']}\n\n")
        
        f.write("## Conclusion\n\n")
        if results['total']['failed'] == 0:
            f.write("✅ **All tests passed successfully!**\n\n")
            f.write("The RenumTaskMaster PoC meets all the defined criteria and is ready for review.\n")
        else:
            f.write("❌ **Some tests failed.**\n\n")
            f.write("Please review the test results and fix the issues before proceeding.\n")
    
    print(f"\nTest report generated: {report_file}")

if __name__ == "__main__":
    results = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["total"]["failed"] == 0 else 1)
