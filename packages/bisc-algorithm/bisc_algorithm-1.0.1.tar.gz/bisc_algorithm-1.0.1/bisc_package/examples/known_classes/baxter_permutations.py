"""
Baxter permutations example.

Baxter permutations have applications in various areas of mathematics
and are characterized by avoiding certain mesh patterns.
"""

from itertools import permutations
from typing import List
from ...core.permutation import Permutation
from ...core.bisc_algorithm import bisc_algorithm
from ...utils.pattern_utils import contains_pattern

def generate_baxter_approximation(max_length: int) -> List[Permutation]:
    """
    Generate an approximation of Baxter permutations using classical patterns.

    Note: True Baxter permutations are defined by mesh patterns (2413, {(2,2)})
    and (3142, {(2,2)}), but we use classical patterns as an approximation.

    Args:
        max_length: Maximum length of permutations to generate

    Returns:
        List of permutations avoiding classical patterns 2413 and 3142
    """
    baxter_approx = []

    for length in range(1, max_length + 1):
        for perm in permutations(range(1, length + 1)):
            perm_list = list(perm)
            # Approximate by avoiding classical patterns 2413 and 3142
            if (not contains_pattern(perm_list, [2, 4, 1, 3]) and
                not contains_pattern(perm_list, [3, 1, 4, 2])):
                baxter_approx.append(Permutation(perm_list))

    return baxter_approx

def demo_baxter_permutations():
    """Demonstrate the complexity of Baxter permutations."""
    print("=" * 60)
    print("EXAMPLE: Baxter permutations (classical approximation)")
    print("=" * 60)

    print("True Baxter permutations avoid mesh patterns (2413, {(2,2)}) and (3142, {(2,2)}).")
    print("Here we show the classical pattern approximation and its limitations.")
    print()

    # Generate approximation using classical patterns
    max_length = 5
    baxter_approx = generate_baxter_approximation(max_length)

    print(f"Classical approximation: {len(baxter_approx)} permutations (length ≤ {max_length})")

    # Show counts by length
    by_length = {}
    for perm in baxter_approx:
        length = perm.length
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(perm)

    # Known Baxter numbers for comparison
    known_baxter = [1, 1, 2, 6, 22]

    print("Comparison with true Baxter numbers:")
    for length in range(1, max_length + 1):
        our_count = len(by_length.get(length, []))
        true_count = known_baxter[length - 1] if length <= len(known_baxter) else "?"
        match = "✓" if our_count == true_count else "✗"
        print(f"  Length {length}: found {our_count:3d}, true Baxter {true_count:3d} {match}")

    print("\nAs we can see, classical patterns are insufficient!")
    print("The mesh pattern constraints (2,2) are crucial for the correct count.")

    print(f"\nRunning BiSC on classical approximation...")

    # Run BiSC on our approximation
    forbidden_patterns = bisc_algorithm(baxter_approx[:20], 4)  # Limit for performance

    print(f"\nBiSC found {len(forbidden_patterns)} forbidden patterns:")
    for pattern in forbidden_patterns[:5]:  # Show first 5
        print(f"  {pattern}")
    if len(forbidden_patterns) > 5:
        print(f"  ... and {len(forbidden_patterns) - 5} more")

    print("\nConclusion:")
    print("- Classical pattern analysis is insufficient for Baxter permutations")
    print("- True Baxter permutations require mesh pattern constraints")
    print("- This demonstrates the power and necessity of mesh patterns")

    return True

if __name__ == "__main__":
    demo_baxter_permutations()