"""
Main BiSC algorithm implementation.

This module contains the core MINE and GEN algorithms, as well as
the main BiSC algorithm that combines them.
"""

from typing import List, Set, Dict, FrozenSet, Tuple
from itertools import chain, combinations
from .permutation import Permutation
from .mesh_pattern import MeshPattern
from ..utils.pattern_utils import flatten, generate_all_permutations
from ..utils.mesh_utils import get_maximal_shading, is_pattern_contained, is_shading_consequence

def mine_algorithm(permutations: List[Permutation], max_pattern_length: int) -> Dict[Tuple[int, ...], Set[FrozenSet]]:
    """
    The MINE algorithm (Algorithm 1 from the paper).

    Finds all mesh patterns that are contained in permutations in the input.
    This is the first step of the BiSC algorithm.

    Args:
        permutations: List of input permutations
        max_pattern_length: Upper bound on pattern length to search for

    Returns:
        Dictionary mapping classical patterns to sets of maximal shadings

    Note:
        The output maps pattern tuples to sets of frozensets, where each
        frozenset represents a maximal shading for that pattern.
    """
    # Initialize S with all classical patterns of length at most max_pattern_length
    S = {}

    # Generate all classical patterns of length 1 to max_pattern_length
    def generate_patterns(length):
        if length == 0:
            return [[]]
        if length == 1:
            return [[1]]

        patterns = []
        from itertools import permutations as iter_perms
        for perm in iter_perms(range(1, length + 1)):
            patterns.append(list(perm))
        return patterns

    # Initialize with all patterns having empty shading sets
    for length in range(max_pattern_length + 1):
        for pattern in generate_patterns(length):
            pattern_tuple = tuple(pattern)
            S[pattern_tuple] = set()

    # Process each permutation
    for perm in permutations:
        # Get all subwords of length at most max_pattern_length
        subwords = perm.subwords(max_pattern_length)

        for subword, positions in subwords:
            if not subword:  # Skip empty subword
                continue

            # Flatten the subword to get the classical pattern
            pattern = flatten(subword)
            pattern_tuple = tuple(pattern)

            # Get maximal shading for this occurrence
            shading = get_maximal_shading(pattern, subword, positions, perm)
            shading_frozen = frozenset(shading)

            # Update S[pattern] with this shading if it's not redundant
            if pattern_tuple in S:
                # Check if this shading is not a subset of any existing shading
                is_redundant = any(shading_frozen.issubset(existing)
                                 for existing in S[pattern_tuple])

                if not is_redundant:
                    # Add this shading and remove any shadings that are subsets
                    S[pattern_tuple] = {existing for existing in S[pattern_tuple]
                                      if not existing.issubset(shading_frozen)}
                    S[pattern_tuple].add(shading_frozen)

    return S

def gen_algorithm(S: Dict[Tuple[int, ...], Set[FrozenSet]]) -> List[MeshPattern]:
    """
    The GEN algorithm (Algorithm 2 from the paper).

    Generates forbidden patterns from the allowed patterns found by MINE.
    This is the second step of the BiSC algorithm.

    Args:
        S: Output from MINE algorithm - patterns with their allowed shadings

    Returns:
        List of forbidden mesh patterns

    Note:
        This generates minimal forbidden shadings that are not contained
        in any allowed shading.
    """
    forbidden_patterns = []

    # Sort patterns by length for processing
    sorted_patterns = sorted(S.keys(), key=len)

    for pattern_tuple in sorted_patterns:
        pattern = list(pattern_tuple)
        allowed_shadings = S[pattern_tuple]

        if not pattern:  # Skip empty pattern
            continue

        # Generate all possible shadings for this pattern
        n = len(pattern)
        all_regions = [(i, j) for i in range(n + 1) for j in range(n + 1)]

        # Find minimal forbidden shadings
        forbidden_shadings = []

        # Check all possible shadings using powerset
        def powerset(iterable):
            """Generate the powerset of an iterable."""
            s = list(iterable)
            return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

        for shading_tuple in powerset(all_regions):
            shading = frozenset(shading_tuple)

            # Check if this shading is forbidden (not contained in any allowed shading)
            is_forbidden = True
            for allowed in allowed_shadings:
                if shading.issubset(allowed):
                    is_forbidden = False
                    break

            if is_forbidden:
                # Check if it's minimal (no proper subset is also forbidden)
                is_minimal = True
                for existing_forbidden in forbidden_shadings:
                    if existing_forbidden.issubset(shading) and existing_forbidden != shading:
                        is_minimal = False
                        break

                if is_minimal:
                    # Remove any existing forbidden shadings that are supersets
                    forbidden_shadings = [fs for fs in forbidden_shadings
                                        if not shading.issubset(fs)]
                    forbidden_shadings.append(shading)

        # Convert to MeshPattern objects and check for consequences
        for shading in forbidden_shadings:
            mesh_pattern = MeshPattern(pattern, set(shading))

            # Check if this pattern is a consequence of a shorter pattern
            is_consequence = False

            for shorter_pattern in forbidden_patterns:
                if (len(shorter_pattern.pattern) < len(pattern) and
                    is_pattern_contained(shorter_pattern.pattern, pattern)):
                    # Check if the forbidden shading is a consequence
                    if is_shading_consequence(shorter_pattern, mesh_pattern):
                        is_consequence = True
                        break

            if not is_consequence:
                forbidden_patterns.append(mesh_pattern)

    return forbidden_patterns

