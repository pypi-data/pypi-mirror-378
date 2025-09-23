"""
Test suite for the BiSC algorithm implementation.
"""

__all__ = ['run_all_tests']

def run_all_tests():
    """Run all tests."""
    from .unit.test_permutation import test_permutation
    from .unit.test_mesh_pattern import test_mesh_pattern
    from .unit.test_utils import test_utils
    from .integration.test_bisc_algorithm import test_bisc_algorithm

    print("Running BiSC test suite...")

    # Unit tests
    test_permutation()
    test_mesh_pattern()
    test_utils()

    # Integration tests
    test_bisc_algorithm()

    print("All tests completed!")