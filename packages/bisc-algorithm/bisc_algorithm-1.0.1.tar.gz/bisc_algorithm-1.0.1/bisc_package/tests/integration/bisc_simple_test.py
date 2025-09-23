"""
Simplified test of the BiSC algorithm focusing on basic functionality.
"""

from typing import List, Set, Tuple, Dict, FrozenSet
from itertools import combinations

class Permutation:
    """Represents a permutation in one-line notation."""

    def __init__(self, sequence: List[int]):
        self.sequence = sequence
        self.length = len(sequence)

    def __str__(self):
        return ''.join(map(str, self.sequence))

    def __repr__(self):
        return f"Perm({self.sequence})"

    def subwords(self, max_length: int) -> List[Tuple[List[int], List[int]]]:
        """Returns all subwords of length at most max_length with their positions."""
        subwords = []

        # Generate all subwords of length 1 to max_length (skip empty for simplicity)
        for length in range(1, min(max_length + 1, self.length + 1)):
            for positions in combinations(range(self.length), length):
                subword = [self.sequence[i] for i in positions]
                subwords.append((subword, list(positions)))

        return subwords

def flatten(word: List[int]) -> List[int]:
    """Flattens a word to a permutation by replacing values with their relative order."""
    if not word:
        return []

    sorted_unique = sorted(set(word))
    rank_map = {val: i + 1 for i, val in enumerate(sorted_unique)}
    return [rank_map[val] for val in word]

def simple_mine_test():
    """Simple test of the MINE concept with manual verification."""
    print("=== Simple BiSC Test ===")

    # Test with a very simple case: permutations that avoid 231
    # Input: all permutations of length ≤ 3 except 231
    perms = [
        Permutation([1]),
        Permutation([1, 2]),
        Permutation([2, 1]),
        Permutation([1, 2, 3]),
        Permutation([1, 3, 2]),
        Permutation([2, 1, 3]),
        # Missing [2, 3, 1] which is the pattern 231
        Permutation([3, 1, 2]),
        Permutation([3, 2, 1]),
    ]

    print("Input permutations:")
    for p in perms:
        print(f"  {p}")

    print("\nAnalyzing patterns of length ≤ 3...")

    # Track which patterns appear
    patterns_seen = set()

    for perm in perms:
        subwords = perm.subwords(3)
        print(f"\nPermutation {perm}:")

        for subword, positions in subwords:
            pattern = flatten(subword)
            pattern_tuple = tuple(pattern)
            patterns_seen.add(pattern_tuple)
            print(f"  Subword {subword} at positions {positions} -> pattern {pattern}")

    print(f"\nAll patterns seen: {sorted(patterns_seen)}")

    # Generate all possible patterns of length ≤ 3
    all_patterns = set()
    all_patterns.add((1,))
    all_patterns.add((1, 2))
    all_patterns.add((2, 1))
    all_patterns.add((1, 2, 3))
    all_patterns.add((1, 3, 2))
    all_patterns.add((2, 1, 3))
    all_patterns.add((2, 3, 1))  # This is 231
    all_patterns.add((3, 1, 2))
    all_patterns.add((3, 2, 1))

    missing_patterns = all_patterns - patterns_seen
    print(f"Missing patterns (should be forbidden): {sorted(missing_patterns)}")

    # Expected result: (2, 3, 1) should be the only missing pattern
    if missing_patterns == {(2, 3, 1)}:
        print("SUCCESS: Correctly identified that pattern 231 is forbidden!")
    else:
        print("Something went wrong...")

def test_flatten():
    """Test the flatten function."""
    print("\n=== Testing flatten function ===")
    test_cases = [
        ([1, 2, 3], [1, 2, 3]),
        ([3, 1, 2], [3, 1, 2]),  # This should stay as 312
        ([4, 8, 2], [2, 3, 1]),  # This should give 231
        ([2, 3, 1], [2, 3, 1]),
    ]

    for input_word, expected in test_cases:
        result = flatten(input_word)
        print(f"flatten({input_word}) = {result}, expected {expected}")
        if result == expected:
            print("  CORRECT")
        else:
            print("  INCORRECT")

if __name__ == "__main__":
    test_flatten()
    simple_mine_test()