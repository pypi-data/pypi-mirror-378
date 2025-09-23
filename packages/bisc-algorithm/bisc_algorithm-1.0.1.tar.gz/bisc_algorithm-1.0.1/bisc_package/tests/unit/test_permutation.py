"""
Unit tests for the Permutation class.
"""

from ...core.permutation import Permutation

def test_permutation():
    """Test basic Permutation functionality."""
    print("Testing Permutation class...")

    # Test creation
    p = Permutation([3, 1, 2])
    assert str(p) == "312"
    assert p.length == 3

    # Test subwords
    subwords = p.subwords(2)
    expected_subwords = [
        ([], []),
        ([3], [0]),
        ([1], [1]),
        ([2], [2]),
        ([3, 1], [0, 1]),
        ([3, 2], [0, 2]),
        ([1, 2], [1, 2])
    ]

    assert len(subwords) == len(expected_subwords)
    for subword, positions in subwords:
        assert (subword, positions) in expected_subwords

    # Test pattern containment
    assert p.contains_classical_pattern([2, 1])  # 31 at positions 0,1
    assert p.contains_classical_pattern([1, 2])  # 12 at positions 1,2
    assert not p.contains_classical_pattern([1, 3, 2])  # Would need length 4+

    # Test transformations
    assert p.reverse().sequence == [2, 1, 3]
    assert p.complement().sequence == [1, 3, 2]
    assert p.inverse().sequence == [2, 3, 1]

    print("  ✓ Permutation tests passed")

def test_permutation_validation():
    """Test permutation validation."""
    print("Testing Permutation validation...")

    # Valid permutations
    try:
        Permutation([1])
        Permutation([2, 1])
        Permutation([1, 3, 2])
        print("  ✓ Valid permutations accepted")
    except ValueError:
        print("  ✗ Valid permutations rejected")
        raise

    # Invalid permutations
    try:
        Permutation([1, 1])  # Duplicate
        print("  ✗ Invalid permutation accepted")
        raise AssertionError("Should have rejected duplicate values")
    except ValueError:
        print("  ✓ Duplicate values rejected")

    try:
        Permutation([1, 3])  # Gap in values
        print("  ✗ Invalid permutation accepted")
        raise AssertionError("Should have rejected gap in values")
    except ValueError:
        print("  ✓ Gap in values rejected")

if __name__ == "__main__":
    test_permutation()
    test_permutation_validation()