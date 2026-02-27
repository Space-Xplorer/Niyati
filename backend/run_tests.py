"""
Test Runner Script for Project Niyati

This script runs the complete test suite with proper configuration.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --coverage         # Run with coverage report
"""

import sys
import pytest
import argparse


def main():
    """Run the test suite with specified options."""
    
    parser = argparse.ArgumentParser(description='Run Project Niyati tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--slow', action='store_true', help='Include slow tests')
    parser.add_argument('--neo4j', action='store_true', help='Include tests requiring Neo4j')
    parser.add_argument('--llm', action='store_true', help='Include tests requiring LLM API')
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    # Add test markers
    if args.integration:
        pytest_args.extend(['-m', 'integration'])
    elif args.unit:
        pytest_args.extend(['-m', 'unit'])
    
    # Add coverage
    if args.coverage:
        pytest_args.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
    
    # Add verbosity
    if args.verbose:
        pytest_args.append('-vv')
    else:
        pytest_args.append('-v')
    
    # Include slow tests
    if not args.slow:
        pytest_args.extend(['-m', 'not slow'])
    
    # Include Neo4j tests
    if not args.neo4j:
        pytest_args.extend(['-m', 'not requires_neo4j'])
    
    # Include LLM tests
    if not args.llm:
        pytest_args.extend(['-m', 'not requires_llm'])
    
    # Add test directory
    pytest_args.append('tests/')
    
    # Show output
    pytest_args.append('-s')
    
    print("="*80)
    print("Project Niyati Test Suite")
    print("="*80)
    print(f"Running tests with arguments: {' '.join(pytest_args)}")
    print("="*80 + "\n")
    
    # Run pytest
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*80)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
