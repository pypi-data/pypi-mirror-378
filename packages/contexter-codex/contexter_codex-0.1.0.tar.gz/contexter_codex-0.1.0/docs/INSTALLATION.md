# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### From PyPI (Recommended)

```bash
pip install contexter-codex
```

### From Source

```bash
git clone https://github.com/org/contexter-dev.git
cd contexter-dev
pip install -e ".[dev]"
```

## Verification

After installation, verify that Contexter is working:

```bash
contexter --help
contexter version
```

You should see:
- CLI help output
- Version information (e.g., `contexter-codex 0.1.0`)

## Development Setup

For contributing to Contexter:

```bash
git clone https://github.com/org/contexter-dev.git
cd contexter-dev
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Troubleshooting

### Common Issues

1. **Command not found**: Make sure the virtual environment is activated or Contexter is installed globally
2. **Permission denied**: Use `pip install --user contexter-codex` for user-level installation
3. **Python version**: Ensure Python 3.8+ is installed

### Getting Help

- Check the [Usage Guide](USAGE.md)
- Open an issue on GitHub
- Check the [README](../README.md) for quick start
