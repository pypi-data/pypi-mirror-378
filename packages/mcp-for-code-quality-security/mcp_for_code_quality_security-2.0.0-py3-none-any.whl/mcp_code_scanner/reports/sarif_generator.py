"""
SARIF format generator for GitHub Security integration (V1 architectural pattern).
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.models import ScanReport, ScanResult
from ..compliance.owasp_mapper import ComplianceReport


class SARIFGenerator:
    """
    SARIF (Static Analysis Results Interchange Format) generator.

    Generates SARIF 2.1.0 format for integration with:
    - GitHub Security tab
    - Azure DevOps security dashboard
    - GitLab security reports
    - SARIF viewers and tools
    """

    def __init__(self):
        self.sarif_version = "2.1.0"
        self.schema_uri = "https://json.schemastore.org/sarif-2.1.0.json"

    def generate_sarif(self, scan_report: ScanReport,
                      compliance_report: Optional[ComplianceReport] = None,
                      project_name: str = "Security Scan") -> str:
        """Generate complete SARIF report."""

        sarif = {
            "version": self.sarif_version,
            "$schema": self.schema_uri,
            "runs": [self._create_run(scan_report, compliance_report, project_name)]
        }

        return json.dumps(sarif, indent=2)

    def _create_run(self, scan_report: ScanReport,
                   compliance_report: Optional[ComplianceReport],
                   project_name: str) -> Dict[str, Any]:
        """Create SARIF run object."""

        run = {
            "tool": self._create_tool_info(scan_report),
            "results": [],
            "artifacts": [],
            "invocations": [self._create_invocation(scan_report)],
            "properties": {
                "projectName": project_name,
                "scanTimestamp": scan_report.timestamp,
                "totalIssues": sum(len(r.issues) for r in scan_report.results),
                "toolsExecuted": len(scan_report.results)
            }
        }

        # Add compliance information if available
        if compliance_report:
            run["properties"]["complianceScore"] = compliance_report.compliance_score
            run["properties"]["frameworkScores"] = compliance_report.framework_scores

        # Process each scanner result
        artifacts_added = set()
        rules_added = set()

        for result in scan_report.results:
            self._process_scanner_result(result, run, artifacts_added, rules_added, compliance_report)

        return run

    def _create_tool_info(self, scan_report: ScanReport) -> Dict[str, Any]:
        """Create tool information section."""

        # Extract tool information from scan results
        scanner_tools = []
        for result in scan_report.results:
            tool_info = {
                "name": result.tool,
                "version": result.metadata.get("version", "unknown"),
                "informationUri": result.metadata.get("documentation", "")
            }
            scanner_tools.append(tool_info)

        return {
            "driver": {
                "name": "MCP Security Scanner",
                "organization": "MCP Security",
                "version": "2.0.0",
                "informationUri": "https://github.com/your-org/mcp-security-scanner",
                "shortDescription": {
                    "text": "Comprehensive security scanner for Python applications"
                },
                "fullDescription": {
                    "text": "MCP Security Scanner provides automated security analysis for Python applications with FastAPI and AI/LLM security focus."
                },
                "rules": [],
                "notifications": [],
                "properties": {
                    "scannerTools": scanner_tools,
                    "supportedFrameworks": ["FastAPI", "AI/LLM", "General Python"],
                    "complianceFrameworks": ["OWASP Top 10", "OWASP API", "OWASP LLM"]
                }
            }
        }

    def _create_invocation(self, scan_report: ScanReport) -> Dict[str, Any]:
        """Create invocation information."""

        return {
            "executionSuccessful": True,
            "startTimeUtc": scan_report.timestamp,
            "endTimeUtc": datetime.now(timezone.utc).isoformat(),
            "exitCode": 0,
            "workingDirectory": {
                "uri": str(Path.cwd())
            },
            "commandLine": f"mcp-scanner scan --config {scan_report.scan_config}",
            "properties": {
                "executionTime": scan_report.summary.get("execution_time", 0),
                "totalFileScanned": sum(r.metadata.get("files_scanned", 0) for r in scan_report.results)
            }
        }

    def _process_scanner_result(self, result: ScanResult, run: Dict[str, Any],
                               artifacts_added: set, rules_added: set,
                               compliance_report: Optional[ComplianceReport]):
        """Process individual scanner result."""

        for issue in result.issues:
            rule_id = f"{result.tool}_{issue.get('rule', 'unknown')}"

            # Add rule definition if not already added
            if rule_id not in rules_added:
                rule = self._create_rule(issue, result, compliance_report)
                run["tool"]["driver"]["rules"].append(rule)
                rules_added.add(rule_id)

            # Add artifact if not already added
            file_path = issue.get("file", "")
            if file_path and file_path not in artifacts_added:
                artifact = self._create_artifact(file_path)
                run["artifacts"].append(artifact)
                artifacts_added.add(file_path)

            # Create result entry
            sarif_result = self._create_result(issue, result, rule_id, len(run["tool"]["driver"]["rules"]) - 1)
            run["results"].append(sarif_result)

    def _create_rule(self, issue: Dict[str, Any], result: ScanResult,
                    compliance_report: Optional[ComplianceReport]) -> Dict[str, Any]:
        """Create SARIF rule definition."""

        rule_id = f"{result.tool}_{issue.get('rule', 'unknown')}"

        rule = {
            "id": rule_id,
            "name": issue.get("rule", "Unknown Rule"),
            "shortDescription": {
                "text": issue.get("message", "Security issue detected")
            },
            "fullDescription": {
                "text": issue.get("description", issue.get("message", "No description available"))
            },
            "messageStrings": {
                "default": {
                    "text": issue.get("message", "Security vulnerability detected")
                }
            },
            "defaultConfiguration": {
                "level": self._map_severity_to_level(issue.get("severity", "low"))
            },
            "properties": {
                "category": result.tool,
                "severity": issue.get("severity", "low"),
                "confidence": issue.get("confidence", 0.8),
                "tags": self._get_rule_tags(issue, result)
            }
        }

        # Add help information if available
        if issue.get("documentation"):
            rule["helpUri"] = issue["documentation"]
            rule["help"] = {
                "text": f"For more information, see: {issue['documentation']}"
            }

        # Add OWASP mapping if available
        if compliance_report:
            owasp_mappings = self._find_owasp_mappings(issue, compliance_report)
            if owasp_mappings:
                rule["properties"]["owaspMappings"] = owasp_mappings

        # Add CWE mapping if available
        if issue.get("cwe_id"):
            rule["properties"]["cwe"] = issue["cwe_id"]

        return rule

    def _create_artifact(self, file_path: str) -> Dict[str, Any]:
        """Create SARIF artifact definition."""

        return {
            "location": {
                "uri": file_path
            },
            "properties": {
                "mimeType": "text/x-python" if file_path.endswith(".py") else "text/plain"
            }
        }

    def _create_result(self, issue: Dict[str, Any], result: ScanResult,
                      rule_id: str, rule_index: int) -> Dict[str, Any]:
        """Create SARIF result entry."""

        sarif_result = {
            "ruleId": rule_id,
            "ruleIndex": rule_index,
            "message": {
                "text": issue.get("message", "Security issue detected")
            },
            "level": self._map_severity_to_level(issue.get("severity", "low")),
            "locations": [],
            "properties": {
                "tool": result.tool,
                "category": issue.get("rule", "unknown"),
                "confidence": issue.get("confidence", 0.8),
                "severity": issue.get("severity", "low")
            }
        }

        # Add location if file path is available
        file_path = issue.get("file")
        if file_path:
            location = {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": file_path
                    },
                    "region": {
                        "startLine": issue.get("line", 1),
                        "startColumn": issue.get("column", 1)
                    }
                }
            }

            # Add code snippet if available
            if issue.get("code_snippet"):
                location["physicalLocation"]["contextRegion"] = {
                    "snippet": {
                        "text": issue["code_snippet"]
                    }
                }

            sarif_result["locations"].append(location)

        # Add remediation information
        if issue.get("remediation"):
            sarif_result["fixes"] = [{
                "description": {
                    "text": issue["remediation"]
                }
            }]

        return sarif_result

    def _map_severity_to_level(self, severity: str) -> str:
        """Map security severity to SARIF level."""
        severity_map = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note"
        }
        return severity_map.get(severity.lower(), "note")

    def _get_rule_tags(self, issue: Dict[str, Any], result: ScanResult) -> List[str]:
        """Get tags for the rule."""
        tags = ["security"]

        # Add tool-specific tags
        tags.append(result.tool)

        # Add severity tag
        severity = issue.get("severity", "low")
        tags.append(f"severity-{severity}")

        # Add category-specific tags
        rule_name = issue.get("rule", "").lower()
        if "injection" in rule_name:
            tags.append("injection")
        if "auth" in rule_name:
            tags.append("authentication")
        if "xss" in rule_name:
            tags.append("xss")
        if "path" in rule_name:
            tags.append("path-traversal")
        if "ai" in rule_name or "llm" in rule_name:
            tags.append("ai-security")

        return tags

    def _find_owasp_mappings(self, issue: Dict[str, Any],
                           compliance_report: ComplianceReport) -> List[str]:
        """Find OWASP mappings for the issue."""
        mappings = []

        rule_name = issue.get("rule", "")
        for mapping in compliance_report.mappings:
            if mapping.finding_rule == rule_name:
                mappings.append(f"{mapping.owasp_id}: {mapping.owasp_title}")

        return mappings

    def generate_github_security_sarif(self, scan_report: ScanReport,
                                     compliance_report: Optional[ComplianceReport] = None,
                                     project_name: str = "Security Scan") -> str:
        """Generate SARIF specifically optimized for GitHub Security tab."""

        # Use standard SARIF generation but with GitHub-specific optimizations
        sarif_content = self.generate_sarif(scan_report, compliance_report, project_name)
        sarif_data = json.loads(sarif_content)

        # Add GitHub-specific properties
        run = sarif_data["runs"][0]
        run["properties"]["github"] = {
            "category": "security",
            "upload_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Optimize for GitHub display
        for result in run["results"]:
            # Ensure all results have proper locations for GitHub
            if not result.get("locations"):
                result["locations"] = [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "unknown"},
                        "region": {"startLine": 1}
                    }
                }]

        return json.dumps(sarif_data, indent=2)