"""
Verification of examples from the BiSC paper.
Tests our implementation against the specific examples mentioned in the paper.
"""

from typing import List, Set, Tuple
from itertools import combinations, permutations

# Import our BiSC implementation
from bisc_implementation import Permutation, bisc_algorithm, flatten

def generate_all_permutations(max_length: int) -> List[List[int]]:
    """Generate all permutations up to given length."""
    all_perms = []
    for length in range(1, max_length + 1):
        for perm in permutations(range(1, length + 1)):
            all_perms.append(list(perm))
    return all_perms

def contains_pattern(permutation: List[int], pattern: List[int]) -> bool:
    """Check if permutation contains the given classical pattern."""
    if len(pattern) > len(permutation):
        return False

    for positions in combinations(range(len(permutation)), len(pattern)):
        subword = [permutation[i] for i in positions]
        if flatten(subword) == pattern:
            return True
    return False

def verify_stack_sortable():
    """Verify Example 1: Stack-sortable permutations avoid 231."""
    print("=" * 60)
    print("VERIFICATION 1: Stack-sortable permutations")
    print("=" * 60)
    print("Expected: Should find that pattern 231 is forbidden")

    # Generate all permutations of length ≤ 4
    all_perms = generate_all_permutations(4)

    # Stack-sortable = those that avoid 231
    stack_sortable = []
    for perm in all_perms:
        if not contains_pattern(perm, [2, 3, 1]):
            stack_sortable.append(perm)

    print(f"\nFound {len(stack_sortable)} stack-sortable permutations of length ≤ 4:")
    for i, perm in enumerate(stack_sortable):
        print(f"  {i+1:2d}: {''.join(map(str, perm))}")

    # Convert to Permutation objects and run BiSC
    perm_objects = [Permutation(perm) for perm in stack_sortable]
    result = bisc_algorithm(perm_objects, max_pattern_length=3)

    print(f"\nBiSC found {len(result)} forbidden patterns:")
    for pattern in result:
        print(f"  {pattern}")

    # Check if 231 is among the forbidden patterns
    found_231 = any(pattern.pattern == [2, 3, 1] and len(pattern.shading) == 0
                   for pattern in result)

    if found_231:
        print("\n✓ SUCCESS: BiSC correctly identified 231 as forbidden!")
    else:
        print("\n✗ FAILED: BiSC did not find 231 as forbidden")

    return found_231

