"""
Command-line interface for the BiSC algorithm package.

This module provides console commands for running examples and demonstrations.
"""

import sys
import argparse
from . import __version__

def run_examples():
    """Run the main BiSC algorithm examples."""
    print(f"BiSC Algorithm Examples (v{__version__})")
    print("=" * 50)

    try:
        from .examples.known_classes.stack_sortable import demo_stack_sortable
        from .examples.known_classes.smooth_permutations import demo_smooth_permutations

        print("Running stack-sortable permutations example...")
        success1 = demo_stack_sortable()

        print("\nRunning smooth permutations example...")
        success2 = demo_smooth_permutations()

        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Stack-sortable: {'PASS' if success1 else 'FAIL'}")
        print(f"Smooth perms:   {'PASS' if success2 else 'FAIL'}")

        if success1 and success2:
            print("\nAll examples completed successfully!")
            return 0
        else:
            print("\nSome examples failed or had issues.")
            return 1

    except Exception as e:
        print(f"Error running examples: {e}")
        return 1

def run_demo():
    """Run the comprehensive BiSC demonstration."""
    print(f"BiSC Algorithm Demonstration (v{__version__})")
    print("=" * 50)

    try:
        # Import and run the demo
        from .examples import bisc_demo
        # The demo module should have a main function
        if hasattr(bisc_demo, 'demonstrate_bisc'):
            bisc_demo.demonstrate_bisc()
        else:
            print("Demo function not found. Running basic info...")
            print_basic_info()
        return 0

    except Exception as e:
        print(f"Error running demo: {e}")
        print("Running basic information instead...")
        print_basic_info()
        return 1

def print_basic_info():
    """Print basic information about the BiSC algorithm."""
    print("""
BiSC Algorithm - Pattern Discovery in Permutations

The BiSC algorithm automatically discovers forbidden patterns in sets of
permutations. It consists of two main steps:

1. MINE: Find all mesh patterns that appear in input permutations
2. GEN: Generate forbidden patterns from allowed patterns

Key Features:
- Rediscovers known theorems (stack-sortable, smooth permutations)
- Handles both classical and mesh patterns
- Automated conjecture generation
- Educational demonstrations

Usage:
  from bisc_package import Permutation, bisc_algorithm

  # Create permutations
  perms = [Permutation([1,2,3]), Permutation([1,3,2])]

  # Discover patterns
  forbidden = bisc_algorithm(perms, 3)

  # Analyze results
  for pattern in forbidden:
      print(pattern)

For more examples, run: bisc-examples
""")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BiSC Algorithm - Pattern Discovery in Permutations",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'bisc-algorithm {__version__}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Examples command
    examples_parser = subparsers.add_parser('examples', help='Run example demonstrations')

    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run comprehensive demonstration')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show basic information')

    args = parser.parse_args()

    if args.command == 'examples':
        return run_examples()
    elif args.command == 'demo':
        return run_demo()
    elif args.command == 'info':
        print_basic_info()
        return 0
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())