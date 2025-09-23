"""
Utility functions for the BiSC algorithm.
"""

from .pattern_utils import flatten, contains_pattern, generate_all_permutations
from .mesh_utils import get_maximal_shading, is_pattern_contained, is_shading_consequence

__all__ = [
    'flatten',
    'contains_pattern',
    'generate_all_permutations',
    'get_maximal_shading',
    'is_pattern_contained',
    'is_shading_consequence'
]