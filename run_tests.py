#!/usr/bin/env python3
"""
Receipt OCR App - Test Runner Script
"""
import subprocess
import sys
import os

def check_dependencies():
    """Check if testing dependencies are installed"""
    try:
        import pytest
        import pytest_asyncio
        import pytest_mock
        import httpx
        print("✅ All testing dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing testing dependency: {e}")
        print("Installing testing dependencies...")
        return install_test_dependencies()

def install_test_dependencies():
    """Install testing dependencies"""
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0', 
            'pytest-mock>=3.10.0',
            'httpx>=0.24.0',
            'pytest-cov>=4.0.0'
        ], check=True)
        print("✅ Testing dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install testing dependencies")
        return False

def run_tests(test_type="all", verbose=True, coverage=False):
    """Run tests with specified options"""
    cmd = [sys.executable, '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    if test_type == "unit":
        cmd.extend(['-m', 'unit'])
    elif test_type == "integration":
        cmd.extend(['-m', 'integration'])
    elif test_type == "fast":
        cmd.extend(['-m', 'not slow'])
    
    cmd.append('tests/')
    
    print(f"🧪 Running tests: {' '.join(cmd)}")
    return subprocess.run(cmd)

def main():
    """Main test runner function"""
    print("🧾 Receipt OCR App - Test Runner")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    test_type = "all"
    coverage = False
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['unit', 'integration', 'fast']:
            test_type = arg
        elif arg == 'coverage':
            coverage = True
        elif arg == 'help':
            print_help()
            return
    
    # Run tests
    result = run_tests(test_type=test_type, coverage=coverage)
    
    if result.returncode == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(result.returncode)

def print_help():
    """Print help information"""
    print("""
Usage: python run_tests.py [OPTIONS]

Options:
    unit        Run only unit tests
    integration Run only integration tests  
    fast        Run fast tests (exclude slow tests)
    coverage    Run tests with coverage report
    help        Show this help message

Examples:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run unit tests only
    python run_tests.py coverage     # Run with coverage report
    """)

if __name__ == "__main__":
    main()