# Marketplace Token Leak Hunter

**By Rick Deacon | Knostic Labs**

[![Tests](https://github.com/rickdeaconx/marketplace-token-leak-hunter/actions/workflows/test.yml/badge.svg)](https://github.com/rickdeaconx/marketplace-token-leak-hunter/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A fast, targeted scanner specialized in detecting leaked marketplace tokens (VS Code, Open VSX, npm) in repositories and CI workflows.

## Overview

This scanner is purpose-built for the specific threat of leaked marketplace publishing tokens—credentials that extension developers use daily but that often slip through general-purpose scanners. It's designed to run fast, integrate easily into your workflow, and catch the marketplace-specific patterns that matter most for supply-chain security.

**What makes this scanner valuable:**
- **Fast & focused**: Optimized specifically for marketplace token patterns
- **Easy integration**: Drop into CI/CD in minutes, works alongside existing security tools
- **Marketplace-specific**: Catches VS Code, Open VSX, and npm publishing tokens that generic scanners may miss
- **Developer-friendly**: Clear output, low false positives, practical remediation guidance

**Your security toolkit:**
Use this scanner alongside tools like [gitleaks](https://github.com/gitleaks/gitleaks) for comprehensive coverage. While gitleaks provides broad secret detection, this tool specializes in marketplace tokens—a critical attack vector for extension supply chains. Deploy both for defense in depth.

### Why This Tool Exists

This scanner was developed in response to real-world security incidents involving IDE extensions and marketplace plugins. Developers building extensions for VS Code, Open VSX, and similar marketplaces often need to publish their work using tokens or PATs. These credentials can accidentally end up committed in:

- CI/CD workflow files (`.github/workflows/*.yml`)
- Configuration files (`.npmrc`, `package.json`)
- Documentation and example files
- Deployment scripts and Dockerfiles

When extension developers inadvertently commit their marketplace tokens, attackers can:
- Hijack legitimate extensions by publishing malicious updates
- Steal user data or inject malware into popular extensions
- Compromise the supply chain for thousands of users

This tool helps prevent these supply-chain attacks by detecting leaked tokens before they're pushed to public repositories, enabling teams to rotate credentials and secure their release pipelines proactively.

## Detection Patterns

This scanner uses targeted regex patterns for marketplace-specific tokens:

### Primary Marketplace Tokens

**GitHub Personal Access Tokens (for GitHub Marketplace/Releases):**
```regex
github_pat_[A-Za-z0-9_]{82}  # Fine-grained PAT (recommended, 93 chars total)
ghp_[A-Za-z0-9_]{36,}        # Classic PAT
gho_[A-Za-z0-9_]{36,}        # GitHub OAuth token
ghu_[A-Za-z0-9_]{36,}        # GitHub user-to-server token
ghs_[A-Za-z0-9_]{36,}        # GitHub server-to-server token
ghr_[A-Za-z0-9_]{36,}        # GitHub refresh token
```
✅ **Verified**: These are the official GitHub token formats (2025)
- **Fine-grained PATs** (`github_pat_`) became GA in March 2025 and are now the recommended format
- **Classic PATs** (`ghp_`) still in use but GitHub recommends migrating to fine-grained

**npm Publishing Tokens:**
```regex
_authToken\s*=\s*[A-Za-z0-9\-_]{20,}           # npm _authToken in .npmrc
NPM_TOKEN\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,}) # NPM_TOKEN env var
```
✅ **Verified**: Standard npm authentication format

**VS Code Marketplace / Open VSX:**
```regex
VSCE_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})       # VSCE environment variable
OVSX_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})       # Open VSX environment variable
OPENVSX_TOKEN\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})  # Open VSX token variable
OPENVSX_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})    # Open VSX PAT variable
```
⚠️ **Note**: VS Code Marketplace and Open VSX use Azure DevOps Personal Access Tokens (PATs). These tokens don't have a distinctive prefix format like GitHub tokens. This scanner detects them by looking for common environment variable names (`VSCE_PAT`, `OVSX_PAT`, etc.) with token-like values. This approach catches tokens in typical CI/CD configurations but may miss tokens stored with non-standard variable names.

**Azure DevOps PATs**: Base32-encoded 256-bit keys, typically 52+ characters. No distinctive prefix pattern.

### Also Detects

- AWS access keys (for extension distribution via S3)
- Azure client secrets (for Azure DevOps publishing)
- Generic API keys and secrets in publishing workflows
- Private key headers in CI configurations

See [src/rules.py](src/rules.py) for complete pattern definitions and scoring.

### Pattern Limitations

**What this scanner catches well:**
- GitHub tokens with official prefixes
- npm tokens in standard configurations
- Marketplace tokens in commonly-named environment variables

**What it may miss:**
- VS Code/Open VSX tokens stored with custom variable names
- Azure DevOps PATs without contextual environment variable names
- Tokens split across multiple lines or obfuscated
- Base64-encoded or encrypted tokens

For comprehensive secret detection including pattern variations, use this tool alongside [gitleaks](https://github.com/gitleaks/gitleaks).

## Features

- Focused detection for marketplace publishing tokens
- Scans CI workflows (.github/workflows), .npmrc, package.json
- Path-based risk scoring (+10 for CI files and config files)
- Token redaction in reports (keeps first/last 4 chars)
- Allowlist support for known false positives
- Exit codes for CI integration (0=clean, 1=medium, 2=critical)
- JSON and CSV report generation
- Local and remote (GitHub API) scanning modes

## Quickstart - Local Usage

### Installation

```bash
git clone https://github.com/rickdeaconx/marketplace-token-leak-hunter.git
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

### Dogfooding - Scanning This Repository

This scanner has been tested against itself to validate detection accuracy:

```bash
python -m src.scan_repo --path . --out scan.json --csv scan.csv
```

**Results:** 8 detections (all expected and safe)
- ✅ Sample test data with FAKE tokens
- ✅ Documentation examples (allowlist.txt.example, README.md)
- ✅ Placeholder strings in templates
- ✅ All findings properly redacted and scored

**Security Status:** Clean - no real secrets detected. All findings are intentional test data or documentation examples clearly marked with FAKE prefixes.

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

## Troubleshooting

### Python Version Error

**Error:** `Package 'marketplace-token-leak-hunter' requires a different Python: 3.9.6 not in '>=3.11'`

**Solution:** This tool requires Python 3.11 or higher. Check your version:
```bash
python3 --version
```

If you have an older version, you can still run the scanner directly:
```bash
# Instead of installing with pip
python3 -m src.scan_repo --path . --out report.json --csv report.csv
```

Or install Python 3.11+ from [python.org](https://www.python.org/downloads/).

### False Positives in Documentation

**Issue:** Scanner detects tokens in README files or documentation.

**Solution:** Add documentation examples to `allowlist.txt`:
```bash
# Create allowlist.txt in repository root
echo "ghp_EXAMPLE_TOKEN_FOR_DOCS" >> allowlist.txt
echo "npm_SAMPLE_TOKEN_IN_README" >> allowlist.txt
```

Or use obviously fake prefixes like `ghp_FAKE_TOKEN_...` in your documentation.

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Run from the repository root directory:
```bash
cd /path/to/marketplace-token-leak-hunter
python3 -m src.scan_repo --path . --out report.json --csv report.csv
```

### Remote Scanning Rate Limits

**Error:** `Error fetching repository tree: 403`

**Solution:** You've hit GitHub API rate limits. Check your remaining quota:
```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

Wait for the rate limit to reset or use a different token.

### Expected Findings When Scanning This Repository

When scanning the marketplace-token-leak-hunter repository itself, you'll see 8 detections. These are **all expected and safe**:

- `sample-data/repo-sample/*` - Test data with FAKE tokens
- `allowlist.txt.example` - Example allowlist entries
- `README.md` - CSV output examples
- `docs/OPERATIONAL_NOTES.md` - Documentation placeholders
- `.github/ISSUE_TEMPLATE/bug_report.md` - Example in template

This validates the scanner is working correctly. No real secrets are present.

## License

MIT License - see LICENSE file

## Security

To report a suspected token leak in a public repository, please use the [issue template](.github/ISSUE_TEMPLATE/report-leak.md).

For security issues in this tool itself, contact the maintainers directly.

## Built with Claude Code

This entire security scanner was developed using [Claude Code](https://claude.ai/code), Anthropic's AI-powered coding assistant. The tool was built with security as a first principle:

- **No real secrets**: All development used FAKE tokens with clear prefixes
- **Secure by design**: Token redaction, input validation, and safe file handling built in from the start
- **Tested thoroughly**: Self-scanned (dogfooding) to validate detection accuracy
- **Open source**: Full code transparency for security review

Claude Code enabled rapid development of a secure, functional scanner with comprehensive testing and documentation—demonstrating how AI coding tools can accelerate security tooling when used responsibly.

## Contributing

Contributions welcome. When adding new detection rules:
1. Add pattern to `src/rules.py`
2. Include test cases with fake tokens
3. Document in OPERATIONAL_NOTES.md
4. Test against sample data

---

**Note:** This tool performs static analysis only. It cannot detect:
- Tokens retrieved at runtime
- Encrypted or encoded secrets (without decoding logic)
- Secrets in compiled binaries
- Tokens stored in external systems

Always use proper secrets management and assume least privilege.
