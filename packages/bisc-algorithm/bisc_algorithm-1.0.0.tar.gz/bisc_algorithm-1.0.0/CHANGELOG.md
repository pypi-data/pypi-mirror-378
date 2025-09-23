# Changelog

All notable changes to the BiSC Algorithm package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-XX

### Added
- Initial implementation of the BiSC algorithm
- Core components: Permutation, MeshPattern, BiSC algorithm
- MINE algorithm (Algorithm 1 from the paper)
- GEN algorithm (Algorithm 2 from the paper)
- Comprehensive examples for known permutation classes:
  - Stack-sortable permutations
  - Smooth permutations
  - Baxter permutations (educational example)
- Utility functions for pattern manipulation
- Command-line interface with `bisc-examples` and `bisc-demo`
- Complete test suite with unit and integration tests
- Verification against examples from the original paper
- Documentation and examples
- PyPI package structure

### Verified Results
- ✅ Stack-sortable permutations: Correctly identifies pattern 231
- ✅ Smooth permutations: Finds patterns 1324 and 2143
- ✅ West-2-stack-sortable: Basic pattern detection works
- ✅ Complex input handling: Processes non-trivial permutation sets
- ⚠️ Baxter permutations: Demonstrates mesh pattern complexity

### Performance
- Efficient for permutation sets up to ~25 elements
- Pattern enumeration scales exponentially with length
- Suitable for educational and research purposes

### Dependencies
- Pure Python implementation (no external dependencies)
- Compatible with Python 3.7+
- Optional development dependencies for testing and documentation

## [Unreleased]

### Planned Features
- Enhanced mesh pattern geometric constraint checking
- Performance optimizations for larger pattern sets
- Interactive Jupyter notebook examples
- Pattern visualization tools
- Extended pattern class support
- Web interface for algorithm demonstration

### Known Limitations
- Full mesh pattern geometry requires more sophisticated implementation
- Algorithm complexity is exponential in pattern length
- Some advanced mesh pattern features not yet implemented

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## Citation

```bibtex
@article{ulfarsson2024bisc,
  title={BiSC: An algorithm for discovering generalized permutation patterns},
  author={Ulfarsson, Henning},
  journal={arXiv preprint arXiv:2411.17778},
  year={2024}
}
```