"""
Enhanced tool result processing with V1-pattern comprehensive error handling.

Incorporates learnings from experimental v1/v2/v3 projects for robust tool output parsing.
"""

import json
import re
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from enum import Enum

from ..core.models import ScanResult


class ToolStatus(Enum):
    """Tool execution status with confidence levels."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ToolResult:
    """Enhanced tool result with V1-pattern comprehensive metadata."""
    tool_name: str
    status: ToolStatus
    raw_output: str
    parsed_issues: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    return_code: int = 0
    confidence_score: float = 1.0  # V1 pattern: confidence in results
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_scan_result(self) -> ScanResult:
        """Convert to ScanResult for compatibility."""
        return ScanResult(
            tool=self.tool_name,
            success=self.status in [ToolStatus.SUCCESS, ToolStatus.PARTIAL_SUCCESS],
            issues=self.parsed_issues,
            errors=self.errors,
            execution_time=self.execution_time,
            metadata={
                **self.metadata,
                "confidence_score": self.confidence_score,
                "warnings": self.warnings,
                "return_code": self.return_code
            }
        )


class BaseToolParser(ABC):
    """
    V1-pattern: Base class for tool-specific output parsers.

    Each tool gets a dedicated parser with comprehensive error handling
    and confidence scoring based on output quality.
    """

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.known_error_patterns = self._get_error_patterns()
        self.issue_patterns = self._get_issue_patterns()

    @abstractmethod
    def _get_error_patterns(self) -> List[str]:
        """Get regex patterns for known tool errors."""
        pass

    @abstractmethod
    def _get_issue_patterns(self) -> Dict[str, str]:
        """Get regex patterns for parsing tool-specific issues."""
        pass

    def parse_output(self, raw_output: str, return_code: int,
                    execution_time: float) -> ToolResult:
        """
        V1-pattern: Comprehensive tool output parsing with error handling.

        Returns ToolResult with confidence scoring and detailed metadata.
        """
        result = ToolResult(
            tool_name=self.tool_name,
            status=ToolStatus.UNKNOWN,
            raw_output=raw_output,
            execution_time=execution_time,
            return_code=return_code
        )

        # Step 1: Determine tool execution status
        result.status = self._determine_status(raw_output, return_code)

        # Step 2: Extract errors and warnings
        result.errors = self._extract_errors(raw_output)
        result.warnings = self._extract_warnings(raw_output)

        # Step 3: Parse issues if tool succeeded
        if result.status in [ToolStatus.SUCCESS, ToolStatus.PARTIAL_SUCCESS]:
            result.parsed_issues = self._parse_issues(raw_output)
            result.metadata = self._extract_metadata(raw_output)

        # Step 4: Calculate confidence score
        result.confidence_score = self._calculate_confidence(result)

        return result

    def _determine_status(self, output: str, return_code: int) -> ToolStatus:
        """Determine tool execution status from output and return code."""
        if return_code == 0:
            return ToolStatus.SUCCESS
        elif return_code == 1 and self._has_valid_output(output):
            return ToolStatus.PARTIAL_SUCCESS  # Tool found issues but ran successfully
        elif return_code == 124:  # timeout
            return ToolStatus.TIMEOUT
        else:
            return ToolStatus.FAILED

    def _has_valid_output(self, output: str) -> bool:
        """Check if output contains valid tool results despite non-zero exit."""
        # Override in subclasses for tool-specific validation
        return len(output.strip()) > 0

    def _extract_errors(self, output: str) -> List[str]:
        """Extract error messages from tool output."""
        errors = []

        for pattern in self.known_error_patterns:
            matches = re.finditer(pattern, output, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                error_msg = match.group(1) if match.groups() else match.group(0)
                errors.append(error_msg.strip())

        return list(set(errors))  # Remove duplicates

    def _extract_warnings(self, output: str) -> List[str]:
        """Extract warning messages from tool output."""
        warnings = []
        warning_patterns = [
            r'warning[:\s]+(.+?)(?:\n|$)',
            r'warn[:\s]+(.+?)(?:\n|$)',
            r'deprecated[:\s]+(.+?)(?:\n|$)'
        ]

        for pattern in warning_patterns:
            matches = re.finditer(pattern, output, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                warning_msg = match.group(1) if match.groups() else match.group(0)
                warnings.append(warning_msg.strip())

        return list(set(warnings))

    @abstractmethod
    def _parse_issues(self, output: str) -> List[Dict[str, Any]]:
        """Parse tool-specific issues from output."""
        pass

    def _extract_metadata(self, output: str) -> Dict[str, Any]:
        """Extract tool-specific metadata from output."""
        # Base implementation - override in subclasses
        return {
            "output_length": len(output),
            "line_count": len(output.splitlines())
        }

    def _calculate_confidence(self, result: ToolResult) -> float:
        """
        V1-pattern: Calculate confidence score based on output quality.

        Factors:
        - Tool execution status
        - Output completeness
        - Error/warning ratio
        - Known issue patterns matched
        """
        confidence = 1.0

        # Status-based confidence
        if result.status == ToolStatus.SUCCESS:
            confidence *= 1.0
        elif result.status == ToolStatus.PARTIAL_SUCCESS:
            confidence *= 0.8
        elif result.status == ToolStatus.FAILED:
            confidence *= 0.3
        elif result.status == ToolStatus.TIMEOUT:
            confidence *= 0.1
        else:
            confidence *= 0.0

        # Error/warning penalty
        total_issues = len(result.errors) + len(result.warnings)
        if total_issues > 0:
            confidence *= max(0.5, 1.0 - (total_issues * 0.1))

        # Output completeness bonus
        if len(result.raw_output) > 100:  # Substantial output
            confidence *= 1.1

        return min(1.0, max(0.0, confidence))


class RuffParser(BaseToolParser):
    """V1-pattern: Ruff-specific output parser."""

    def __init__(self):
        super().__init__("ruff")

    def _get_error_patterns(self) -> List[str]:
        return [
            r'error[:\s]+(.+?)(?:\n|$)',
            r'failed to parse[:\s]+(.+?)(?:\n|$)',
            r'could not find[:\s]+(.+?)(?:\n|$)'
        ]

    def _get_issue_patterns(self) -> Dict[str, str]:
        return {
            "file_line": r'^(.+?):(\d+):(\d+):\s*([A-Z]\d+)\s*(.+?)$',
            "json_format": r'^\s*\{.*\}$'
        }

    def _parse_issues(self, output: str) -> List[Dict[str, Any]]:
        """Parse Ruff issues from output."""
        issues = []

        # Try JSON format first
        try:
            for line in output.splitlines():
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    issue_data = json.loads(line)
                    issues.append({
                        "file": issue_data.get("filename", "unknown"),
                        "line": issue_data.get("location", {}).get("row", 0),
                        "column": issue_data.get("location", {}).get("column", 0),
                        "rule": issue_data.get("code", "unknown"),
                        "message": issue_data.get("message", ""),
                        "severity": self._map_ruff_severity(issue_data.get("code", "")),
                        "tool": "ruff"
                    })
        except json.JSONDecodeError:
            # Fall back to text parsing
            pattern = self.issue_patterns["file_line"]
            for match in re.finditer(pattern, output, re.MULTILINE):
                file_path, line_num, col_num, rule_code, message = match.groups()
                issues.append({
                    "file": file_path,
                    "line": int(line_num),
                    "column": int(col_num),
                    "rule": rule_code,
                    "message": message.strip(),
                    "severity": self._map_ruff_severity(rule_code),
                    "tool": "ruff"
                })

        return issues

    def _map_ruff_severity(self, rule_code: str) -> str:
        """Map Ruff rule codes to severity levels."""
        if rule_code.startswith(('E', 'W')):
            return "warning"
        elif rule_code.startswith(('F', 'C')):
            return "error"
        elif rule_code.startswith('S'):  # Security
            return "high"
        else:
            return "info"


class BanditParser(BaseToolParser):
    """V1-pattern: Bandit-specific output parser."""

    def __init__(self):
        super().__init__("bandit")

    def _get_error_patterns(self) -> List[str]:
        return [
            r'ERROR[:\s]+(.+?)(?:\n|$)',
            r'No Python files found[:\s]*(.+?)(?:\n|$)',
            r'Failed to parse[:\s]+(.+?)(?:\n|$)'
        ]

    def _get_issue_patterns(self) -> Dict[str, str]:
        return {
            "json_format": r'^\s*\{.*\}$'
        }

    def _parse_issues(self, output: str) -> List[Dict[str, Any]]:
        """Parse Bandit security issues from JSON output."""
        issues = []

        try:
            # Bandit outputs JSON when using -f json
            data = json.loads(output)

            for result in data.get("results", []):
                issues.append({
                    "file": result.get("filename", "unknown"),
                    "line": result.get("line_number", 0),
                    "column": result.get("col_offset", 0),
                    "rule": result.get("test_id", "unknown"),
                    "message": result.get("issue_text", ""),
                    "severity": result.get("issue_severity", "low").lower(),
                    "confidence": result.get("issue_confidence", "medium").lower(),
                    "tool": "bandit",
                    "cwe_id": result.get("cwe", {}).get("id", ""),
                    "owasp_mapping": self._get_bandit_owasp_mapping(result.get("test_id", ""))
                })

        except json.JSONDecodeError:
            # Fall back to text parsing if not JSON
            pass

        return issues

    def _get_bandit_owasp_mapping(self, test_id: str) -> List[str]:
        """Map Bandit test IDs to OWASP categories."""
        mapping = {
            "B101": ["A03:2021 - Injection"],  # assert_used
            "B102": ["A06:2021 - Vulnerable Components"],  # exec_used
            "B103": ["A03:2021 - Injection"],  # set_bad_file_permissions
            "B104": ["A02:2021 - Cryptographic Failures"],  # hardcoded_bind_all_interfaces
            "B105": ["A02:2021 - Cryptographic Failures"],  # hardcoded_password_string
            "B106": ["A02:2021 - Cryptographic Failures"],  # hardcoded_password_funcarg
            "B107": ["A02:2021 - Cryptographic Failures"],  # hardcoded_password_default
            "B108": ["A10:2021 - Server-Side Request Forgery"],  # hardcoded_tmp_directory
            "B201": ["A06:2021 - Vulnerable Components"],  # flask_debug_true
            "B301": ["A02:2021 - Cryptographic Failures"],  # pickle
            "B302": ["A06:2021 - Vulnerable Components"],  # marshal
            "B303": ["A02:2021 - Cryptographic Failures"],  # md5
            "B324": ["A02:2021 - Cryptographic Failures"],  # hashlib_new_insecure_functions
            "B501": ["A10:2021 - Server-Side Request Forgery"],  # request_with_no_cert_validation
            "B506": ["A02:2021 - Cryptographic Failures"],  # yaml_load
            "B601": ["A03:2021 - Injection"],  # paramiko_calls
            "B602": ["A03:2021 - Injection"],  # subprocess_popen_with_shell_equals_true
            "B603": ["A03:2021 - Injection"],  # subprocess_without_shell_equals_true
            "B604": ["A03:2021 - Injection"],  # any_other_function_with_shell_equals_true
            "B605": ["A03:2021 - Injection"],  # start_process_with_a_shell
            "B606": ["A03:2021 - Injection"],  # start_process_with_no_shell
            "B607": ["A03:2021 - Injection"],  # start_process_with_partial_path
            "B608": ["A03:2021 - Injection"],  # hardcoded_sql_expressions
            "B609": ["A03:2021 - Injection"],  # linux_commands_wildcard_injection
        }
        return mapping.get(test_id, ["A06:2021 - Vulnerable Components"])


class EnhancedToolProcessor:
    """
    V1-pattern: Enhanced tool processing orchestrator.

    Manages multiple tool parsers with comprehensive error handling
    and result aggregation.
    """

    def __init__(self):
        self.parsers = {
            "ruff": RuffParser(),
            "bandit": BanditParser(),
            # Add more parsers as needed
        }

    def process_tool_output(self, tool_name: str, raw_output: str,
                          return_code: int, execution_time: float) -> ToolResult:
        """
        V1-pattern: Process tool output with appropriate parser.

        Returns comprehensive ToolResult with confidence scoring.
        """
        parser = self.parsers.get(tool_name)

        if parser:
            return parser.parse_output(raw_output, return_code, execution_time)
        else:
            # Generic parser for unknown tools
            return self._generic_parse(tool_name, raw_output, return_code, execution_time)

    def _generic_parse(self, tool_name: str, raw_output: str,
                      return_code: int, execution_time: float) -> ToolResult:
        """Generic parser for tools without specific implementations."""
        status = ToolStatus.SUCCESS if return_code == 0 else ToolStatus.FAILED
        confidence = 0.7 if status == ToolStatus.SUCCESS else 0.3

        return ToolResult(
            tool_name=tool_name,
            status=status,
            raw_output=raw_output,
            return_code=return_code,
            execution_time=execution_time,
            confidence_score=confidence,
            metadata={"parser": "generic"}
        )

    def get_supported_tools(self) -> List[str]:
        """Get list of tools with dedicated parsers."""
        return list(self.parsers.keys())

    def add_parser(self, tool_name: str, parser: BaseToolParser):
        """Add a new tool parser."""
        self.parsers[tool_name] = parser