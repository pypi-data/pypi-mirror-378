# RunKMC
Tool for simulating polymerization using a Kinetic Monte Carlo algorithm.

The core simulation engine is written in C++ within a thin Python wrapper for accessibility.

## Quick install

The simplest way to install **RunKMC** is via pip:

```shell
pip install runkmc
```

## Examples

Tutorial notebooks can be found in the documentation.

## Development Guide

### Quick Setup

For new developers, run this one command after cloning:

```bash
./setup-dev.sh
```

Or using Make:

```bash
make setup
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Build the C++ components with Eigen
- Set up IDE support

### Manual Setup

If you prefer manual setup:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode (builds C++ automatically)
pip install -e .

# Optional: Set up IDE IntelliSense
cd cpp && cmake -B build -S .
```

### Requirements

- Python ≥3.8
- CMake ≥3.15 (automatically installed via pip)
- C++17 compiler
- Eigen (automatically downloaded by CMake)

## How to Cite

When using RunKMC in your project, please cite:

```
DOI for paper
```
