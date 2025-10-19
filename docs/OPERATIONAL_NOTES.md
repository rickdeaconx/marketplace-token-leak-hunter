# Operational Notes

Detailed guidance for running, tuning, and integrating the Marketplace Token Leak Hunter.

## Running Locally

### Basic Scan

```bash
python -m src.scan_repo --path /path/to/repo --out results.json --csv results.csv
```

### Scan Current Directory

```bash
python -m src.scan_repo --path . --out leak-report.json --csv leak-report.csv
```

### Output Interpretation

The scanner produces two files:

1. **JSON Report** (`--out`): Structured data with scan summary and detailed findings
2. **CSV Report** (`--csv`): Tabular format for spreadsheet analysis

Both contain the same findings with redacted token values.

## Running Remote Scans via GitHub API

### Prerequisites

Create a GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `public_repo` for public repositories
   - `repo` (full) for private repositories
4. Copy the token

### Execute Remote Scan

```bash
export GITHUB_TOKEN="ghp_your_actual_token"
python -m src.scan_repo --repo owner/repository --github-token $GITHUB_TOKEN --out report.json --csv report.csv
```

### API Rate Limits

- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour

Large repositories with hundreds of files may consume 50-200 requests. Monitor rate limits:

```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

### Files Fetched in Remote Mode

The scanner fetches:
- `.yml`, `.yaml` (workflows)
- `.json`, `.txt`, `.md`
- `.npmrc`, `Dockerfile`, `package.json`
- Source code: `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.c`, `.cpp`, `.h`
- `.env`, `.sh` files

Binary files are skipped.

## Tuning Detection Rules

### Rule Structure

Rules are defined in `src/rules.py`. Each rule contains:

```python
{
    'id': 'unique_identifier',
    'description': 'Human readable description',
    'pattern': re.compile(r'regex_pattern'),
    'score': 85  # Base score 30-100
}
```

### Adding Custom Rules

Edit `src/rules.py` and add to the `rules` list in `get_rules()`:

```python
{
    'id': 'custom_api_key',
    'description': 'Custom service API key',
    'pattern': re.compile(r'CUSTOM_API_KEY\s*[:=]\s*["\']?([A-Za-z0-9]{32})["\']?'),
    'score': 80
},
```

### Adjusting Scores

Base scores:
- **90-100**: Very high confidence (e.g., GitHub token prefixes)
- **70-89**: High confidence (e.g., npm tokens, AWS secrets)
- **50-69**: Medium confidence (e.g., generic API_KEY patterns)
- **30-49**: Low confidence (e.g., broad "secret" patterns)

Path boost (+10) is automatically applied for:
- `.github/workflows/`
- `.npmrc`
- `Dockerfile`
- `package.json`
- `.env`
- `/ci/` directories

### Disabling Rules

Comment out rules in `src/rules.py` or remove from the list.

## Allowlist Management

### Creating an Allowlist

Create `allowlist.txt` in the repository root:

```txt
# Documentation examples - not real tokens
ghp_EXAMPLE_TOKEN_FOR_DOCS_ONLY
npm_SAMPLE_TOKEN_IN_README

# Test fixtures
test_fake_token_abc123xyz

# Known safe patterns
PLACEHOLDER_API_KEY
```

### Allowlist Behavior

- Exact string match only
- Lines starting with `#` are comments
- Empty lines ignored
- Case-sensitive matching

### Allowlist Strategy

**DO add to allowlist:**
- Documentation examples with clearly fake tokens
- Test fixtures with synthetic data
- Placeholder values in templates

**DO NOT add to allowlist:**
- Actual rotated tokens
- Patterns that might mask real leaks
- "Probably safe" production values

When in doubt, investigate and rotate rather than allowlist.

## Score Interpretation and Remediation

### Critical Findings (Score >= 90)

**Characteristics:**
- GitHub token with recognized prefix (ghp_, gho_, etc.)
- AWS secret access key pattern
- npm _authToken in .npmrc

**Actions:**
1. Assume compromise
2. Revoke token immediately via provider
3. Rotate credentials
4. Scan git history for token appearances
5. Check access logs for unauthorized usage
6. File security incident if needed

### High Findings (Score >= 70)

**Characteristics:**
- NPM_TOKEN, GITHUB_TOKEN with suspicious values
- Azure client secrets
- Open VSX tokens

**Actions:**
1. Verify if token is real or example
2. If real: revoke and rotate
3. If example: add to allowlist
4. Review commit history

### Medium/Low Findings (Score < 70)

**Characteristics:**
- Generic API_KEY patterns
- SECRET/PASSWORD with long values
- Broad pattern matches

**Actions:**
1. Manual review required
2. Check context (is it in test code, docs, production?)
3. If production code: treat as high finding
4. If test/doc: add to allowlist

## Remediation Workflows

### GitHub Token Leak

1. **Revoke immediately:**
   - Go to https://github.com/settings/tokens
   - Click "Delete" on the leaked token

2. **Generate new token:**
   - Create token with minimum required scopes
   - Add to GitHub Secrets (Settings → Secrets → Actions)

3. **Update CI workflows:**
   ```yaml
   env:
     GITHUB_TOKEN: ${{ secrets.MY_NEW_TOKEN }}
   ```