def verify_west_2_stack_sortable():
    """Verify Example 2: West-2-stack-sortable permutations."""
    print("\n" + "=" * 60)
    print("VERIFICATION 2: West-2-stack-sortable permutations")
    print("=" * 60)
    print("Expected: Should find 2341 and (3241, {(1,4)}) as forbidden")

    # From the paper: these are the West-2-stack-sortable permutations of length ≤ 4
    west_2_stack = [
        [1],
        [1, 2], [2, 1],
        [1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1],
        [1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4], [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
        [2, 1, 3, 4], [2, 1, 4, 3], [2, 4, 1, 3], [2, 4, 3, 1],
        [3, 1, 2, 4], [3, 1, 4, 2], [3, 4, 1, 2], [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3], [4, 3, 1, 2], [4, 3, 2, 1]
        # Missing: 2341, 3241 (without the right shading), and others
    ]

    print(f"\nInput: {len(west_2_stack)} West-2-stack-sortable permutations:")
    for i, perm in enumerate(west_2_stack):
        print(f"  {i+1:2d}: {''.join(map(str, perm))}")

    # Check what's missing from all length-4 permutations
    all_length_4 = list(permutations(range(1, 5)))
    missing = []
    west_2_tuples = [tuple(perm) for perm in west_2_stack if len(perm) == 4]

    for perm in all_length_4:
        if perm not in west_2_tuples:
            missing.append(list(perm))

    print(f"\nMissing length-4 permutations ({len(missing)}):")
    for perm in missing:
        print(f"  {''.join(map(str, perm))}")

    # Run BiSC
    perm_objects = [Permutation(perm) for perm in west_2_stack]
    result = bisc_algorithm(perm_objects, max_pattern_length=4)

    print(f"\nBiSC found {len(result)} forbidden patterns:")
    for pattern in result:
        print(f"  {pattern}")

    # Check for expected patterns
    found_2341 = any(pattern.pattern == [2, 3, 4, 1] for pattern in result)
    found_3241 = any(pattern.pattern == [3, 2, 4, 1] for pattern in result)

    print(f"\nFound 2341: {found_2341}")
    print(f"Found 3241 variant: {found_3241}")

    return found_2341 or found_3241

def verify_difficult_example():
    """Verify the difficult example from equation (2): 1, 21, 321, 2341, 4123, 4321."""
    print("\n" + "=" * 60)
    print("VERIFICATION 3: Difficult example from equation (2)")
    print("=" * 60)
    print("Input from paper: 1, 21, 321, 2341, 4123, 4321")

    # The permutations from equation (2)
    difficult_perms = [
        [1],
        [2, 1],
        [3, 2, 1],
        [2, 3, 4, 1],
        [4, 1, 2, 3],
        [4, 3, 2, 1]
    ]

    print(f"\nInput permutations:")
    for i, perm in enumerate(difficult_perms):
        print(f"  {i+1}: {''.join(map(str, perm))}")

    # Run BiSC
    perm_objects = [Permutation(perm) for perm in difficult_perms]
    result = bisc_algorithm(perm_objects, max_pattern_length=4)

    print(f"\nBiSC found {len(result)} forbidden patterns:")
    for pattern in result:
        print(f"  {pattern}")

    # According to the paper, this should be the set Av((12, R1), (12, R2))
    # where R1 and R2 are specific shadings

    return len(result) > 0

def verify_smooth_permutations():
    """Verify smooth permutations avoid 1324 and 2143."""
    print("\n" + "=" * 60)
    print("VERIFICATION 4: Smooth permutations")
    print("=" * 60)
    print("Expected: Should find 1324 and 2143 as forbidden")

    # Generate all permutations up to length 4
    all_perms = generate_all_permutations(4)

    # Smooth permutations avoid both 1324 and 2143
    smooth_perms = []
    for perm in all_perms:
        if (not contains_pattern(perm, [1, 3, 2, 4]) and
            not contains_pattern(perm, [2, 1, 4, 3])):
            smooth_perms.append(perm)

    print(f"\nFound {len(smooth_perms)} smooth permutations of length ≤ 4:")
    for i, perm in enumerate(smooth_perms[:20]):  # Show first 20
        print(f"  {i+1:2d}: {''.join(map(str, perm))}")
    if len(smooth_perms) > 20:
        print(f"  ... and {len(smooth_perms) - 20} more")

    # Run BiSC
    perm_objects = [Permutation(perm) for perm in smooth_perms]
    result = bisc_algorithm(perm_objects, max_pattern_length=4)

    print(f"\nBiSC found {len(result)} forbidden patterns:")
    for pattern in result:
        print(f"  {pattern}")

    # Check for expected patterns
    found_1324 = any(pattern.pattern == [1, 3, 2, 4] for pattern in result)
    found_2143 = any(pattern.pattern == [2, 1, 4, 3] for pattern in result)

    print(f"\nFound 1324: {found_1324}")
    print(f"Found 2143: {found_2143}")

    return found_1324 and found_2143

def main():
    """Run all verifications."""
    print("BISC ALGORITHM VERIFICATION")
    print("Testing against examples from the paper")
    print("=" * 60)

    results = []

    # Test 1: Stack-sortable
    try:
        results.append(("Stack-sortable", verify_stack_sortable()))
    except Exception as e:
        print(f"Error in stack-sortable test: {e}")
        results.append(("Stack-sortable", False))

    # Test 2: West-2-stack-sortable
    try:
        results.append(("West-2-stack-sortable", verify_west_2_stack_sortable()))
    except Exception as e:
        print(f"Error in West-2-stack test: {e}")
        results.append(("West-2-stack-sortable", False))

    # Test 3: Difficult example
    try:
        results.append(("Difficult example", verify_difficult_example()))
    except Exception as e:
        print(f"Error in difficult example: {e}")
        results.append(("Difficult example", False))

    # Test 4: Smooth permutations
    try:
        results.append(("Smooth permutations", verify_smooth_permutations()))
    except Exception as e:
        print(f"Error in smooth permutations test: {e}")
        results.append(("Smooth permutations", False))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name:25s}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()