# Security Policy

## Reporting Security Vulnerabilities

**Knostic Labs** takes security seriously. If you discover a security vulnerability in Marketplace Token Leak Hunter, please report it responsibly.

### Reporting Process

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues via:

1. **Email**: rickdeaconx@gmail.com
2. **GitHub Security Advisory**: Use the "Report a vulnerability" button in the Security tab
3. **GitHub**: Contact Rick Deacon directly through GitHub

### What to Include

Please include the following in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if available)
- Your contact information for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies by severity (critical issues prioritized)

### Scope

This security policy applies to:

- The Marketplace Token Leak Hunter scanner code
- GitHub Action workflow
- Detection rules and patterns
- Report generation

### Out of Scope

- Issues in third-party dependencies (report to upstream)
- Social engineering attacks
- Denial of service against public APIs

## Security Best Practices for Users

### Using the Scanner Safely

1. **Never commit real secrets** to test the scanner
2. **Use only FAKE tokens** in test data
3. **Protect GitHub tokens** used for remote scanning (use read-only scopes)
4. **Review reports** before sharing (may contain redacted but sensitive data)
5. **Rotate credentials** immediately upon detection

### GitHub Action Security

1. **Use pinned versions** of actions: `actions/checkout@v4`
2. **Limit token permissions** in workflows
3. **Store sensitive data** in GitHub Secrets
4. **Review artifacts** before making public
5. **Enable branch protection** requiring scan success

### Token Management

- **GitHub tokens**: Use fine-grained PATs with minimum scopes
- **npm tokens**: Use automation tokens with limited scope
- **CI secrets**: Never commit, always use secret management
- **Rotation schedule**: Rotate all tokens quarterly

## Known Security Considerations

### Scanner Limitations

This tool performs **static analysis only** and cannot detect:

- Runtime secrets loaded from environment
- Encrypted or encoded secrets (without decoding)
- Secrets in compiled binaries
- Tokens retrieved from external services
- Obfuscated credentials

### False Negatives

The scanner may miss:

- Custom token formats not in detection rules
- Tokens split across multiple lines
- Base64 encoded secrets (unless pattern matches after encoding)
- Credentials in unusual file types

### False Positives

The scanner may flag:

- Documentation examples with FAKE tokens (add to allowlist)
- Test fixtures with synthetic data
- Placeholder values in templates
- Environment variable references like `${{ secrets.TOKEN }}`

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Updates

Security fixes will be:

- Released as soon as possible after verification
- Documented in CHANGELOG.md
- Announced in GitHub releases
- Tagged with `security` label

## Responsible Disclosure

We follow coordinated disclosure:

1. Report received and acknowledged
2. Issue verified and assessed
3. Fix developed and tested
4. Security advisory drafted
5. Fix released
6. Public disclosure (after fix available)

We ask security researchers to:

- Allow reasonable time for fixes (90 days for non-critical)
- Not exploit vulnerabilities
- Not publicly disclose until fix is released
- Act in good faith

## Recognition

Security researchers who responsibly disclose vulnerabilities will be:

- Credited in release notes (with permission)
- Listed in security acknowledgments
- Thanked publicly (unless anonymity requested)

## Questions

For questions about this security policy:

- Open a discussion on GitHub
- Email: rickdeaconx@gmail.com
- Contact Rick Deacon via GitHub

Thank you for helping keep Marketplace Token Leak Hunter and its users secure!

---

**Copyright (c) 2025 Rick Deacon / Knostic Labs**
