"""
Enterprise-grade report generator with professional formatting and CI/CD integration.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..core.models import ScanReport, ScanResult
from ..compliance.owasp_mapper import ComplianceReport, OWASPMapper


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    include_executive_summary: bool = True
    include_compliance_mapping: bool = True
    include_remediation_guide: bool = True
    include_cicd_examples: bool = True
    include_metrics_dashboard: bool = True
    logo_url: Optional[str] = None
    company_name: str = "Your Organization"
    report_template: str = "enterprise"


class EnterpriseReportGenerator:
    """
    Enterprise-grade report generator following V1 architectural pattern.

    Generates comprehensive reports suitable for:
    - Executive summaries for C-level stakeholders
    - Technical reports for development teams
    - Compliance reports for auditors
    - CI/CD integration examples
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.owasp_mapper = OWASPMapper()

    def generate_executive_report(self, scan_report: ScanReport,
                                compliance_report: ComplianceReport,
                                project_name: str = "Security Scan") -> str:
        """Generate executive summary report for C-level stakeholders."""

        risk_level = self._calculate_risk_level(compliance_report.compliance_score)

        report = f"""# 🏢 Executive Security Report

## {self.config.company_name} - Security Assessment

**Project:** {project_name}
**Scan Date:** {datetime.now().strftime('%B %d, %Y')}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
**Overall Risk Level:** {risk_level['emoji']} **{risk_level['level']}**

---

## 📊 Executive Summary

{compliance_report.executive_summary}

### Key Metrics
- **Overall Security Score:** {compliance_report.compliance_score:.1f}%
- **Total Security Findings:** {compliance_report.total_findings}
- **Critical/High Priority Issues:** {sum(1 for m in compliance_report.mappings if m.remediation_priority <= 2)}
- **Files Scanned:** {sum(r.metadata.get('files_scanned', 0) for r in scan_report.results)}
- **Scan Duration:** {scan_report.summary.get('execution_time', 0):.1f} seconds

### Compliance Framework Scores
"""

        for framework, score in compliance_report.framework_scores.items():
            status_emoji = "✅" if score >= 90 else "⚠️" if score >= 70 else "🚨"
            framework_name = framework.replace('_', ' ').title()
            report += f"- **{framework_name}:** {score:.1f}% {status_emoji}\n"

        report += f"""

---

## 🎯 Strategic Recommendations

### Immediate Actions Required
"""

        priority_actions = [rec for rec in compliance_report.recommendations if "CRITICAL" in rec]
        for i, action in enumerate(priority_actions[:3], 1):
            report += f"{i}. {action}\n"

        report += f"""

### Risk Mitigation Timeline
- **Week 1:** Address all critical and high priority security vulnerabilities
- **Week 2-4:** Implement authentication and access controls
- **Month 2:** Establish ongoing security monitoring and compliance
- **Month 3:** Security training and process improvements

### Business Impact
- **Security Posture:** {risk_level['business_impact']}
- **Compliance Status:** {'Compliant' if compliance_report.compliance_score >= 80 else 'Non-Compliant'}
- **Regulatory Risk:** {'Low' if compliance_report.compliance_score >= 90 else 'Medium' if compliance_report.compliance_score >= 70 else 'High'}

---

## 📈 Investment Recommendations

### Immediate Investment Priorities
1. **Security Team Expansion** - Dedicated security engineers
2. **Automated Security Tools** - SAST/DAST integration in CI/CD
3. **Security Training** - Developer security awareness programs
4. **Compliance Auditing** - Regular third-party security assessments

### ROI Expectations
- **Risk Reduction:** {100 - compliance_report.compliance_score:.0f}% improvement potential
- **Compliance Cost Avoidance:** Estimated $50K-$500K in potential fines
- **Brand Protection:** Maintain customer trust and market reputation

---

**Report prepared by:** MCP Security Scanner v2.0
**Next Review Date:** Next Month

*This report contains confidential security information and should be handled according to your organization's data classification policies.*
"""

        return report

    def generate_technical_report(self, scan_report: ScanReport,
                                compliance_report: ComplianceReport,
                                project_name: str = "Security Scan") -> str:
        """Generate detailed technical report for development teams."""

        report = f"""# 🔧 Technical Security Report

## Project: {project_name}

**Scan Timestamp:** {scan_report.timestamp}
**Configuration:** {scan_report.scan_config}
**Tools Executed:** {len(scan_report.results)}

---

## 🔍 Scan Overview

### Tool Execution Summary
| Tool | Status | Issues Found | Execution Time |
|------|--------|--------------|----------------|
"""

        for result in scan_report.results:
            status_emoji = "✅" if result.success else "❌"
            report += f"| {result.tool} | {status_emoji} | {len(result.issues)} | {result.execution_time:.2f}s |\n"

        report += f"""

### Issue Distribution by Severity
"""
        severity_counts = self._count_issues_by_severity(scan_report)
        for severity, count in severity_counts.items():
            emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}.get(severity, "📝")
            report += f"- **{severity.title()}:** {count} issues {emoji}\n"

        report += f"""

---

## 🛡️ Security Findings by Category

"""
        # Group issues by tool/category
        for result in scan_report.results:
            if not result.issues:
                continue

            report += f"""
### {result.tool.replace('_', ' ').title()}

**Status:** {'✅ Passed' if result.success else '❌ Failed'}
**Issues Found:** {len(result.issues)}
**Tool Version:** {result.metadata.get('version', 'Unknown')}

"""
            # Show top 5 issues for each tool
            for i, issue in enumerate(result.issues[:5], 1):
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}.get(
                    issue.get('severity', 'low'), "📝"
                )

                report += f"""
#### {i}. {issue.get('rule', 'Unknown Rule')} {severity_emoji}

**File:** `{issue.get('file', 'Unknown')}`
**Line:** {issue.get('line', 'N/A')}
**Severity:** {issue.get('severity', 'Unknown').title()}
**Message:** {issue.get('message', 'No description available')}

"""
                if issue.get('code_snippet'):
                    report += f"**Code:**\n```python\n{issue['code_snippet']}\n```\n"

                if issue.get('remediation'):
                    report += f"**Fix:** {issue['remediation']}\n"

            if len(result.issues) > 5:
                report += f"\n*... and {len(result.issues) - 5} more issues*\n"

        report += f"""

---

## 🏛️ OWASP Compliance Analysis

### Framework Compliance Scores
"""

        for framework, score in compliance_report.framework_scores.items():
            status = "✅ Compliant" if score >= 90 else "⚠️ Needs Improvement" if score >= 70 else "🚨 Non-Compliant"
            framework_name = framework.replace('_', ' ').title()
            report += f"- **{framework_name}:** {score:.1f}% - {status}\n"

        report += f"""

### Detailed OWASP Mappings
"""

        # Group mappings by framework
        framework_mappings = {}
        for mapping in compliance_report.mappings:
            fw = mapping.framework.value
            if fw not in framework_mappings:
                framework_mappings[fw] = []
            framework_mappings[fw].append(mapping)

        for framework, mappings in framework_mappings.items():
            framework_name = framework.replace('_', ' ').title()
            report += f"""
#### {framework_name}

| OWASP ID | Title | Rule | Priority | Status |
|----------|-------|------|----------|--------|
"""
            for mapping in sorted(mappings, key=lambda x: x.remediation_priority):
                status_emoji = "❌" if mapping.compliance_status == "non_compliant" else "⚠️" if mapping.compliance_status == "partial" else "✅"
                priority_emoji = "🚨" if mapping.remediation_priority <= 2 else "⚠️" if mapping.remediation_priority == 3 else "📝"

                report += f"| {mapping.owasp_id} | {mapping.owasp_title} | `{mapping.finding_rule}` | {mapping.remediation_priority}/5 {priority_emoji} | {status_emoji} |\n"

        report += f"""

---

## 🔧 Remediation Guide

### Priority-Based Action Plan
"""

        # Group issues by priority
        priority_groups = {}
        for mapping in compliance_report.mappings:
            priority = mapping.remediation_priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(mapping)

        for priority in sorted(priority_groups.keys()):
            mappings = priority_groups[priority]
            priority_name = {1: "🚨 Critical", 2: "⚠️ High", 3: "📋 Medium", 4: "📝 Low", 5: "ℹ️ Info"}[priority]

            report += f"""
### {priority_name} Priority (Fix within {'1 day' if priority <= 2 else '1 week' if priority == 3 else '1 month'})

"""
            for mapping in mappings:
                report += f"- **{mapping.owasp_id}:** {mapping.owasp_title} (`{mapping.finding_rule}`)\n"

        report += f"""

### Fix Suggestions
"""
        for i, suggestion in enumerate(compliance_report.recommendations, 1):
            report += f"{i}. {suggestion}\n"

        report += f"""

---

## 📊 Metrics and Trends

### Scan Performance
- **Total Scan Time:** {scan_report.summary.get('execution_time', 0):.1f} seconds
- **Files Processed:** {sum(r.metadata.get('files_scanned', 0) for r in scan_report.results)}
- **Average Issues per File:** {compliance_report.total_findings / max(1, sum(r.metadata.get('files_scanned', 0) for r in scan_report.results)):.1f}

### Tool Effectiveness
"""

        for result in scan_report.results:
            if result.success:
                effectiveness = len(result.issues) / max(1, result.execution_time)
                report += f"- **{result.tool}:** {effectiveness:.1f} issues/second\n"

        report += f"""

---

*Report generated by MCP Security Scanner - Enterprise Edition*
*For support and questions, contact your security team*
"""

        return report

    def generate_sarif_report(self, scan_report: ScanReport,
                            project_name: str = "Security Scan") -> str:
        """Generate SARIF format for GitHub Security tab integration."""

        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "MCP Security Scanner",
                        "organization": "MCP Security",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/your-org/mcp-security-scanner",
                        "rules": []
                    }
                },
                "results": [],
                "artifacts": [],
                "invocations": [{
                    "executionSuccessful": True,
                    "startTimeUtc": scan_report.timestamp,
                    "endTimeUtc": datetime.now(timezone.utc).isoformat()
                }]
            }]
        }

        run = sarif["runs"][0]
        rules_added = set()
        artifacts_added = set()

        # Process results from each tool
        for result in scan_report.results:
            for issue in result.issues:
                rule_id = f"{result.tool}_{issue.get('rule', 'unknown')}"

                # Add rule definition if not already added
                if rule_id not in rules_added:
                    rule = {
                        "id": rule_id,
                        "name": issue.get('rule', 'Unknown Rule'),
                        "shortDescription": {
                            "text": issue.get('message', 'No description available')
                        },
                        "fullDescription": {
                            "text": issue.get('description', issue.get('message', 'No description available'))
                        },
                        "helpUri": issue.get('documentation', ''),
                        "properties": {
                            "category": result.tool,
                            "severity": issue.get('severity', 'low'),
                            "precision": "high"
                        }
                    }

                    # Add OWASP mapping if available
                    if issue.get('owasp_mapping'):
                        rule["properties"]["owasp"] = issue['owasp_mapping']

                    run["tool"]["driver"]["rules"].append(rule)
                    rules_added.add(rule_id)

                # Add artifact if not already added
                file_path = issue.get('file', '')
                if file_path and file_path not in artifacts_added:
                    run["artifacts"].append({
                        "location": {
                            "uri": file_path
                        }
                    })
                    artifacts_added.add(file_path)

                # Add result
                sarif_result = {
                    "ruleId": rule_id,
                    "ruleIndex": len([r for r in run["tool"]["driver"]["rules"] if r["id"] == rule_id]) - 1,
                    "message": {
                        "text": issue.get('message', 'Security issue detected')
                    },
                    "level": self._sarif_severity_level(issue.get('severity', 'low')),
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_path
                            },
                            "region": {
                                "startLine": issue.get('line', 1),
                                "startColumn": issue.get('column', 1)
                            }
                        }
                    }] if file_path else [],
                    "properties": {
                        "tool": result.tool,
                        "category": issue.get('rule', 'unknown'),
                        "confidence": issue.get('confidence', 0.8)
                    }
                }

                # Add code snippet if available
                if issue.get('code_snippet'):
                    sarif_result["locations"][0]["physicalLocation"]["contextRegion"] = {
                        "snippet": {
                            "text": issue['code_snippet']
                        }
                    }

                run["results"].append(sarif_result)

        return json.dumps(sarif, indent=2)

    def _calculate_risk_level(self, compliance_score: float) -> Dict[str, str]:
        """Calculate overall risk level based on compliance score."""
        if compliance_score >= 90:
            return {
                "level": "LOW RISK",
                "emoji": "✅",
                "business_impact": "Minimal security concerns, strong defensive posture"
            }
        elif compliance_score >= 70:
            return {
                "level": "MEDIUM RISK",
                "emoji": "⚠️",
                "business_impact": "Some security gaps present, manageable with focused effort"
            }
        else:
            return {
                "level": "HIGH RISK",
                "emoji": "🚨",
                "business_impact": "Significant security vulnerabilities requiring immediate attention"
            }

    def _count_issues_by_severity(self, scan_report: ScanReport) -> Dict[str, int]:
        """Count total issues by severity across all tools."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for result in scan_report.results:
            for issue in result.issues:
                severity = issue.get('severity', 'low').lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
                else:
                    severity_counts['low'] += 1

        return severity_counts

    def _sarif_severity_level(self, severity: str) -> str:
        """Convert severity to SARIF level."""
        severity_map = {
            'critical': 'error',
            'high': 'error',
            'medium': 'warning',
            'low': 'note',
            'info': 'note'
        }
        return severity_map.get(severity.lower(), 'note')