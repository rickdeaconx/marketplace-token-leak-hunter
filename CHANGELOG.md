# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-19

### Added
- Initial release of Marketplace Token Leak Hunter
- Core scanning engine with local and remote (GitHub API) modes
- 15 detection rules covering major token types:
  - GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_ prefixes)
  - npm tokens and _authToken
  - Open VSX tokens and PATs
  - AWS and Azure credentials
  - Generic API keys and secrets
  - Private key headers
- Automatic token redaction in reports (keeps first/last 4 chars)
- Path-based risk scoring with +10 boost for sensitive locations
- Allowlist support for managing false positives
- JSON and CSV report generation
- CLI with exit codes for CI integration (0=clean, 1=medium, 2=critical)
- GitHub Action workflow for automated scanning
- Comprehensive documentation (README, OPERATIONAL_NOTES)
- Unit test suite with sample data
- Security-focused design (no external calls during scanning)
- MIT license

### Security
- All sample tokens use FAKE_ prefix
- Token redaction implemented for all outputs
- No real credentials in repository
- Defensive security tool (detection only)

## Release Notes

### v1.0.0 - Initial Release

This is the first stable release of Marketplace Token Leak Hunter, a production-ready security scanner for detecting leaked marketplace tokens, GitHub PATs, npm tokens, and other credentials in repositories.

**Key Features:**
- Detects 15+ token types with high accuracy
- Local and remote scanning modes
- Integrated GitHub Action workflow
- Comprehensive test coverage
- Conservative scoring to minimize false positives

**Requirements:**
- Python 3.11+
- requests library

**Quick Start:**
```bash
pip install -r requirements.txt
python -m src.scan_repo --path . --out report.json --csv report.csv
```

See README.md for full documentation.

---

## Version History

- **1.0.0** (2025-01-19) - Initial stable release

## Upgrade Guide

### From pre-release to 1.0.0
This is the first official release. No upgrade path needed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## Security

To report security vulnerabilities, see [SECURITY.md](SECURITY.md).

---

**Copyright (c) 2025 Rick Deacon / Knostic Labs**

[Unreleased]: https://github.com/knostic-labs/marketplace-token-leak-hunter/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/knostic-labs/marketplace-token-leak-hunter/releases/tag/v1.0.0
