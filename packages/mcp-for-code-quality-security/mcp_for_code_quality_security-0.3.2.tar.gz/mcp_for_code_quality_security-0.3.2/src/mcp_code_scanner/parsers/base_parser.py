"""
Base parser for tool output processing (V1 architectural pattern).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import yaml


@dataclass
class ToolResult:
    """Structured result from tool output parsing."""
    tool_name: str
    success: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # V1 pattern: Rich output processing
    summary: Dict[str, Any] = field(default_factory=dict)
    fix_suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'issues': self.issues,
            'errors': self.errors,
            'warnings': self.warnings,
            'execution_time': self.execution_time,
            'metadata': self.metadata,
            'summary': self.summary,
            'fix_suggestions': self.fix_suggestions,
            'confidence_score': self.confidence_score
        }


class BaseToolParser(ABC):
    """Base class for tool-specific output parsers (V1 pattern)."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.tool_name = self.config.get('name', self.__class__.__name__)

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load tool configuration from YAML (V2 pattern)."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}

    @abstractmethod
    def parse_output(self, raw_output: str, returncode: int,
                    stderr: str = "", execution_time: float = 0.0) -> ToolResult:
        """Parse tool output into structured result."""
        pass

    def _create_base_result(self, success: bool, execution_time: float = 0.0) -> ToolResult:
        """Create base tool result with common fields."""
        return ToolResult(
            tool_name=self.tool_name,
            success=success,
            execution_time=execution_time
        )

    def _extract_severity(self, issue: Dict[str, Any]) -> str:
        """Extract and normalize severity from issue."""
        severity = issue.get('severity', 'info').lower()

        # Normalize severity levels
        severity_map = {
            'error': 'high',
            'warning': 'medium',
            'info': 'low',
            'note': 'low',
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }

        return severity_map.get(severity, 'low')

    def _count_issues_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by severity level."""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for issue in issues:
            severity = self._extract_severity(issue)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return severity_counts

    def _generate_summary(self, issues: List[Dict[str, Any]],
                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics (V1 pattern)."""
        severity_counts = self._count_issues_by_severity(issues)

        return {
            'total_issues': len(issues),
            'severity_breakdown': severity_counts,
            'critical_count': severity_counts['critical'],
            'high_count': severity_counts['high'],
            'medium_count': severity_counts['medium'],
            'low_count': severity_counts['low'],
            'files_scanned': metadata.get('files_scanned', 0),
            'scan_coverage': metadata.get('scan_coverage', 0.0)
        }

    def _generate_fix_suggestions(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate fix suggestions based on issues found (V1 pattern)."""
        suggestions = []
        issue_types = set()

        for issue in issues:
            rule = issue.get('rule', '')
            severity = self._extract_severity(issue)

            if rule not in issue_types:
                issue_types.add(rule)

                # Get remediation from config or use default
                remediation = self.config.get('remediation', {}).get(rule)
                if remediation and isinstance(remediation, list):
                    suggestions.extend(remediation)
                else:
                    # Default suggestions based on rule type
                    if 'injection' in rule.lower():
                        suggestions.append("Use parameterized queries and input validation")
                    elif 'auth' in rule.lower():
                        suggestions.append("Implement proper authentication and authorization")
                    elif 'crypto' in rule.lower():
                        suggestions.append("Use strong cryptographic algorithms")

        return list(set(suggestions))  # Remove duplicates

    def _calculate_confidence(self, issues: List[Dict[str, Any]],
                            metadata: Dict[str, Any]) -> float:
        """Calculate confidence score for scan results (V1 pattern)."""
        base_confidence = 0.8

        # Adjust based on coverage
        coverage = metadata.get('scan_coverage', 1.0)
        coverage_adjustment = coverage * 0.2

        # Adjust based on file types
        files_scanned = metadata.get('files_scanned', 1)
        coverage_bonus = min(0.1, files_scanned * 0.01)

        # Penalize if too many errors
        error_penalty = max(0.0, len(metadata.get('scan_errors', [])) * 0.05)

        confidence = base_confidence + coverage_adjustment + coverage_bonus - error_penalty
        return max(0.0, min(1.0, confidence))

    def _enrich_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich issue with additional metadata."""
        enriched = issue.copy()

        # Add confidence score for individual issue
        enriched['confidence'] = issue.get('confidence', 0.8)

        # Add remediation suggestion if available
        rule = issue.get('rule', '')
        remediation = self.config.get('remediation', {}).get(rule)
        if remediation:
            if isinstance(remediation, list):
                enriched['remediation'] = remediation[0]  # First suggestion
            else:
                enriched['remediation'] = str(remediation)

        # Add OWASP mapping if available
        owasp_mappings = self.config.get('owasp_mappings', {}).get(rule)
        if owasp_mappings:
            enriched['owasp_mappings'] = owasp_mappings

        return enriched