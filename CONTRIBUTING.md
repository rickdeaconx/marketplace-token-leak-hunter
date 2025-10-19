# Contributing to Marketplace Token Leak Hunter

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and OS
- Sample repository or files that trigger the issue (with fake tokens only)
- Full error message and stack trace

Use the bug report issue template.

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear, descriptive title
- Provide detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include examples of how it would work

Use the feature request issue template.

### Reporting Token Detection Gaps

If you discover a token format that should be detected:

1. Create an issue with the token pattern (use fake examples only)
2. Explain where this token type is commonly found
3. Provide context about the risk level
4. Include sample regex pattern if possible

Never include real tokens in issues or pull requests.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip
- git

### Clone and Setup

```bash
# Fork the repository on GitHub first

# Clone your fork
git clone https://github.com/YOUR_USERNAME/marketplace-token-leak-hunter.git
cd marketplace-token-leak-hunter

# Add upstream remote
git remote add upstream https://github.com/rickdeaconx/marketplace-token-leak-hunter.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_scan_basic.py::test_redact_token -v
```

### Code Style

This project follows PEP 8 style guidelines:

```bash
# Format code with black
black src/ tests/

# Check style with flake8
flake8 src/ tests/ --max-line-length=120

# Type checking with mypy (optional but encouraged)
mypy src/ --ignore-missing-imports
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch** from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for any new functionality

4. **Update documentation** if needed (README.md, OPERATIONAL_NOTES.md)

5. **Run tests** to ensure everything passes:
   ```bash
   pytest tests/ -v
   ```

6. **Test against sample data**:
   ```bash
   python -m src.scan_repo --path sample-data/repo-sample --out test.json --csv test.csv
   ```

7. **Commit with clear messages**:
   ```bash
   git commit -m "Add detection for XYZ token type"
   ```

### Submitting Pull Request

1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template completely

4. Link any related issues

5. Wait for review and address feedback

### PR Requirements

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Code follows style guidelines
- [ ] Commit messages are clear and descriptive
- [ ] No real secrets in code or tests
- [ ] PR description explains what and why

## Adding New Detection Rules

To add a new token detection rule:

1. **Edit src/rules.py** and add to the `rules` list in `get_rules()`:

```python
{
    'id': 'unique_rule_id',
    'description': 'Human readable description',
    'pattern': re.compile(r'YOUR_REGEX_PATTERN'),
    'score': 85  # 30-100 based on confidence
},
```

2. **Add test data** to `sample-data/repo-sample/` with a FAKE token

3. **Update tests** in `tests/test_scan_basic.py` if needed

4. **Document** in docs/OPERATIONAL_NOTES.md under "Rule Structure"

5. **Test thoroughly**:
   ```bash
   pytest tests/test_scan_basic.py -v
   python -m src.scan_repo --path sample-data/repo-sample --out test.json --csv test.csv
   ```

### Scoring Guidelines

- **90-100**: Very high confidence (e.g., token with known prefix format)
- **70-89**: High confidence (e.g., token in sensitive location with strong pattern)
- **50-69**: Medium confidence (e.g., generic API key pattern)
- **30-49**: Low confidence (e.g., broad keyword matches)

## Testing Guidelines

### Test Requirements

- All new features must have tests
- Aim for >80% code coverage
- Tests must be deterministic (no randomness, no external calls)
- Use fake tokens with FAKE_ prefix
- Tests should run in <5 seconds total

### Test Structure

```python
def test_feature_name():
    """Clear description of what is being tested."""
    # Arrange
    input_data = "test input"

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
    assert 'required_field' in result
```

## Documentation Guidelines

- Keep README.md focused on quick start and common usage
- Put detailed operational info in docs/OPERATIONAL_NOTES.md
- Use clear, concise language
- Include code examples for all features
- Update CHANGELOG.md for all notable changes

## Security Guidelines

### Never Commit

- Real tokens, credentials, or secrets
- API keys or passwords
- Personal information
- Production configuration

### Always

- Use obviously fake tokens (e.g., `ghp_FAKE_TOKEN_...`)
- Redact tokens in outputs
- Test security features thoroughly
- Report vulnerabilities via SECURITY.md process
- Consider security implications of changes

## Release Process

(For maintainers)

1. Update version in relevant files
2. Update CHANGELOG.md with all changes
3. Run full test suite
4. Create release branch: `release/v1.x.x`
5. Tag release: `git tag -a v1.x.x -m "Release v1.x.x"`
6. Push tag: `git push origin v1.x.x`
7. Create GitHub release with notes
8. Update documentation if needed

## Getting Help

- Check existing documentation (README.md, OPERATIONAL_NOTES.md)
- Search existing issues
- Join discussions in GitHub Discussions
- Ask questions in issues with `question` label

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- Project documentation where applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Questions?

If you have questions about contributing, please:
1. Check this document thoroughly
2. Search existing issues
3. Create a new issue with the `question` label

Thank you for contributing to making the ecosystem more secure!
