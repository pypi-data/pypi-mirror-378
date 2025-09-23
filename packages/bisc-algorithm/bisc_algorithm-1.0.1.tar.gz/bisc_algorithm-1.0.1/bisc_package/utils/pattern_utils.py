"""
Pattern manipulation utilities for the BiSC algorithm.
"""

from typing import List
from itertools import combinations, permutations

def flatten(word: List[int]) -> List[int]:
    """
    Flatten a word to a permutation by replacing values with their relative order.

    This is a fundamental operation in pattern analysis. Given a word of distinct
    integers, it replaces the i-th smallest value with i.

    Args:
        word: List of distinct integers

    Returns:
        The flattened permutation

    Examples:
        >>> flatten([3, 1, 4])
        [2, 1, 3]
        >>> flatten([5, 2, 8, 1])
        [3, 2, 4, 1]
    """
    if not word:
        return []

    sorted_unique = sorted(set(word))
    rank_map = {val: i + 1 for i, val in enumerate(sorted_unique)}
    return [rank_map[val] for val in word]

def contains_pattern(permutation: List[int], pattern: List[int]) -> bool:
    """
    Check if permutation contains the given classical pattern.

    Args:
        permutation: The permutation to search in
        pattern: The pattern to search for

    Returns:
        True if the pattern is contained, False otherwise

    Examples:
        >>> contains_pattern([3, 1, 4, 2], [2, 1])
        True
        >>> contains_pattern([1, 2, 3], [3, 2, 1])
        False
    """
    if len(pattern) > len(permutation):
        return False

    for positions in combinations(range(len(permutation)), len(pattern)):
        subword = [permutation[i] for i in positions]
        if flatten(subword) == pattern:
            return True
    return False

def generate_all_permutations(max_length: int) -> List[List[int]]:
    """
    Generate all permutations up to a given length.

    Args:
        max_length: Maximum length of permutations to generate

    Returns:
        List of all permutations of length 1 to max_length
    """
    all_perms = []
    for length in range(1, max_length + 1):
        for perm in permutations(range(1, length + 1)):
            all_perms.append(list(perm))
    return all_perms

def find_missing_patterns(input_perms: List[List[int]], max_pattern_length: int) -> List[List[int]]:
    """
    Find classical patterns that are missing from the input set.

    Args:
        input_perms: List of input permutations
        max_pattern_length: Maximum length of patterns to consider

    Returns:
        List of missing patterns
    """
    # Generate all possible patterns up to max_pattern_length
    all_patterns = []
    for length in range(1, max_pattern_length + 1):
        for perm in permutations(range(1, length + 1)):
            all_patterns.append(list(perm))

    # Find which patterns appear in the input
    patterns_seen = set()
    for perm in input_perms:
        for pattern_length in range(1, min(len(perm) + 1, max_pattern_length + 1)):
            for positions in combinations(range(len(perm)), pattern_length):
                subword = [perm[i] for i in positions]
                pattern = flatten(subword)
                patterns_seen.add(tuple(pattern))

    # Find missing patterns
    missing = []
    for pattern in all_patterns:
        if tuple(pattern) not in patterns_seen:
            missing.append(pattern)

    return missing

def permutation_to_string(perm: List[int]) -> str:
    """
    Convert a permutation to a string representation.

    Args:
        perm: The permutation as a list

    Returns:
        String representation
    """
    return ''.join(map(str, perm))

def string_to_permutation(s: str) -> List[int]:
    """
    Convert a string to a permutation.

    Args:
        s: String representation of the permutation

    Returns:
        The permutation as a list

    Raises:
        ValueError: If the string doesn't represent a valid permutation
    """
    try:
        perm = [int(c) for c in s]
        # Validate it's a proper permutation
        if sorted(perm) != list(range(1, len(perm) + 1)):
            raise ValueError(f"Invalid permutation string: {s}")
        return perm
    except ValueError as e:
        raise ValueError(f"Cannot parse permutation from string '{s}': {e}")

def reverse_permutation(perm: List[int]) -> List[int]:
    """
    Return the reverse of a permutation.

    Args:
        perm: The input permutation

    Returns:
        The reversed permutation
    """
    return list(reversed(perm))

def complement_permutation(perm: List[int]) -> List[int]:
    """
    Return the complement of a permutation.

    Args:
        perm: The input permutation

    Returns:
        The complement permutation
    """
    n = len(perm)
    return [n + 1 - x for x in perm]

def inverse_permutation(perm: List[int]) -> List[int]:
    """
    Return the inverse of a permutation.

    Args:
        perm: The input permutation

    Returns:
        The inverse permutation
    """
    n = len(perm)
    inverse = [0] * n
    for i, val in enumerate(perm):
        inverse[val - 1] = i + 1
    return inverse