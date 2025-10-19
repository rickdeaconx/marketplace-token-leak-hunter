"""
report.py - Report generation for scan findings.

Generates JSON and CSV output formats with structured findings.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

import json
import csv
from typing import List, Dict, Any


def generate_json_report(findings: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate JSON report of findings.

    Args:
        findings: List of finding dictionaries
        output_path: Path to write JSON file
    """
    report = {
        'scan_summary': {
            'total_findings': len(findings),
            'critical': len([f for f in findings if f['score'] >= 90]),
            'high': len([f for f in findings if 70 <= f['score'] < 90]),
            'medium': len([f for f in findings if f['score'] < 70]),
        },
        'findings': findings
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"JSON report written to {output_path}", file=None)


def generate_csv_report(findings: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate CSV report of findings.

    Args:
        findings: List of finding dictionaries
        output_path: Path to write CSV file
    """
    if not findings:
        # Write empty CSV with headers
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['path', 'line', 'rule_id', 'description', 'match', 'score', 'snippet'])
        print(f"CSV report written to {output_path}", file=None)
        return

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['path', 'line', 'rule_id', 'desc', 'match', 'score', 'snippet']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for finding in findings:
            writer.writerow(finding)

    print(f"CSV report written to {output_path}", file=None)
