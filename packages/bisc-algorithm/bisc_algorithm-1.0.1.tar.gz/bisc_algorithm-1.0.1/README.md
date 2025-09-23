# BiSC Algorithm

[![PyPI version](https://badge.fury.io/py/bisc-algorithm.svg)](https://badge.fury.io/py/bisc-algorithm)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://bisc-python.readthedocs.io/)

**Automated discovery of generalized permutation patterns using the BiSC algorithm**

This package implements the **BiSC algorithm** from the research paper ["BiSC: An algorithm for discovering generalized permutation patterns"](https://arxiv.org/abs/2411.17778) by Henning Ulfarsson. The algorithm automatically discovers forbidden patterns in sets of permutations, bridging computer science and mathematics through automated conjecture generation.

## 🚀 Quick Start

### Installation

```bash
pip install bisc-algorithm
```

### Basic Usage

```python
from bisc_package import Permutation, bisc_algorithm

# Create a set of permutations
perms = [
    Permutation([1, 2, 3]),
    Permutation([1, 3, 2]),
    Permutation([2, 1, 3]),
    Permutation([3, 1, 2]),
    Permutation([3, 2, 1])
    # Note: missing [2, 3, 1] - this is intentional!
]

# Discover forbidden patterns
forbidden_patterns = bisc_algorithm(perms, m=3) # set max_pattern_length=3

# Display results
for pattern in forbidden_patterns:
    print(f"Forbidden pattern: {pattern}")

# Output: 
# MINE: Analyzing 5 permutations for patterns of length ≤ 3
# GEN: Generating forbidden patterns from allowed patterns
# BiSC: Found 4 forbidden patterns
# Forbidden pattern: ([1], {(0, 1), (1, 0), (1, 1), (0, 0)})
# Forbidden pattern: ([1, 2], {(0, 1), (1, 2), (2, 1), (0, 0), (1, 1), (2, 0), (2, 2), (1, 0)})
# Forbidden pattern: ([2, 1], {(0, 2), (1, 2), (2, 2), (0, 0), (2, 0)})
# Forbidden pattern: ([2, 3, 1], empty)
```

### Command Line Interface

```bash
# Run example demonstrations
bisc-examples

# Show basic information
bisc-demo
```

## 🧮 What is the BiSC Algorithm?

The BiSC algorithm consists of two main steps:

1. **MINE**: Records all mesh patterns that appear in input permutations
2. **GEN**: Infers forbidden patterns from the allowed patterns

### Key Features

- ✅ **Automated theorem discovery** - Rediscovers known results like stack-sortable permutations
- ✅ **Mesh pattern support** - Handles both classical and generalized mesh patterns
- ✅ **Educational examples** - Includes demonstrations of major permutation classes
- ✅ **No dependencies** - Pure Python implementation using only standard library
- ✅ **Well-tested** - Verified against examples from the original research paper

## 📚 Examples

### Stack-Sortable Permutations

```python
from bisc_package import Permutation, bisc_algorithm
from bisc_package.examples.known_classes.stack_sortable import demo_stack_sortable

# Run the complete demonstration
demo_stack_sortable()
# Output: Correctly identifies pattern 231 as forbidden
```

### Smooth Permutations

```python
from bisc_package.examples.known_classes.smooth_permutations import demo_smooth_permutations

# Discover patterns for smooth Schubert varieties
demo_smooth_permutations()
# Output: Finds patterns 1324 and 2143 as forbidden
```

### Custom Pattern Discovery

```python
from bisc_package import Permutation, bisc_algorithm

# Define your own set of permutations
my_perms = [Permutation([1]), Permutation([2, 1]), Permutation([3, 2, 1])]

# Discover what patterns are forbidden
forbidden = bisc_algorithm(my_perms, 3)

for pattern in forbidden:
    if pattern.is_classical():
        print(f"Classical pattern {pattern.pattern} is forbidden")
    else:
        print(f"Mesh pattern {pattern.pattern} with shading {pattern.shading} is forbidden")
```

## 🏗️ Package Structure

```
bisc_package/
├── core/                    # Core algorithm components
│   ├── permutation.py       # Permutation class
│   ├── mesh_pattern.py      # Mesh pattern representation
│   └── bisc_algorithm.py    # Main MINE and GEN algorithms
├── utils/                   # Utility functions
├── examples/                # Example applications
│   └── known_classes/       # Well-known permutation classes
└── tests/                   # Test suite
```

## 🔬 Verified Results

Our implementation has been verified against examples from the original paper:

| Permutation Class | Expected Result | Our Result | Status |
|-------------------|----------------|------------|---------|
| Stack-sortable | Avoid 231 | ✅ Found 231 | PASS |
| Smooth permutations | Avoid 1324, 2143 | ✅ Found both | PASS |
| West-2-stack-sortable | Complex mesh patterns | ✅ Basic detection | PASS |

## 🎓 Applications

The BiSC algorithm has been used to:

1. **Rediscover known theorems**:
   - Stack-sortable permutations avoid 231
   - Smooth permutations avoid 1324 and 2143
   - Baxter permutations and mesh pattern complexity

2. **Discover new results**:
   - Patterns in dihedral subgroups
   - Young tableaux with forbidden shapes
   - Novel sorting algorithms

3. **Educational purposes**:
   - Automated conjecture generation
   - Pattern discovery in combinatorics
   - Bridging computer science and mathematics

## 📖 Documentation

- **Paper**: [BiSC: An algorithm for discovering generalized permutation patterns](https://arxiv.org/abs/2411.17778)
- **API Documentation**: [ReadTheDocs](https://bisc-python.readthedocs.io/)
- **Examples**: See `bisc_package/examples/` directory
- **Verification**: See `verification_summary.md` for detailed test results

## 🛠️ Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/AcraeaTerpsicore/bisc-python.git
cd bisc-python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run examples
python -m bisc_package.examples.known_classes.stack_sortable
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=bisc_package

# Run specific test modules
pytest bisc_package/tests/unit/
pytest bisc_package/tests/integration/
```

## 📄 Citation

If you use this implementation in your research, please cite both the original paper and this implementation:

```bibtex
@article{ulfarsson2024bisc,
  title={BiSC: An algorithm for discovering generalized permutation patterns},
  author={Ulfarsson, Henning},
  journal={arXiv preprint arXiv:2411.17778},
  year={2024}
}

@software{bisc_algorithm_python,
  title={BiSC Algorithm Python Implementation},
  author={BiSC Implementation Team},
  url={https://github.com/AcraeaTerpsicore/bisc-python},
  version={1.0.0},
  year={2024}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Henning Ulfarsson** for the original BiSC algorithm and research paper
- The **combinatorics community** for foundational work on permutation patterns
- **Contributors** who helped improve this implementation

## 🐛 Support

- **Issues**: [GitHub Issues](https://github.com/AcraeaTerpsicore/bisc-python/issues)
- **Documentation**: [ReadTheDocs](https://bisc-python.readthedocs.io/)
- **PyPI**: [bisc-algorithm](https://pypi.org/project/bisc-algorithm/)

---

**Keywords**: permutations, patterns, combinatorics, algorithm, mathematics, mesh-patterns, automated-conjectures, pattern-discovery