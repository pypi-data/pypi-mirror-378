"""
Permutation class for the BiSC algorithm.

This module provides the core Permutation class with methods for
subword enumeration and pattern analysis.
"""

from typing import List, Tuple
from itertools import combinations

class Permutation:
    """
    Represents a permutation in one-line notation.

    A permutation is a bijection from {1, 2, ..., n} to itself.
    We represent it as a list where position i contains the value π(i).

    Attributes:
        sequence (List[int]): The permutation in one-line notation
        length (int): The length of the permutation
    """

    def __init__(self, sequence: List[int]):
        """
        Initialize a permutation.

        Args:
            sequence: List representing the permutation in one-line notation
        """
        self.sequence = list(sequence)
        self.length = len(sequence)
        self._validate()

    def _validate(self):
        """Validate that the sequence is a proper permutation."""
        if not self.sequence:
            return  # Empty permutation is valid

        sorted_seq = sorted(self.sequence)
        expected = list(range(1, len(self.sequence) + 1))
        if sorted_seq != expected:
            raise ValueError(f"Invalid permutation: {self.sequence}")

    def __str__(self):
        """String representation of the permutation."""
        return ''.join(map(str, self.sequence))

    def __repr__(self):
        """Detailed string representation."""
        return f"Permutation({self.sequence})"

    def __eq__(self, other):
        """Check equality with another permutation."""
        return isinstance(other, Permutation) and self.sequence == other.sequence

    def __hash__(self):
        """Hash function for use in sets and dictionaries."""
        return hash(tuple(self.sequence))

    def subwords(self, max_length: int) -> List[Tuple[List[int], List[int]]]:
        """
        Generate all subwords of length at most max_length.

        Args:
            max_length: Maximum length of subwords to generate

        Returns:
            List of tuples (subword, positions) where:
            - subword is the subsequence of values
            - positions is the list of indices where these values occur
        """
        subwords = []

        # Add empty subword
        subwords.append(([], []))

        # Generate all subwords of length 1 to max_length
        for length in range(1, min(max_length + 1, self.length + 1)):
            for positions in combinations(range(self.length), length):
                subword = [self.sequence[i] for i in positions]
                subwords.append((subword, list(positions)))

        return subwords

    def contains_classical_pattern(self, pattern: List[int]) -> bool:
        """
        Check if this permutation contains a classical pattern.

        Args:
            pattern: The pattern to search for

        Returns:
            True if the pattern is contained, False otherwise
        """
        from ..utils.pattern_utils import flatten

        if len(pattern) > self.length:
            return False

        for positions in combinations(range(self.length), len(pattern)):
            subword = [self.sequence[i] for i in positions]
            if flatten(subword) == pattern:
                return True
        return False

    def reverse(self) -> 'Permutation':
        """Return the reverse of this permutation."""
        return Permutation(list(reversed(self.sequence)))

    def complement(self) -> 'Permutation':
        """Return the complement of this permutation."""
        n = self.length
        return Permutation([n + 1 - x for x in self.sequence])

    def inverse(self) -> 'Permutation':
        """Return the inverse of this permutation."""
        inverse_seq = [0] * self.length
        for i, val in enumerate(self.sequence):
            inverse_seq[val - 1] = i + 1
        return Permutation(inverse_seq)