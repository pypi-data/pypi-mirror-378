"""
BiSC Algorithm Package

Implementation of the BiSC algorithm from "BiSC: An algorithm for discovering
generalized permutation patterns" by Henning Ulfarsson.

The BiSC algorithm automatically discovers forbidden patterns in sets of permutations,
bridging computer science and mathematics through automated conjecture generation.
"""

from .core.permutation import Permutation
from .core.mesh_pattern import MeshPattern
from .core.bisc_algorithm import bisc_algorithm, mine_algorithm, gen_algorithm

# Version information
__version__ = "1.0.0"
__author__ = "BiSC Implementation Team"
__author_email__ = "bisc-algorithm@example.com"
__description__ = "Implementation of the BiSC pattern discovery algorithm for permutations"
__license__ = "MIT"
__url__ = "https://github.com/AcraeaTerpsicore/bisc-python"

# Package metadata
__title__ = "bisc-algorithm"
__summary__ = "Automated discovery of generalized permutation patterns using the BiSC algorithm"
__keywords__ = ["permutations", "patterns", "combinatorics", "algorithm", "mathematics"]

__all__ = [
    'Permutation',
    'MeshPattern',
    'bisc_algorithm',
    'mine_algorithm',
    'gen_algorithm',
    '__version__',
]