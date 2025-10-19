---
name: Report Token Leak
about: Report a suspected token leak in a public repository
title: '[LEAK] Repository: owner/repo'
labels: 'security, token-leak'
assignees: ''
---

## Suspected Token Leak Report

**Repository:** owner/repository-name

**File Path(s):**
- path/to/file.yml:42
- path/to/other/file:13

**Token Type:**
- [ ] GitHub Personal Access Token (ghp_, gho_, etc.)
- [ ] npm token / _authToken
- [ ] Open VSX token / PAT
- [ ] AWS credentials
- [ ] Azure credentials
- [ ] Other (specify): ___________

**Severity Assessment:**
- [ ] Critical - Active token with write permissions
- [ ] High - Token present in main branch
- [ ] Medium - Token in old commits or branches
- [ ] Low - Appears to be example/test data

**Evidence:**
<!-- Provide redacted excerpts showing the leak. DO NOT paste full tokens. -->

```
Example line showing pattern (redacted):
NPM_TOKEN: npm_abc***REDACTED***xyz
```

**Discovery Method:**
- [ ] Automated scan (this tool)
- [ ] Manual code review
- [ ] External report
- [ ] Other: ___________

**Remediation Checklist:**
- [ ] Token has been revoked
- [ ] Repository owner/maintainer notified
- [ ] Commit containing token identified (SHA: _________)
- [ ] Token found in git history (not just current branch)
- [ ] Access logs reviewed for unauthorized usage
- [ ] New token generated and stored securely

**Additional Context:**
<!-- Add any other relevant information about the leak -->

**Contact Information:**
<!-- Optional: How to reach you for follow-up -->

---

**For Repository Maintainers:**

If you are the repository owner:
1. **Revoke the leaked token immediately** via your platform (GitHub, npm, etc.)
2. **Rotate credentials** and use secrets management
3. **Scan git history** for the token: `git log -S "token_prefix" --all`
4. **Review access logs** for unauthorized activity
5. **Update CI/CD** to use secrets: `${{ secrets.TOKEN_NAME }}`
6. **Consider security incident** if token had write access

**For Reporters:**

Please follow responsible disclosure:
- Do not use the leaked token
- Do not publicly share full token values
- Allow reasonable time for remediation (24-48 hours for critical)
- Contact repository owners directly for sensitive cases

Thank you for helping secure the ecosystem.
