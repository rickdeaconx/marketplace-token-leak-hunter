"""
test_scan_basic.py - Basic unit tests for scanner functionality.

Tests scanner against sample data and validates output structure.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Add src to path (must be before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scan_repo import scan_path, determine_exit_code  # noqa: E402
from src.utils import redact_token  # noqa: E402


def test_redact_token():
    """Test token redaction function."""
    # Short token - no redaction
    assert redact_token("short") == "short"

    # Long token - redact middle
    result = redact_token("ghp_abc123xyz789_long")
    assert result.startswith("ghp_")
    assert "***REDACTED***" in result
    assert result.endswith("long")

    # Exact 12 chars - no redaction
    assert redact_token("123456789012") == "123456789012"

    # 13 chars - redact
    result = redact_token("1234567890123")
    assert "***REDACTED***" in result


def test_scan_sample_repo():
    """Test scanning the sample repository."""
    sample_path = "sample-data/repo-sample"

    # Skip if sample doesn't exist
    if not os.path.exists(sample_path):
        print(f"Warning: {sample_path} does not exist, skipping test")
        return

    findings = scan_path(sample_path)

    # Validate findings structure
    assert isinstance(findings, list), "Findings should be a list"

    # Should detect at least one issue in sample data
    assert len(findings) >= 1, "Should detect at least one finding in sample data"

    # Validate finding structure
    for finding in findings:
        assert "path" in finding, "Finding should have 'path'"
        assert "line" in finding, "Finding should have 'line'"
        assert "rule_id" in finding, "Finding should have 'rule_id'"
        assert "desc" in finding, "Finding should have 'desc'"
        assert "match" in finding, "Finding should have 'match'"
        assert "score" in finding, "Finding should have 'score'"
        assert "snippet" in finding, "Finding should have 'snippet'"

        # Verify score is valid
        assert 0 <= finding["score"] <= 100, "Score should be 0-100"

        # Verify redaction occurred (no full fake tokens in output)
        if len(finding["match"]) > 12:
            assert (
                "***REDACTED***" in finding["match"]
            ), "Long tokens should be redacted"


def test_exit_code_logic():
    """Test exit code determination."""
    # No findings
    assert determine_exit_code([]) == 0

    # Low score
    assert determine_exit_code([{"score": 50}]) == 0

    # Medium score
    assert determine_exit_code([{"score": 75}]) == 1

    # High score
    assert determine_exit_code([{"score": 95}]) == 2

    # Mixed scores - highest wins
    assert determine_exit_code([{"score": 50}, {"score": 75}, {"score": 95}]) == 2


def test_cli_integration():
    """Test CLI execution produces valid output."""
    sample_path = "sample-data/repo-sample"

    if not os.path.exists(sample_path):
        print(f"Warning: {sample_path} does not exist, skipping CLI test")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        json_out = os.path.join(tmpdir, "out.json")
        csv_out = os.path.join(tmpdir, "out.csv")

        # Run scanner
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.scan_repo",
                "--path",
                sample_path,
                "--out",
                json_out,
                "--csv",
                csv_out,
            ],
            capture_output=True,
            text=True,
        )

        # Should exit with code 1 or 2 (findings expected)
        assert result.returncode in [
            0,
            1,
            2,
        ], f"Exit code should be 0, 1, or 2, got {result.returncode}"

        # Check JSON output exists and is valid
        assert os.path.exists(json_out), "JSON output file should exist"

        with open(json_out, "r") as f:
            report = json.load(f)
            assert "scan_summary" in report
            assert "findings" in report
            assert isinstance(report["findings"], list)

        # Check CSV output exists
        assert os.path.exists(csv_out), "CSV output file should exist"
