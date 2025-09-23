"""
Mesh pattern utilities for the BiSC algorithm.
"""

from typing import List, Set, Tuple
from itertools import combinations
from ..core.mesh_pattern import MeshPattern
from ..core.permutation import Permutation

def get_maximal_shading(pattern: List[int], subword: List[int], positions: List[int],
                       permutation: Permutation) -> Set[Tuple[int, int]]:
    """
    Compute the maximal shading for a pattern occurrence.

    This is a core operation in the MINE algorithm. For a given occurrence
    of a classical pattern in a permutation, we find the maximal set of
    mesh regions that can be shaded while still preserving the occurrence.

    Args:
        pattern: The flattened classical pattern
        subword: The original subword from the permutation
        positions: Positions of the subword in the permutation
        permutation: The full permutation

    Returns:
        Set of shaded regions (i,j) where i is row, j is column
    """
    if not pattern:
        return set()

    n = len(pattern)
    shading = set()

    # For each mesh region (i,j), check if it should be shaded
    for i in range(n + 1):
        for j in range(n + 1):
            # Check if this region should be shaded
            # Region (i,j) is between pattern elements i-1 and i (vertically)
            # and between pattern elements j-1 and j (horizontally)

            should_shade = True

            # Get the range of values and positions this region covers
            if i == 0:
                min_val = 0
            else:
                # Find the element with relative rank i in the pattern
                pattern_element_idx = pattern.index(i)
                min_val = subword[pattern_element_idx]

            if i == n:
                max_val = float('inf')
            else:
                # Find the element with relative rank i+1 in the pattern
                try:
                    pattern_element_idx = pattern.index(i + 1)
                    max_val = subword[pattern_element_idx]
                except ValueError:
                    max_val = float('inf')

            if j == 0:
                min_pos = -1
            else:
                # Find the position with relative rank j in the pattern
                pattern_element_idx = pattern.index(j)
                min_pos = positions[pattern_element_idx]

            if j == n:
                max_pos = len(permutation.sequence)
            else:
                # Find the position with relative rank j+1 in the pattern
                try:
                    pattern_element_idx = pattern.index(j + 1)
                    max_pos = positions[pattern_element_idx]
                except ValueError:
                    max_pos = len(permutation.sequence)

            # Check if any element of the permutation falls in this region
            for pos in range(len(permutation.sequence)):
                val = permutation.sequence[pos]

                # Skip if this position is already used in the pattern
                if pos in positions:
                    continue

                # Check if this element would fall in the mesh region
                if max_val == float('inf'):
                    val_in_range = val > min_val
                else:
                    val_in_range = min_val < val < max_val

                if max_pos == len(permutation.sequence):
                    pos_in_range = pos > min_pos
                else:
                    pos_in_range = min_pos < pos < max_pos

                if val_in_range and pos_in_range:
                    should_shade = False
                    break

            if should_shade:
                shading.add((i, j))

    return shading

def is_pattern_contained(small_pattern: List[int], large_pattern: List[int]) -> bool:
    """
    Check if small_pattern is contained in large_pattern as a classical pattern.

    Args:
        small_pattern: The pattern to search for
        large_pattern: The pattern to search in

    Returns:
        True if small_pattern is contained in large_pattern
    """
    from .pattern_utils import flatten, contains_pattern
    return contains_pattern(large_pattern, small_pattern)

def is_shading_consequence(forbidden_short: MeshPattern, candidate_long: MeshPattern) -> bool:
    """
    Check if the long pattern's forbidden shading is a consequence of the short pattern.

    This is used in the GEN algorithm to remove redundant forbidden patterns.
    A mesh pattern is redundant if any permutation containing it also contains
    a previously forbidden pattern.

    Args:
        forbidden_short: A previously identified forbidden pattern
        candidate_long: A candidate forbidden pattern to check

    Returns:
        True if candidate_long is a consequence of forbidden_short

    Note:
        This is a simplified implementation. A complete version would require
        more sophisticated analysis of mesh pattern containment relationships.
    """
    # Check if the short pattern is contained in the long pattern
    if not is_pattern_contained(forbidden_short.pattern, candidate_long.pattern):
        return False

    # For now, return False to avoid removing patterns
    # A full implementation would check if any permutation containing candidate_long
    # also contains forbidden_short with compatible shading
    return False

def mesh_pattern_contains(permutation: Permutation, mesh_pattern: MeshPattern) -> bool:
    """
    Check if a permutation contains a mesh pattern.

    This is a simplified implementation that checks classical pattern containment.
    A complete implementation would also verify mesh constraints.

    Args:
        permutation: The permutation to check
        mesh_pattern: The mesh pattern to search for

    Returns:
        True if the mesh pattern is contained

    Note:
        This implementation only checks classical pattern containment.
        Full mesh pattern checking requires geometric constraint verification.
    """
    return permutation.contains_classical_pattern(mesh_pattern.pattern)

def generate_mesh_regions(pattern_length: int) -> List[Tuple[int, int]]:
    """
    Generate all possible mesh regions for a pattern of given length.

    Args:
        pattern_length: Length of the classical pattern

    Returns:
        List of all possible (i,j) mesh regions
    """
    regions = []
    for i in range(pattern_length + 1):
        for j in range(pattern_length + 1):
            regions.append((i, j))
    return regions

def is_shading_minimal(shading: Set[Tuple[int, int]],
                      forbidden_shadings: List[Set[Tuple[int, int]]]) -> bool:
    """
    Check if a shading is minimal among forbidden shadings.

    Args:
        shading: The shading to check
        forbidden_shadings: List of existing forbidden shadings

    Returns:
        True if the shading is minimal (no proper subset is also forbidden)
    """
    shading_set = set(shading)
    for existing in forbidden_shadings:
        existing_set = set(existing)
        if existing_set.issubset(shading_set) and existing_set != shading_set:
            return False
    return True

def visualize_mesh_pattern(mesh_pattern: MeshPattern) -> str:
    """
    Create a simple text visualization of a mesh pattern.

    Args:
        mesh_pattern: The mesh pattern to visualize

    Returns:
        String representation of the pattern with shading
    """
    if mesh_pattern.length == 0:
        return "∅"

    n = mesh_pattern.length
    pattern = mesh_pattern.pattern
    shading = mesh_pattern.shading

    # Create a simple grid representation
    lines = []
    lines.append(f"Pattern: {pattern}")
    if shading:
        lines.append(f"Shaded regions: {sorted(shading)}")
    else:
        lines.append("No shading (classical pattern)")

    return "\n".join(lines)