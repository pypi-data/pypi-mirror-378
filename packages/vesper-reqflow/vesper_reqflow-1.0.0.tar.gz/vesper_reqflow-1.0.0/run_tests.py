#!/usr/bin/env python3
"""Test runner script for API Tester CLI."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run API Tester CLI tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "cli", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Skip slow tests"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--linting", 
        action="store_true", 
        help="Run linting checks"
    )
    parser.add_argument(
        "--format-check", 
        action="store_true", 
        help="Check code formatting"
    )
    parser.add_argument(
        "--type-check", 
        action="store_true", 
        help="Run type checking"
    )
    parser.add_argument(
        "--security", 
        action="store_true", 
        help="Run security checks"
    )
    parser.add_argument(
        "--all-checks", 
        action="store_true", 
        help="Run all checks (linting, formatting, type checking, security)"
    )
    
    args = parser.parse_args()
    
    # Set up base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add test type filters
    if args.type == "unit":
        pytest_cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        pytest_cmd.extend(["-m", "integration"])
    elif args.type == "cli":
        pytest_cmd.extend(["-m", "cli"])
    
    # Add options
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    
    if args.coverage:
        pytest_cmd.extend([
            "--cov=src/apitester",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    # Run all checks if requested
    if args.all_checks:
        args.linting = True
        args.format_check = True
        args.type_check = True
        args.security = True
    
    success = True
    
    # Run linting
    if args.linting:
        print("\n" + "="*60)
        print("RUNNING LINTING CHECKS")
        print("="*60)
        
        # Flake8
        if not run_command(
            ["python", "-m", "flake8", "src/", "tests/"],
            "Flake8 linting"
        ):
            success = False
        
        # Pylint
        if not run_command(
            ["python", "-m", "pylint", "src/apitester/"],
            "Pylint analysis"
        ):
            success = False
    
    # Run format checking
    if args.format_check:
        print("\n" + "="*60)
        print("RUNNING FORMAT CHECKS")
        print("="*60)
        
        # Black
        if not run_command(
            ["python", "-m", "black", "--check", "--diff", "src/", "tests/"],
            "Black format checking"
        ):
            success = False
        
        # isort
        if not run_command(
            ["python", "-m", "isort", "--check-only", "--diff", "src/", "tests/"],
            "isort import sorting check"
        ):
            success = False
    
    # Run type checking
    if args.type_check:
        print("\n" + "="*60)
        print("RUNNING TYPE CHECKS")
        print("="*60)
        
        # MyPy
        if not run_command(
            ["python", "-m", "mypy", "src/apitester/"],
            "MyPy type checking"
        ):
            success = False
    
    # Run security checks
    if args.security:
        print("\n" + "="*60)
        print("RUNNING SECURITY CHECKS")
        print("="*60)
        
        # Bandit
        if not run_command(
            ["python", "-m", "bandit", "-r", "src/"],
            "Bandit security analysis"
        ):
            success = False
        
        # Safety
        if not run_command(
            ["python", "-m", "safety", "check"],
            "Safety dependency check"
        ):
            success = False
    
    # Run tests
    print("\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60)
    
    if not run_command(pytest_cmd, f"Pytest {args.type} tests"):
        success = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if success:
        print("✅ All tests and checks passed!")
        return 0
    else:
        print("❌ Some tests or checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())