def bisc_algorithm(permutations: List[Permutation], max_pattern_length: int) -> List[MeshPattern]:
    """
    The full BiSC algorithm.

    Combines the MINE and GEN algorithms to discover forbidden patterns
    in a set of permutations.

    Args:
        permutations: Input set of permutations
        max_pattern_length: Upper bound on pattern length to search for

    Returns:
        List of conjectured forbidden patterns

    Examples:
        >>> # Stack-sortable permutations
        >>> stack_sortable = [Permutation([1]), Permutation([1,2]), ...]
        >>> forbidden = bisc_algorithm(stack_sortable, max_pattern_length=3)
        >>> # Should find pattern 231 as forbidden
    """
    # Step 1: MINE - find allowed patterns
    print(f"MINE: Analyzing {len(permutations)} permutations for patterns of length ≤ {max_pattern_length}")
    allowed_patterns = mine_algorithm(permutations, max_pattern_length)

    # Step 2: GEN - generate forbidden patterns
    print("GEN: Generating forbidden patterns from allowed patterns")
    forbidden_patterns = gen_algorithm(allowed_patterns)

    print(f"BiSC: Found {len(forbidden_patterns)} forbidden patterns")
    return forbidden_patterns

def bisc_with_pruning(permutations: List[Permutation], max_pattern_length: int) -> List[MeshPattern]:
    """
    BiSC algorithm with additional pruning step.

    This version includes post-processing to remove redundant patterns.

    Args:
        permutations: Input set of permutations
        max_pattern_length: Upper bound on pattern length to search for

    Returns:
        List of minimal forbidden patterns
    """
    # Run basic BiSC
    forbidden_patterns = bisc_algorithm(permutations, max_pattern_length)

    # Pruning step: remove redundant patterns
    print("PRUNE: Removing redundant patterns")
    pruned_patterns = []

    for i, pattern in enumerate(forbidden_patterns):
        is_redundant = False

        # Check if this pattern is implied by any other pattern
        for j, other_pattern in enumerate(forbidden_patterns):
            if i != j and is_shading_consequence(other_pattern, pattern):
                is_redundant = True
                break

        if not is_redundant:
            pruned_patterns.append(pattern)

    print(f"PRUNE: Reduced from {len(forbidden_patterns)} to {len(pruned_patterns)} patterns")
    return pruned_patterns

def analyze_pattern_statistics(S: Dict[Tuple[int, ...], Set[FrozenSet]]) -> Dict[str, int]:
    """
    Analyze statistics from the MINE algorithm output.

    Args:
        S: Output from MINE algorithm

    Returns:
        Dictionary with various statistics
    """
    stats = {
        'total_patterns': len(S),
        'patterns_with_occurrences': sum(1 for shadings in S.values() if shadings),
        'patterns_without_occurrences': sum(1 for shadings in S.values() if not shadings),
        'total_shadings': sum(len(shadings) for shadings in S.values()),
    }

    # Count patterns by length
    for pattern_tuple in S.keys():
        length = len(pattern_tuple)
        key = f'patterns_length_{length}'
        stats[key] = stats.get(key, 0) + 1

    return stats