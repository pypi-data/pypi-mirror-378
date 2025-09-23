"""
Stack-sortable permutations example.

Stack-sortable permutations are those that can be sorted using a single stack.
They are characterized by avoiding the pattern 231.
"""

from itertools import permutations
from typing import List
from ...core.permutation import Permutation
from ...core.bisc_algorithm import bisc_algorithm
from ...utils.pattern_utils import contains_pattern

def generate_stack_sortable(max_length: int) -> List[Permutation]:
    """
    Generate all stack-sortable permutations up to max_length.

    Args:
        max_length: Maximum length of permutations to generate

    Returns:
        List of stack-sortable permutations
    """
    stack_sortable = []

    for length in range(1, max_length + 1):
        for perm in permutations(range(1, length + 1)):
            perm_list = list(perm)
            # Stack-sortable permutations avoid the pattern 231
            if not contains_pattern(perm_list, [2, 3, 1]):
                stack_sortable.append(Permutation(perm_list))

    return stack_sortable

def demo_stack_sortable():
    """Demonstrate BiSC on stack-sortable permutations."""
    print("=" * 60)
    print("EXAMPLE: Stack-sortable permutations")
    print("=" * 60)

    print("Stack-sortable permutations are those that can be sorted using a single stack.")
    print("Known theorem: They avoid exactly the pattern 231.")
    print()

    # Generate stack-sortable permutations of length ≤ 4
    max_length = 4
    stack_sortable = generate_stack_sortable(max_length)

    print(f"Generated {len(stack_sortable)} stack-sortable permutations of length ≤ {max_length}:")

    # Group by length for display
    by_length = {}
    for perm in stack_sortable:
        length = perm.length
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(perm)

    for length in sorted(by_length.keys()):
        perms = by_length[length]
        print(f"  Length {length}: {[str(p) for p in perms]}")

    print(f"\nRunning BiSC algorithm (pattern length ≤ 3)...")

    # Run BiSC
    forbidden_patterns = bisc_algorithm(stack_sortable, max_pattern_length=3)

    print(f"\nBiSC found {len(forbidden_patterns)} forbidden patterns:")
    for pattern in forbidden_patterns:
        print(f"  {pattern}")

    # Check if we found the expected result
    expected_pattern = [2, 3, 1]
    found_231 = any(pattern.pattern == expected_pattern and pattern.is_classical()
                   for pattern in forbidden_patterns)

    print(f"\nVerification:")
    print(f"  Expected forbidden pattern: {expected_pattern}")
    print(f"  Found by BiSC: {'YES' if found_231 else 'NO'}")

    if found_231:
        print("  SUCCESS: BiSC correctly rediscovered the characterization!")
    else:
        print("  Note: BiSC may have found equivalent or more general patterns")

    return found_231

if __name__ == "__main__":
    demo_stack_sortable()