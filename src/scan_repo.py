#!/usr/bin/env python3
"""
scan_repo.py - Main entrypoint for marketplace token leak scanner.

Scans local or remote repositories for leaked tokens and credentials.
Outputs findings as JSON and CSV with redacted tokens and severity scores.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

from src.rules import get_rules, apply_path_boost, check_allowlist
from src.report import generate_json_report, generate_csv_report
from src.utils import is_binary_file, redact_token, fetch_repo_files


def scan_file(file_path: str, content: str, rules: List[Dict]) -> List[Dict[str, Any]]:
    """
    Scan a single file content against all rules.

    Args:
        file_path: Relative path of the file being scanned
        content: File content as string
        rules: List of detection rules

    Returns:
        List of findings with path, line, rule_id, desc, match, score, snippet
    """
    findings = []
    lines = content.split('\n')

    for rule in rules:
        pattern = rule['pattern']
        for line_num, line in enumerate(lines, start=1):
            matches = pattern.finditer(line)
            for match in matches:
                matched_text = match.group(0)

                # Check allowlist
                if check_allowlist(matched_text):
                    continue

                # Calculate score with path boost
                score = apply_path_boost(rule['score'], file_path)

                # Create snippet (80 char context)
                snippet = line.strip()[:80]

                finding = {
                    'path': file_path,
                    'line': line_num,
                    'rule_id': rule['id'],
                    'desc': rule['description'],
                    'match': redact_token(matched_text),
                    'score': score,
                    'snippet': snippet
                }
                findings.append(finding)

    return findings


def scan_path(root_path: str) -> List[Dict[str, Any]]:
    """
    Recursively scan a local directory for token leaks.

    Args:
        root_path: Path to scan

    Returns:
        List of all findings
    """
    rules = get_rules()
    all_findings = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip common non-code directories
        dirnames[:] = [d for d in dirnames if d not in {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_path)

            # Skip binary files
            if is_binary_file(full_path):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    findings = scan_file(rel_path, content, rules)
                    all_findings.extend(findings)
            except (IOError, OSError) as e:
                print(f"Warning: Could not read {rel_path}: {e}", file=sys.stderr)
                continue

    return all_findings


def scan_remote(repo: str, github_token: str) -> List[Dict[str, Any]]:
    """
    Scan a remote GitHub repository via API.

    Args:
        repo: Repository in format 'owner/name'
        github_token: GitHub API token for authentication

    Returns:
        List of all findings
    """
    rules = get_rules()
    all_findings = []

    print(f"Fetching files from {repo} via GitHub API...", file=sys.stderr)
    files = fetch_repo_files(repo, github_token)

    for file_info in files:
        path = file_info['path']
        content = file_info['content']

        findings = scan_file(path, content, rules)
        all_findings.extend(findings)

    return all_findings


def determine_exit_code(findings: List[Dict[str, Any]]) -> int:
    """
    Determine exit code based on finding scores.

    Returns:
        2 if any score >= 90 (high confidence)
        1 if any score >= 70 (medium confidence)
        0 otherwise
    """
    if not findings:
        return 0

    max_score = max(f['score'] for f in findings)

    if max_score >= 90:
        return 2
    elif max_score >= 70:
        return 1
    else:
        return 0


def print_summary(findings: List[Dict[str, Any]]) -> None:
    """Print concise summary to stdout."""
    if not findings:
        print("✓ No token leaks detected.")
        return

    print(f"\n⚠ Found {len(findings)} potential token leak(s):\n")

    # Group by severity
    critical = [f for f in findings if f['score'] >= 90]
    high = [f for f in findings if 70 <= f['score'] < 90]
    medium = [f for f in findings if f['score'] < 70]

    if critical:
        print(f"  CRITICAL (score >= 90): {len(critical)} finding(s)")
        for f in critical[:3]:  # Show up to 3
            print(f"    - {f['path']}:{f['line']} [{f['rule_id']}] {f['match']}")

    if high:
        print(f"  HIGH (score >= 70): {len(high)} finding(s)")
        for f in high[:3]:
            print(f"    - {f['path']}:{f['line']} [{f['rule_id']}] {f['match']}")

    if medium:
        print(f"  MEDIUM (score < 70): {len(medium)} finding(s)")

    print(f"\nSee full report in output files.\n")


def main():
    parser = argparse.ArgumentParser(
        description='Scan repositories for leaked marketplace tokens and credentials.'
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--path', help='Local repository path to scan')
    mode_group.add_argument('--repo', help='Remote repository (owner/name) to scan via GitHub API')

    parser.add_argument('--github-token', help='GitHub API token for remote mode')
    parser.add_argument('--out', default='leak-report.json', help='JSON output file')
    parser.add_argument('--csv', default='leak-report.csv', help='CSV output file')

    args = parser.parse_args()

    # Execute scan
    findings = []

    if args.path:
        if not os.path.isdir(args.path):
            print(f"Error: Path '{args.path}' does not exist or is not a directory.", file=sys.stderr)
            sys.exit(3)
        findings = scan_path(args.path)

    elif args.repo:
        if not args.github_token:
            print("Error: --github-token required for remote mode.", file=sys.stderr)
            print("GitHub token needs 'repo' or 'public_repo' read scope.", file=sys.stderr)
            sys.exit(3)
        findings = scan_remote(args.repo, args.github_token)

    # Generate reports
    generate_json_report(findings, args.out)
    generate_csv_report(findings, args.csv)

    # Print summary
    print_summary(findings)

    # Exit with appropriate code
    exit_code = determine_exit_code(findings)
    if exit_code == 2:
        print("⛔ Exiting with code 2: High confidence leak(s) detected.", file=sys.stderr)
    elif exit_code == 1:
        print("⚠ Exiting with code 1: Medium confidence leak(s) detected.", file=sys.stderr)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
