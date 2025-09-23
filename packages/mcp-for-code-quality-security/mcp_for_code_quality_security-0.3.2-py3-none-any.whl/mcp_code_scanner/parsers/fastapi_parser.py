"""
FastAPI Security Scanner output parser (V1 pattern).
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_parser import BaseToolParser, ToolResult


class FastAPISecurityParser(BaseToolParser):
    """Parser for FastAPI security scanner output."""

    def __init__(self, config_path: Optional[Path] = None):
        super().__init__(config_path)
        self.tool_name = "fastapi_security"

    def parse_output(self, raw_output: str, returncode: int,
                    stderr: str = "", execution_time: float = 0.0) -> ToolResult:
        """Parse FastAPI security scanner output."""

        result = self._create_base_result(
            success=(returncode == 0),
            execution_time=execution_time
        )

        # Handle errors
        if stderr:
            result.errors.append(stderr)

        if returncode != 0 and not raw_output:
            result.errors.append(f"Tool exited with code {returncode}")
            return result

        # Parse the output
        try:
            issues = self._parse_issues(raw_output)
            result.issues = [self._enrich_issue(issue) for issue in issues]

            # Generate metadata
            result.metadata = self._extract_metadata(raw_output, issues)

            # Generate summary and suggestions (V1 pattern)
            result.summary = self._generate_summary(result.issues, result.metadata)
            result.fix_suggestions = self._generate_fix_suggestions(result.issues)
            result.confidence_score = self._calculate_confidence(result.issues, result.metadata)

            result.success = True

        except Exception as e:
            result.errors.append(f"Failed to parse output: {str(e)}")
            result.success = False

        return result

    def _parse_issues(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parse issues from raw output."""
        issues = []

        # Try to parse as JSON first (structured output)
        try:
            data = json.loads(raw_output)
            if isinstance(data, dict) and 'issues' in data:
                return data['issues']
            elif isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # Parse text output with patterns
        lines = raw_output.split('\n')
        current_issue = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Pattern: File: /path/to/file.py:line:column
            file_match = re.match(r'File:\s*(.+):(\d+):(\d+)', line)
            if file_match:
                if current_issue:
                    issues.append(current_issue)

                current_issue = {
                    'file': file_match.group(1),
                    'line': int(file_match.group(2)),
                    'column': int(file_match.group(3)),
                    'source': self.tool_name
                }
                continue

            # Pattern: Rule: rule_name (Severity: level)
            rule_match = re.match(r'Rule:\s*(\w+)\s*\(Severity:\s*(\w+)\)', line)
            if rule_match:
                current_issue.update({
                    'rule': rule_match.group(1),
                    'severity': rule_match.group(2).lower()
                })
                continue

            # Pattern: Message: description
            message_match = re.match(r'Message:\s*(.+)', line)
            if message_match:
                current_issue['message'] = message_match.group(1)
                continue

            # Pattern: Code: code snippet
            code_match = re.match(r'Code:\s*(.+)', line)
            if code_match:
                current_issue['code_snippet'] = code_match.group(1)
                continue

        # Add last issue
        if current_issue:
            issues.append(current_issue)

        return issues

    def _extract_metadata(self, raw_output: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from scan output."""
        metadata = {
            'files_scanned': 0,
            'fastapi_files_detected': 0,
            'scan_coverage': 1.0,
            'scan_errors': []
        }

        # Extract metadata from structured output
        try:
            data = json.loads(raw_output)
            if isinstance(data, dict) and 'metadata' in data:
                metadata.update(data['metadata'])
        except json.JSONDecodeError:
            pass

        # Count files from issues
        unique_files = set()
        for issue in issues:
            if 'file' in issue:
                unique_files.add(issue['file'])

        if unique_files:
            metadata['files_with_issues'] = len(unique_files)

        return metadata

    def _generate_fix_suggestions(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate FastAPI-specific fix suggestions."""
        suggestions = super()._generate_fix_suggestions(issues)

        # Add FastAPI-specific suggestions
        issue_types = set(issue.get('rule', '') for issue in issues)

        if 'sql_injection' in issue_types:
            suggestions.extend([
                "Use SQLAlchemy ORM with parameterized queries",
                "Validate and sanitize all user inputs",
                "Consider using Pydantic models for request validation"
            ])

        if 'nosql_injection' in issue_types:
            suggestions.extend([
                "Sanitize user inputs before MongoDB queries",
                "Use proper query builders instead of string concatenation",
                "Implement input validation with Pydantic"
            ])

        if 'missing_auth' in issue_types:
            suggestions.extend([
                "Add FastAPI dependencies for authentication",
                "Use OAuth2 or JWT token validation",
                "Implement proper RBAC (Role-Based Access Control)"
            ])

        if 'ssti' in issue_types:
            suggestions.extend([
                "Use Jinja2 autoescaping",
                "Avoid using user input in template strings",
                "Consider using static templates with data injection"
            ])

        if 'path_traversal' in issue_types:
            suggestions.extend([
                "Use Path parameters with proper validation",
                "Sanitize file paths before file operations",
                "Implement allowlist-based file access"
            ])

        return list(set(suggestions))  # Remove duplicates

    def _enrich_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich FastAPI security issue with additional context."""
        enriched = super()._enrich_issue(issue)

        rule = issue.get('rule', '')

        # Add FastAPI-specific context
        if rule == 'sql_injection':
            enriched['description'] = "SQL injection vulnerability detected in database query"
            enriched['impact'] = "Critical - Can lead to data breaches and unauthorized access"
            enriched['fix_priority'] = 1

        elif rule == 'nosql_injection':
            enriched['description'] = "NoSQL injection vulnerability detected"
            enriched['impact'] = "High - Can lead to data manipulation and unauthorized access"
            enriched['fix_priority'] = 1

        elif rule == 'missing_auth':
            enriched['description'] = "Endpoint lacks proper authentication"
            enriched['impact'] = "High - Unauthorized access to sensitive endpoints"
            enriched['fix_priority'] = 2

        elif rule == 'ssti':
            enriched['description'] = "Server-side template injection vulnerability"
            enriched['impact'] = "Critical - Can lead to remote code execution"
            enriched['fix_priority'] = 1

        elif rule == 'path_traversal':
            enriched['description'] = "Path traversal vulnerability in file operations"
            enriched['impact'] = "High - Can lead to unauthorized file access"
            enriched['fix_priority'] = 2

        # Add FastAPI-specific documentation links
        enriched['documentation'] = self._get_documentation_link(rule)

        return enriched

    def _get_documentation_link(self, rule: str) -> str:
        """Get relevant documentation link for the security issue."""
        docs = {
            'sql_injection': "https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-database-models",
            'nosql_injection': "https://fastapi.tiangolo.com/tutorial/nosql-databases/",
            'missing_auth': "https://fastapi.tiangolo.com/tutorial/security/",
            'ssti': "https://fastapi.tiangolo.com/advanced/templates/",
            'path_traversal': "https://fastapi.tiangolo.com/tutorial/path-params/",
            'weak_crypto': "https://fastapi.tiangolo.com/advanced/security/",
            'insecure_cors': "https://fastapi.tiangolo.com/tutorial/cors/"
        }

        return docs.get(rule, "https://fastapi.tiangolo.com/tutorial/security/")