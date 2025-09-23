"""
Smooth permutations example.

Smooth permutations are related to smooth Schubert varieties in algebraic geometry.
They are characterized by avoiding patterns 1324 and 2143.
"""

from itertools import permutations
from typing import List
from ...core.permutation import Permutation
from ...core.bisc_algorithm import bisc_algorithm
from ...utils.pattern_utils import contains_pattern

def generate_smooth_permutations(max_length: int) -> List[Permutation]:
    """
    Generate all smooth permutations up to max_length.

    Args:
        max_length: Maximum length of permutations to generate

    Returns:
        List of smooth permutations
    """
    smooth_perms = []

    for length in range(1, max_length + 1):
        for perm in permutations(range(1, length + 1)):
            perm_list = list(perm)
            # Smooth permutations avoid both 1324 and 2143
            if (not contains_pattern(perm_list, [1, 3, 2, 4]) and
                not contains_pattern(perm_list, [2, 1, 4, 3])):
                smooth_perms.append(Permutation(perm_list))

    return smooth_perms

def demo_smooth_permutations():
    """Demonstrate BiSC on smooth permutations."""
    print("=" * 60)
    print("EXAMPLE: Smooth permutations")
    print("=" * 60)

    print("Smooth permutations correspond to smooth Schubert varieties.")
    print("Known theorem (Lakshmibai-Sandhya 1990): They avoid patterns 1324 and 2143.")
    print()

    # Generate smooth permutations of length ≤ 4
    max_length = 4
    smooth_perms = generate_smooth_permutations(max_length)

    print(f"Generated {len(smooth_perms)} smooth permutations of length ≤ {max_length}:")

    # Show counts by length
    by_length = {}
    for perm in smooth_perms:
        length = perm.length
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(perm)

    for length in sorted(by_length.keys()):
        perms = by_length[length]
        count = len(perms)
        examples = [str(p) for p in perms[:8]]  # Show first 8
        if count > 8:
            examples.append(f"... +{count-8} more")
        print(f"  Length {length}: {count} permutations - {examples}")

    print(f"\nRunning BiSC algorithm (pattern length ≤ 4)...")

    # Run BiSC
    forbidden_patterns = bisc_algorithm(smooth_perms, max_pattern_length=4)

    print(f"\nBiSC found {len(forbidden_patterns)} forbidden patterns:")
    for pattern in forbidden_patterns:
        print(f"  {pattern}")

    # Check if we found the expected results
    expected_patterns = [[1, 3, 2, 4], [2, 1, 4, 3]]
    found_1324 = any(pattern.pattern == [1, 3, 2, 4] and pattern.is_classical()
                    for pattern in forbidden_patterns)
    found_2143 = any(pattern.pattern == [2, 1, 4, 3] and pattern.is_classical()
                    for pattern in forbidden_patterns)

    print(f"\nVerification:")
    print(f"  Expected forbidden patterns: {expected_patterns}")
    print(f"  Found 1324: {'✓' if found_1324 else '✗'}")
    print(f"  Found 2143: {'✓' if found_2143 else '✗'}")

    success = found_1324 and found_2143
    if success:
        print("  SUCCESS: BiSC correctly rediscovered both forbidden patterns!")
    else:
        print("  Note: BiSC may have found equivalent or more general patterns")

    return success

if __name__ == "__main__":
    demo_smooth_permutations()