4. **Never commit:**
   ```yaml
   # Bad
   GITHUB_TOKEN: ghp_abc123...

   # Good
   GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

### npm Token Leak

1. **Revoke:**
   ```bash
   npm token revoke <token_id>
   ```

2. **Create new token:**
   ```bash
   npm token create --read-only  # or appropriate scope
   ```

3. **Add to CI secrets** (not .npmrc committed to git)

4. **Update .npmrc for local dev:**
   ```
   # .npmrc - DO NOT COMMIT
   //registry.npmjs.org/:_authToken=${NPM_TOKEN}
   ```

5. **Add .npmrc to .gitignore**

### Open VSX / Marketplace Token Leak

1. Revoke via marketplace provider settings
2. Generate new PAT
3. Store in GitHub Secrets
4. Use in CI via secrets only

### AWS / Azure Credential Leak

1. **AWS:**
   ```bash
   aws iam delete-access-key --access-key-id AKIA...
   ```

2. **Azure:**
   ```bash
   az ad app credential delete --id <app-id> --key-id <key-id>
   ```

3. Review CloudTrail/Azure Activity logs for unauthorized access
4. Rotate and store in secrets manager

## Integration with Security Tools

### SIEM / Log Aggregation

Parse JSON output for automated alerting:

```bash
jq '.findings[] | select(.score >= 90)' leak-report.json
```

### Slack / Email Notifications

GitHub Action example:

```yaml
- name: Notify on findings
  if: failure()
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Token leak detected in ${{ github.repository }}"}' \
      ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Pre-commit Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python -m src.scan_repo --path . --out /tmp/scan.json --csv /tmp/scan.csv
if [ $? -eq 2 ]; then
  echo "ERROR: Token leak detected. Commit blocked."
  exit 1
fi
```

## CI/CD Integration Best Practices

### GitHub Actions

- **Run on all pushes** to catch leaks immediately
- **Upload artifacts** for audit trail
- **Fail builds** on critical findings (score >= 90)
- **Allow manual override** via workflow_dispatch

### Jenkins / GitLab CI

```bash
python -m src.scan_repo --path . --out scan.json --csv scan.csv
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  echo "CRITICAL: Token leak detected"
  exit 1
elif [ $EXIT_CODE -eq 1 ]; then
  echo "WARNING: Possible token leak"
  # Allow build to continue but warn
fi
```

## Scanning Git History

Find when a token was committed:

```bash
# Search all history for a pattern
git log -S "ghp_" --all --oneline

# Show commits that touched a specific file
git log --all -- .npmrc

# Show full diff
git log -p -S "NPM_TOKEN" --all
```

If token found in history:
1. Assume it was exposed
2. Revoke and rotate
3. Consider rewriting history (use with extreme caution)

## Performance Considerations

### Local Scans

- **Large repositories**: Scan time proportional to file count
- **Typical scan**: 1000 files in ~5-15 seconds
- **Skipped directories**: `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, `build`
- **Binary files**: Skipped automatically

### Remote Scans

- **API latency**: 1-3 seconds per file fetch
- **Batch optimization**: Fetches tree first, then files
- **Recommended**: Use local scans when possible

## Troubleshooting

### "Error: --github-token required for remote mode"

Provide token:
```bash
python -m src.scan_repo --repo owner/repo --github-token $GITHUB_TOKEN --out report.json --csv report.csv
```

### "Error fetching repository tree: 404"

- Verify repository name format: `owner/repo`
- Check token has `repo` or `public_repo` scope
- Ensure repository exists and is accessible

### "Rate limit exceeded"

Wait or use a different token. Check limits:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

### Too Many False Positives

1. Review findings in CSV/JSON
2. Identify patterns (e.g., test fixtures)
3. Add to `allowlist.txt`
4. Re-run scan

### No Findings When Expected

- Verify rules in `src/rules.py` match your token formats
- Check if files are being scanned (not skipped as binary)
- Run with sample data first: `python -m src.scan_repo --path sample-data/repo-sample --out test.json --csv test.csv`

## Advanced Usage

### Scanning Specific Files Only

Modify code to accept file list, or:

```bash
# Create temporary directory with only target files
mkdir /tmp/scan-target
cp .github/workflows/*.yml /tmp/scan-target/
python -m src.scan_repo --path /tmp/scan-target --out report.json --csv report.csv
```

### Custom Output Processing

Process JSON with jq:

```bash
# Extract only critical findings
jq '.findings[] | select(.score >= 90)' leak-report.json

# Group by file
jq -r '.findings | group_by(.path) | .[] | "\(.[0].path): \(length) findings"' leak-report.json

# Export specific fields
jq -r '.findings[] | [.path, .line, .score, .match] | @csv' leak-report.json
```

## Maintenance

### Regular Updates

- Review and update rules quarterly
- Add new token patterns as platforms evolve
- Test against known leaked token formats
- Monitor false positive rates

### Rule Effectiveness Metrics

Track over time:
- Total findings per scan
- False positive rate
- Time to detect real leaks
- Rules triggering most often

Adjust scores and patterns based on effectiveness.

---

For questions or additional operational guidance, consult the README.md or file an issue.
