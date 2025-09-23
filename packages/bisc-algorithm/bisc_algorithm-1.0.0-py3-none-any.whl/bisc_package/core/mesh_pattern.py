"""
Mesh pattern class for the BiSC algorithm.

This module provides the MeshPattern class for representing
classical patterns with shaded regions.
"""

from typing import Set, Tuple, List

class MeshPattern:
    """
    Represents a mesh pattern (classical pattern + shading).

    A mesh pattern consists of:
    1. A classical pattern (permutation)
    2. A set of shaded regions that forbid elements from appearing

    Attributes:
        pattern (List[int]): The classical pattern
        shading (frozenset): Set of shaded regions (i,j)
        length (int): Length of the classical pattern
    """

    def __init__(self, pattern: List[int], shading: Set[Tuple[int, int]] = None):
        """
        Initialize a mesh pattern.

        Args:
            pattern: The classical pattern as a list
            shading: Set of shaded regions (i,j). Defaults to empty set.
        """
        self.pattern = list(pattern)
        self.shading = frozenset(shading or set())
        self.length = len(pattern)

    def __str__(self):
        """String representation of the mesh pattern."""
        if not self.shading:
            return f"({self.pattern}, empty)"
        return f"({self.pattern}, {set(self.shading)})"

    def __repr__(self):
        """Detailed string representation."""
        return f"MeshPattern({self.pattern}, {set(self.shading)})"

    def __eq__(self, other):
        """Check equality with another mesh pattern."""
        return (isinstance(other, MeshPattern) and
                self.pattern == other.pattern and
                self.shading == other.shading)

    def __hash__(self):
        """Hash function for use in sets and dictionaries."""
        return hash((tuple(self.pattern), self.shading))

    def is_classical(self) -> bool:
        """Check if this is a classical pattern (no shading)."""
        return len(self.shading) == 0

    def add_shading(self, region: Tuple[int, int]) -> 'MeshPattern':
        """
        Return a new mesh pattern with an additional shaded region.

        Args:
            region: The (i,j) region to shade

        Returns:
            New MeshPattern with the additional shading
        """
        new_shading = set(self.shading)
        new_shading.add(region)
        return MeshPattern(self.pattern, new_shading)

    def remove_shading(self, region: Tuple[int, int]) -> 'MeshPattern':
        """
        Return a new mesh pattern with a shaded region removed.

        Args:
            region: The (i,j) region to unshade

        Returns:
            New MeshPattern without the specified shading
        """
        new_shading = set(self.shading)
        new_shading.discard(region)
        return MeshPattern(self.pattern, new_shading)

    def get_all_regions(self) -> Set[Tuple[int, int]]:
        """
        Get all possible mesh regions for this pattern.

        Returns:
            Set of all possible (i,j) mesh regions
        """
        n = self.length
        return {(i, j) for i in range(n + 1) for j in range(n + 1)}

    def get_unshaded_regions(self) -> Set[Tuple[int, int]]:
        """
        Get all unshaded mesh regions.

        Returns:
            Set of unshaded (i,j) regions
        """
        return self.get_all_regions() - set(self.shading)

    def is_shading_maximal(self, allowed_shadings: Set[frozenset]) -> bool:
        """
        Check if this shading is maximal among allowed shadings.

        Args:
            allowed_shadings: Set of allowed shading patterns

        Returns:
            True if this shading is maximal
        """
        for allowed in allowed_shadings:
            if self.shading.issubset(allowed) and self.shading != allowed:
                return False
        return True

    def get_classical_pattern(self) -> List[int]:
        """Get the underlying classical pattern."""
        return list(self.pattern)

    def to_latex(self) -> str:
        """
        Generate LaTeX representation (basic version).

        Returns:
            LaTeX string representation
        """
        pattern_str = ''.join(map(str, self.pattern))
        if not self.shading:
            return f"{pattern_str}"
        shading_str = ','.join(f"({i},{j})" for i, j in sorted(self.shading))
        return f"({pattern_str}, \\{{{shading_str}\\}})"