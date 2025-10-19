"""
utils.py - Utility functions for scanning and token handling.

Provides token redaction, binary file detection, and remote file fetching.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

import os
import sys
from typing import List, Dict
import requests


def redact_token(token: str) -> str:
    """
    Redact token by keeping first 4 and last 4 characters.

    Only redacts if token length > 12. Otherwise returns as-is.

    Args:
        token: The token string to redact

    Returns:
        Redacted token with middle replaced by ***REDACTED***

    Examples:
        ghp_abc123xyz789 -> ghp_***REDACTED***9
        short -> short
    """
    if len(token) <= 12:
        return token

    prefix = token[:4]
    suffix = token[-4:]
    return f"{prefix}***REDACTED***{suffix}"


def is_binary_file(file_path: str) -> bool:
    """
    Quickly check if file is binary by checking for null bytes in first 4KB.

    Args:
        file_path: Path to file to check

    Returns:
        True if file appears binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(4096)
            if b'\x00' in chunk:
                return True
    except (IOError, OSError):
        return True

    return False


def fetch_repo_files(repo: str, github_token: str) -> List[Dict[str, str]]:
    """
    Fetch text files from a GitHub repository via API.

    Retrieves the default branch tree and fetches text file contents.
    Rate limits: GitHub API allows 5000 requests/hour for authenticated users.

    Args:
        repo: Repository in format 'owner/name'
        github_token: GitHub API token

    Returns:
        List of dicts with 'path' and 'content' keys

    Raises:
        SystemExit on API errors
    """
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get default branch
    print(f"Fetching repository info for {repo}...", file=sys.stderr)
    repo_url = f'https://api.github.com/repos/{repo}'
    try:
        resp = requests.get(repo_url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository info: {e}", file=sys.stderr)
        print("Check repository name, token validity, and rate limits.", file=sys.stderr)
        sys.exit(3)

    default_branch = resp.json().get('default_branch', 'main')

    # Get tree
    tree_url = f'https://api.github.com/repos/{repo}/git/trees/{default_branch}?recursive=1'
    try:
        resp = requests.get(tree_url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository tree: {e}", file=sys.stderr)
        sys.exit(3)

    tree = resp.json().get('tree', [])

    # Filter text files
    text_extensions = {'.yml', '.yaml', '.json', '.txt', '.md', '.sh', '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.env', '.npmrc', '.gitignore'}
    target_files = []

    for item in tree:
        if item['type'] != 'blob':
            continue

        path = item['path']

        # Include by extension or specific names
        _, ext = os.path.splitext(path)
        if ext.lower() in text_extensions or os.path.basename(path) in {'.npmrc', 'Dockerfile', 'package.json'}:
            target_files.append(path)

    # Fetch file contents
    files_data = []
    print(f"Fetching {len(target_files)} file(s)...", file=sys.stderr)

    for path in target_files:
        content_url = f'https://api.github.com/repos/{repo}/contents/{path}'
        try:
            resp = requests.get(content_url, headers=headers, timeout=30)
            resp.raise_for_status()

            content_data = resp.json()
            if content_data.get('encoding') == 'base64':
                import base64
                content = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                files_data.append({'path': path, 'content': content})

        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch {path}: {e}", file=sys.stderr)
            continue

    return files_data
