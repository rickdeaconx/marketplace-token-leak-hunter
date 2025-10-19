# Marketplace Token Leak Hunter

**By Rick Deacon | Knostic Labs**

[![Tests](https://github.com/knostic-labs/marketplace-token-leak-hunter/actions/workflows/test.yml/badge.svg)](https://github.com/knostic-labs/marketplace-token-leak-hunter/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready security scanner that detects leaked marketplace tokens, GitHub PATs, npm tokens, and other credentials in repositories and CI configuration files.

## Overview

This tool scans local repositories or fetches files from remote GitHub repositories to identify accidentally committed secrets. It uses pattern matching with severity scoring to minimize false positives and provides actionable reports in JSON and CSV formats.

## Features

- Detects GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_ prefixes)
- Identifies npm _authToken and NPM_TOKEN credentials
- Finds Open VSX tokens and PATs
- Recognizes AWS, Azure, and generic API keys
- Scans CI workflows, .npmrc, Dockerfiles, and other high-risk files
- Path-based risk scoring with +10 boost for sensitive locations
- Token redaction in reports (keeps first/last 4 chars)
- Allowlist support for known false positives
- Exit codes for CI integration (0=clean, 1=medium, 2=critical)
- JSON and CSV report generation

## Quickstart - Local Usage

### Installation

```bash
git clone https://github.com/knostic-labs/marketplace-token-leak-hunter.git
cd marketplace-token-leak-hunter
pip install -r requirements.txt
```

### Run Scanner Locally

```bash
# Scan current directory
python -m src.scan_repo --path . --out report.json --csv report.csv

# Scan specific repository
python -m src.scan_repo --path /path/to/repo --out report.json --csv report.csv
```

### Sample Output

```
Fetching files from sample-data/repo-sample...

⚠ Found 4 potential token leak(s):

  CRITICAL (score >= 90): 2 finding(s)
    - .github/workflows/publish.yml:19 [npm_token_env] NPM_***REDACTED***REAL
    - .npmrc:4 [npm_authtoken] _aut***REDACTED***890

  HIGH (score >= 70): 2 finding(s)
    - .github/workflows/publish.yml:26 [openvsx_pat] OPEN***REDACTED***789
    - .github/workflows/publish.yml:37 [gh_token_ghp] ghp_***REDACTED***PQR

See full report in output files.

⛔ Exiting with code 2: High confidence leak(s) detected.
```

### JSON Report Example

```json
{
  "scan_summary": {
    "total_findings": 4,
    "critical": 2,
    "high": 2,
    "medium": 0
  },
  "findings": [
    {
      "path": ".github/workflows/publish.yml",
      "line": 19,
      "rule_id": "npm_token_env",
      "desc": "NPM_TOKEN environment variable assignment",
      "match": "NPM_***REDACTED***REAL",
      "score": 95,
      "snippet": "NPM_TOKEN: \"npm_FAKE_TOKEN_abc123xyz789_NOT_REAL\""
    }
  ]
}
```

## Quickstart - GitHub Action

### Installation

1. Copy `.github/workflows/leak-hunter.yml` to your repository
2. Commit and push
3. The action runs automatically on every push

### GitHub Action Configuration

Add this workflow to `.github/workflows/leak-hunter.yml`:

```yaml
name: Marketplace Token Leak Hunter

on:
  push:
    branches: ['*']
  workflow_dispatch:
    inputs:
      fail_on_high:
        description: 'Fail job on high confidence findings'
        type: boolean
        default: true

jobs:
  scan-for-leaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install requests pytest
      - run: python -m src.scan_repo --path . --out leak-report.json --csv leak-report.csv
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: leak-scan-report
          path: |
            leak-report.json
            leak-report.csv
```

Reports are uploaded as artifacts and available for 90 days.

## Remote Scanning via GitHub API

Scan public repositories without cloning:

```bash
# Create a GitHub personal access token with 'public_repo' or 'repo' scope
export GITHUB_TOKEN="your_token_here"

# Scan remote repository
python -m src.scan_repo --repo owner/repo-name --github-token $GITHUB_TOKEN --out report.json --csv report.csv
```

**Rate Limits:** GitHub API allows 5000 requests/hour for authenticated users. Large repositories may consume multiple requests.

## Handling Findings

### Immediate Actions

1. **Revoke exposed tokens immediately**
   - GitHub: Settings → Developer settings → Personal access tokens
   - npm: `npm token revoke <token>`
   - Open VSX: Account settings → Access Tokens

2. **Rotate credentials**
   - Generate new tokens/keys
   - Update CI/CD secrets using platform secret management
   - Never commit tokens to code

3. **Scan git history**
   ```bash
   # Check if token exists in history
   git log -S "ghp_" --all --oneline
   ```

4. **Consider secrets in history compromised**
   - Rotate even if removed in later commits
   - Consider using tools like `git-filter-repo` to rewrite history (use with caution)

### False Positive Management

Add known safe patterns to `allowlist.txt` (one per line):

```
npm_EXAMPLE_TOKEN_FOR_DOCS
ghp_SAMPLE_TOKEN_IN_README
```

Lines starting with `#` are ignored.

### Score Interpretation

- **90-100 (Critical)**: High confidence leak, likely real token
- **70-89 (High)**: Strong indicators, review immediately
- **50-69 (Medium)**: Possible credential, investigate
- **Below 50**: Low confidence, may be example code

## Limitations and False Positives

- **Documentation examples**: README files may contain example tokens. Add to allowlist.
- **Test fixtures**: Test data with fake tokens may trigger detection.
- **Comments**: Tokens in comments are still detected (intentional).
- **Environment variable names**: `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` has lower score.
- **Binary files**: Skipped automatically.

To reduce false positives:
1. Use secrets management (`${{ secrets.TOKEN }}` in GitHub Actions)
2. Add test fixtures to allowlist
3. Use obviously fake prefixes in documentation (`ghp_EXAMPLE_...`)

## CSV Report Format

```csv
path,line,rule_id,desc,match,score,snippet
.npmrc,4,npm_authtoken,npm _authToken in .npmrc,_aut***REDACTED***890,100,"_authToken=npm_FAKE_AUTHTOKEN_abcdefghij1234567890"
```

## Testing

Run unit tests:

```bash
pytest -v tests/
```

Test against sample data:

```bash
python -m src.scan_repo --path sample-data/repo-sample --out test-out.json --csv test-out.csv
```

## Operational Guidance

See [docs/OPERATIONAL_NOTES.md](docs/OPERATIONAL_NOTES.md) for:
- Detailed usage instructions
- Rule tuning and customization
- Allowlist management
- Remediation workflows
- Integration with security tools

## Exit Codes

- **0**: No significant findings (clean or low severity only)
- **1**: Medium confidence findings (score >= 70)
- **2**: High confidence findings (score >= 90)
- **3**: Execution error (invalid arguments, API failure, etc.)

## Requirements

- Python 3.11+
- `requests` library (for remote scanning)
- `pytest` (for testing)

## License

MIT License - see LICENSE file

## Security

To report a suspected token leak in a public repository, please use the [issue template](.github/ISSUE_TEMPLATE/report-leak.md).

For security issues in this tool itself, contact the maintainers directly.

## Contributing

Contributions welcome. When adding new detection rules:
1. Add pattern to `src/rules.py`
2. Include test cases with fake tokens
3. Document in OPERATIONAL_NOTES.md
4. Test against sample data

---

**Warning:** This tool performs static analysis only. It cannot detect:
- Tokens retrieved at runtime
- Encrypted or encoded secrets (without decoding logic)
- Secrets in compiled binaries
- Tokens stored in external systems

Always use proper secrets management and assume least privilege.
