"""
Examples demonstrating the BiSC algorithm.

This module contains examples of using the BiSC algorithm on various
permutation classes mentioned in the paper.
"""

from .known_classes import *
from .paper_examples import *

__all__ = ['run_all_examples']

def run_all_examples():
    """Run all available examples."""
    from .known_classes.stack_sortable import demo_stack_sortable
    from .known_classes.smooth_permutations import demo_smooth_permutations
    from .paper_examples.west_2_stack import demo_west_2_stack
    from .paper_examples.difficult_case import demo_difficult_case

    print("Running all BiSC examples...")

    demo_stack_sortable()
    demo_smooth_permutations()
    demo_west_2_stack()
    demo_difficult_case()

    print("All examples completed!")