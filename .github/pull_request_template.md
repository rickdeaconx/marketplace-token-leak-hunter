# Pull Request

## Description

**What does this PR do?**

Brief description of changes.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test coverage improvement

## Related Issues

Closes #(issue number)
Relates to #(issue number)

## Changes Made

**Detailed list of changes:**

- Change 1
- Change 2
- Change 3

## New Detection Rules (if applicable)

**If adding new token detection:**

- Rule ID: `rule_name`
- Token type: [e.g., "Azure SAS Token"]
- Score: [30-100]
- Pattern: `regex pattern`
- Test data added: Yes/No

## Testing

**How has this been tested?**

- [ ] Unit tests pass (`pytest tests/ -v`)
- [ ] Sample scan works (`python -m src.scan_repo --path sample-data/repo-sample`)
- [ ] New tests added for new functionality
- [ ] Tested on: [OS/Python version]

### Test Output

```
Paste relevant test output here
```

## Security Checklist

- [ ] No real secrets committed
- [ ] Only FAKE tokens in test data
- [ ] Code follows security best practices
- [ ] No sensitive data in logs or reports
- [ ] Token redaction working properly

## Code Quality

- [ ] Code follows style guidelines (PEP 8)
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated (README, OPERATIONAL_NOTES)
- [ ] No unnecessary dependencies added

## Breaking Changes

**Does this PR introduce breaking changes?**

- [ ] Yes (explain below)
- [ ] No

**If yes, describe the impact:**

## Screenshots (if applicable)

**Before/after or visual changes:**

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented complex code
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged

## Additional Notes

**Anything else reviewers should know:**

---

**By submitting this PR, I confirm:**
- I have the right to submit this code under the MIT license
- I agree to the project's contribution guidelines
- I have not included any real secrets or credentials

**Copyright (c) 2025 Rick Deacon / Knostic Labs**
