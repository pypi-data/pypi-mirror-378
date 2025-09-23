"""
Setup configuration for the BiSC algorithm package.
"""

from setuptools import setup, find_packages

# Read version from bisc_package/__init__.py
def get_version():
    """Get version from package init file."""
    with open('bisc_package/__init__.py', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bisc-algorithm",
    version=get_version(),
    author="BiSC Implementation Team",
    author_email="bisc-algorithm@example.com",
    description="Implementation of the BiSC pattern discovery algorithm for permutations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AcraeaTerpsicore/bisc-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    keywords="permutations patterns combinatorics algorithm mathematics pattern-discovery mesh-patterns automated-conjectures",
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        'console_scripts': [
            'bisc-examples=bisc_package.cli:run_examples',
            'bisc-demo=bisc_package.cli:run_demo',
        ],
    },
    project_urls={
        "Homepage": "https://github.com/AcraeaTerpsicore/bisc-python",
        "Documentation": "https://bisc-algorithm.readthedocs.io/",
        "Repository": "https://github.com/AcraeaTerpsicore/bisc-python",
        "Bug Reports": "https://github.com/AcraeaTerpsicore/bisc-python/issues",
        "Paper": "https://arxiv.org/abs/2411.17778",
    },
)