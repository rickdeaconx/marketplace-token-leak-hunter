"""
rules.py - Detection rules for marketplace tokens and credentials.

Defines regex patterns and scoring for various token types.
Includes path-based scoring boost and allowlist support.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

import re
import os
from typing import List, Dict

# Path boost configuration
HIGH_RISK_PATHS = [
    ".github/workflows",
    ".npmrc",
    "Dockerfile",
    "package.json",
    ".env",
    "/ci/",
    "/ci.",
]

PATH_BOOST = 10


def get_rules() -> List[Dict]:
    """
    Return list of detection rules.

    Each rule contains:
        - id: unique identifier
        - description: human readable description
        - pattern: compiled regex pattern
        - score: base severity score (30-100)
    """
    rules = [
        {
            "id": "gh_token_ghp",
            "description": "GitHub personal access token (ghp_ prefix)",
            "pattern": re.compile(r"ghp_[A-Za-z0-9_]{36,}"),
            "score": 95,
        },
        {
            "id": "gh_token_gho",
            "description": "GitHub OAuth token (gho_ prefix)",
            "pattern": re.compile(r"gho_[A-Za-z0-9_]{36,}"),
            "score": 95,
        },
        {
            "id": "gh_token_ghu",
            "description": "GitHub user-to-server token (ghu_ prefix)",
            "pattern": re.compile(r"ghu_[A-Za-z0-9_]{36,}"),
            "score": 95,
        },
        {
            "id": "gh_token_ghs",
            "description": "GitHub server-to-server token (ghs_ prefix)",
            "pattern": re.compile(r"ghs_[A-Za-z0-9_]{36,}"),
            "score": 95,
        },
        {
            "id": "gh_token_ghr",
            "description": "GitHub refresh token (ghr_ prefix)",
            "pattern": re.compile(r"ghr_[A-Za-z0-9_]{36,}"),
            "score": 95,
        },
        {
            "id": "npm_authtoken",
            "description": "npm _authToken in .npmrc",
            "pattern": re.compile(r"_authToken\s*=\s*[A-Za-z0-9\-_]{20,}"),
            "score": 90,
        },
        {
            "id": "npm_token_env",
            "description": "NPM_TOKEN environment variable assignment",
            "pattern": re.compile(
                r'NPM_TOKEN\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 85,
        },
        {
            "id": "vsce_pat",
            "description": "VS Code Marketplace VSCE_PAT (Azure DevOps PAT)",
            "pattern": re.compile(
                r'VSCE_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 90,
        },
        {
            "id": "ovsx_pat",
            "description": "Open VSX OVSX_PAT (Azure DevOps PAT)",
            "pattern": re.compile(
                r'OVSX_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 90,
        },
        {
            "id": "openvsx_token",
            "description": "Open VSX token reference",
            "pattern": re.compile(
                r'OPENVSX_TOKEN\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 85,
        },
        {
            "id": "openvsx_pat",
            "description": "Open VSX PAT reference",
            "pattern": re.compile(
                r'OPENVSX_PAT\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 85,
        },
        {
            "id": "github_token_generic",
            "description": "GITHUB_TOKEN with suspicious value",
            "pattern": re.compile(
                r'GITHUB_TOKEN\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?'
            ),
            "score": 70,
        },
        {
            "id": "azure_client_secret",
            "description": "Azure client secret assignment",
            "pattern": re.compile(
                r'AZURE_CLIENT_SECRET\s*[:=]\s*["\']?([A-Za-z0-9\-_~\.]{20,})["\']?'
            ),
            "score": 80,
        },
        {
            "id": "aws_secret_key",
            "description": "AWS secret access key",
            "pattern": re.compile(
                r'AWS_SECRET_ACCESS_KEY\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?'
            ),
            "score": 90,
        },
        {
            "id": "generic_api_key",
            "description": "Generic API key pattern",
            "pattern": re.compile(
                r'(?i)(api[_-]?key|apikey|access[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9\-_]{24,})["\']?'
            ),
            "score": 60,
        },
        {
            "id": "generic_secret",
            "description": "Generic secret pattern",
            "pattern": re.compile(
                r'(?i)(secret|password|passwd)\s*[:=]\s*["\']?([A-Za-z0-9\-_!@#$%^&*]{16,})["\']?'
            ),
            "score": 50,
        },
        {
            "id": "private_key_header",
            "description": "Private key BEGIN header",
            "pattern": re.compile(r"-----BEGIN [A-Z]+ PRIVATE KEY-----"),
            "score": 85,
        },
    ]

    return rules


def apply_path_boost(base_score: int, file_path: str) -> int:
    """
    Apply +10 score boost if file path matches high-risk locations.

    Args:
        base_score: Original rule score
        file_path: Relative file path

    Returns:
        Boosted score (capped at 100)
    """
    normalized_path = file_path.lower().replace("\\", "/")

    for risk_path in HIGH_RISK_PATHS:
        if risk_path in normalized_path:
            return min(base_score + PATH_BOOST, 100)

    return base_score


def check_allowlist(token: str) -> bool:
    """
    Check if token is in allowlist.

    Reads from allowlist.txt in repository root if present.
    Each line is a literal string to skip.

    Args:
        token: The matched token string

    Returns:
        True if token should be skipped (is in allowlist)
    """
    allowlist_path = "allowlist.txt"

    if not os.path.exists(allowlist_path):
        return False

    try:
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if token == line:
                        return True
    except (IOError, OSError):
        pass

    return False
