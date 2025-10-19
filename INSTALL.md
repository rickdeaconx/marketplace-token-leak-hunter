# Installation Guide

## Requirements

- Python 3.11 or higher
- pip package manager
- Git (for cloning)

## Installation Methods

### Option 1: Clone from GitHub

```bash
git clone https://github.com/knostic-labs/marketplace-token-leak-hunter.git
cd marketplace-token-leak-hunter
pip install -r requirements.txt
```

### Option 2: Install as Package

```bash
# Install directly from GitHub
pip install git+https://github.com/knostic-labs/marketplace-token-leak-hunter.git

# Or install in development mode (if you cloned the repo)
cd marketplace-token-leak-hunter
pip install -e .
```

### Option 3: Install from PyPI (future)

```bash
# Once published to PyPI
pip install marketplace-token-leak-hunter
```

## Verify Installation

```bash
# Run tests
pytest tests/ -v

# Try scanning the sample repository
python -m src.scan_repo --path sample-data/repo-sample --out test.json --csv test.csv
```

## Using as GitHub Action

Add to `.github/workflows/security-scan.yml`:

```yaml
name: Token Leak Scanner

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install git+https://github.com/knostic-labs/marketplace-token-leak-hunter.git
      - run: token-leak-hunter --path . --out report.json --csv report.csv
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/knostic-labs/marketplace-token-leak-hunter.git
cd marketplace-token-leak-hunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/ --max-line-length=120
```

## Troubleshooting

**Import errors**: Make sure you've activated your virtual environment and installed dependencies.

**Permission errors**: Use `pip install --user` if you don't have system-wide pip permissions.

**Python version**: Check with `python --version`. You need 3.11+.

## Uninstall

```bash
pip uninstall marketplace-token-leak-hunter
```
