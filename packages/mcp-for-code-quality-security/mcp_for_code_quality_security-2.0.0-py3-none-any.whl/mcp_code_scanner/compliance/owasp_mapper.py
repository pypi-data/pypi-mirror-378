"""
OWASP Compliance Mapper - Maps security findings to OWASP standards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from datetime import datetime


class OWASPFramework(Enum):
    """Supported OWASP frameworks."""
    TOP_10_2021 = "owasp_top10_2021"
    API_TOP_10 = "owasp_api_top10"
    LLM_TOP_10 = "owasp_llm_top10"
    MOBILE_TOP_10 = "owasp_mobile_top10"


@dataclass
class ComplianceMapping:
    """Maps a finding to OWASP compliance standards."""
    finding_rule: str
    framework: OWASPFramework
    owasp_id: str
    owasp_title: str
    compliance_status: str  # "compliant", "non_compliant", "partial"
    severity_impact: str
    remediation_priority: int  # 1-5, 1 being highest priority


@dataclass
class ComplianceReport:
    """Complete OWASP compliance report."""
    project_name: str
    scan_timestamp: str
    frameworks: List[OWASPFramework]
    total_findings: int
    compliance_score: float  # 0-100
    framework_scores: Dict[str, float] = field(default_factory=dict)
    mappings: List[ComplianceMapping] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    executive_summary: str = ""


class OWASPMapper:
    """Maps security findings to OWASP compliance frameworks."""

    def __init__(self):
        self.frameworks = {
            OWASPFramework.TOP_10_2021: {
                "A01": {
                    "title": "Broken Access Control",
                    "description": "Access control enforces policy such that users cannot act outside of their intended permissions",
                    "cwe_ids": ["CWE-22", "CWE-306", "CWE-862"],
                    "severity_weight": 5
                },
                "A02": {
                    "title": "Cryptographic Failures",
                    "description": "Failures related to cryptography which often leads to sensitive data exposure",
                    "cwe_ids": ["CWE-327", "CWE-798", "CWE-916"],
                    "severity_weight": 4
                },
                "A03": {
                    "title": "Injection",
                    "description": "Injection flaws occur when untrusted data is sent to an interpreter",
                    "cwe_ids": ["CWE-89", "CWE-943", "CWE-94"],
                    "severity_weight": 5
                },
                "A04": {
                    "title": "Insecure Design",
                    "description": "Risks related to design flaws and missing security controls",
                    "cwe_ids": ["CWE-209", "CWE-256", "CWE-501"],
                    "severity_weight": 3
                },
                "A05": {
                    "title": "Security Misconfiguration",
                    "description": "Missing appropriate security hardening or misconfigured permissions",
                    "cwe_ids": ["CWE-346", "CWE-489", "CWE-611"],
                    "severity_weight": 3
                },
                "A06": {
                    "title": "Vulnerable and Outdated Components",
                    "description": "Components with known vulnerabilities or outdated versions",
                    "cwe_ids": ["CWE-1104", "CWE-1035"],
                    "severity_weight": 4
                },
                "A07": {
                    "title": "Identification and Authentication Failures",
                    "description": "Confirmation of user identity, authentication, and session management",
                    "cwe_ids": ["CWE-297", "CWE-384", "CWE-613"],
                    "severity_weight": 4
                },
                "A08": {
                    "title": "Software and Data Integrity Failures",
                    "description": "Software updates, critical data, and CI/CD pipelines without integrity verification",
                    "cwe_ids": ["CWE-502", "CWE-829"],
                    "severity_weight": 3
                },
                "A09": {
                    "title": "Security Logging and Monitoring Failures",
                    "description": "Insufficient logging and monitoring coupled with missing incident response",
                    "cwe_ids": ["CWE-117", "CWE-223", "CWE-532"],
                    "severity_weight": 2
                },
                "A10": {
                    "title": "Server-Side Request Forgery (SSRF)",
                    "description": "SSRF flaws occur when a web application fetches a remote resource without validating the user-supplied URL",
                    "cwe_ids": ["CWE-918"],
                    "severity_weight": 4
                }
            },
            OWASPFramework.LLM_TOP_10: {
                "LLM01": {
                    "title": "Prompt Injection",
                    "description": "Manipulating LLM through crafted inputs that override system instructions",
                    "cwe_ids": ["CWE-20", "CWE-74"],
                    "severity_weight": 5
                },
                "LLM02": {
                    "title": "Insecure Output Handling",
                    "description": "Insufficient validation, sanitization, and handling of LLM outputs",
                    "cwe_ids": ["CWE-79", "CWE-116"],
                    "severity_weight": 4
                },
                "LLM03": {
                    "title": "Training Data Poisoning",
                    "description": "Manipulating training data or fine-tuning procedures to introduce vulnerabilities",
                    "cwe_ids": ["CWE-20", "CWE-345"],
                    "severity_weight": 4
                },
                "LLM04": {
                    "title": "Model Denial of Service",
                    "description": "Causing resource-heavy operations that degrade service quality",
                    "cwe_ids": ["CWE-400", "CWE-770"],
                    "severity_weight": 3
                },
                "LLM05": {
                    "title": "Supply Chain Vulnerabilities",
                    "description": "Vulnerabilities in training datasets, models, and deployment environments",
                    "cwe_ids": ["CWE-1104", "CWE-829"],
                    "severity_weight": 4
                },
                "LLM06": {
                    "title": "Sensitive Information Disclosure",
                    "description": "LLM responses revealing confidential data, proprietary algorithms, or personal information",
                    "cwe_ids": ["CWE-200", "CWE-532"],
                    "severity_weight": 4
                },
                "LLM07": {
                    "title": "Insecure Plugin Design",
                    "description": "LLM plugins lacking proper access controls and input validation",
                    "cwe_ids": ["CWE-20", "CWE-862"],
                    "severity_weight": 5
                },
                "LLM08": {
                    "title": "Excessive Agency",
                    "description": "LLM-based systems granted excessive functionality, permissions, or autonomy",
                    "cwe_ids": ["CWE-250", "CWE-269"],
                    "severity_weight": 4
                },
                "LLM09": {
                    "title": "Overreliance",
                    "description": "Systems or people overly depending on LLMs without proper oversight",
                    "cwe_ids": ["CWE-1038"],
                    "severity_weight": 2
                },
                "LLM10": {
                    "title": "Model Theft",
                    "description": "Unauthorized access, copying, or exfiltration of proprietary LLM models",
                    "cwe_ids": ["CWE-200", "CWE-319"],
                    "severity_weight": 3
                }
            },
            OWASPFramework.API_TOP_10: {
                "API1": {
                    "title": "Broken Object Level Authorization",
                    "description": "Insufficient validation of object-level access control",
                    "cwe_ids": ["CWE-284", "CWE-639"],
                    "severity_weight": 5
                },
                "API2": {
                    "title": "Broken User Authentication",
                    "description": "Authentication mechanisms poorly implemented allowing attackers to compromise authentication tokens",
                    "cwe_ids": ["CWE-287", "CWE-384"],
                    "severity_weight": 5
                },
                "API3": {
                    "title": "Excessive Data Exposure",
                    "description": "APIs exposing more data than necessary",
                    "cwe_ids": ["CWE-200"],
                    "severity_weight": 3
                },
                "API4": {
                    "title": "Lack of Resources & Rate Limiting",
                    "description": "APIs without proper resource limiting allowing denial of service",
                    "cwe_ids": ["CWE-770", "CWE-400"],
                    "severity_weight": 3
                },
                "API5": {
                    "title": "Broken Function Level Authorization",
                    "description": "Complex access control policies with different hierarchies, groups, and roles",
                    "cwe_ids": ["CWE-285"],
                    "severity_weight": 4
                },
                "API6": {
                    "title": "Mass Assignment",
                    "description": "Binding client provided data to data models without proper filtering",
                    "cwe_ids": ["CWE-915"],
                    "severity_weight": 3
                },
                "API7": {
                    "title": "Security Misconfiguration",
                    "description": "Missing appropriate security hardening across the API stack",
                    "cwe_ids": ["CWE-16"],
                    "severity_weight": 3
                },
                "API8": {
                    "title": "Injection",
                    "description": "Injection flaws such as SQL, NoSQL, Command Injection occur when untrusted data is sent to an interpreter",
                    "cwe_ids": ["CWE-89", "CWE-943", "CWE-77"],
                    "severity_weight": 5
                },
                "API9": {
                    "title": "Improper Asset Management",
                    "description": "APIs tend to expose more endpoints than traditional web applications making proper documentation important",
                    "cwe_ids": ["CWE-1059"],
                    "severity_weight": 2
                },
                "API10": {
                    "title": "Insufficient Logging & Monitoring",
                    "description": "Insufficient logging and monitoring coupled with missing or ineffective integration with incident response",
                    "cwe_ids": ["CWE-778"],
                    "severity_weight": 2
                }
            }
        }

        # Rule to OWASP mapping
        self.rule_mappings = {
            # General Web Security -> OWASP Top 10 2021
            "sql_injection": [("A03", OWASPFramework.TOP_10_2021), ("API8", OWASPFramework.API_TOP_10)],
            "nosql_injection": [("A03", OWASPFramework.TOP_10_2021), ("API8", OWASPFramework.API_TOP_10)],
            "path_traversal": [("A01", OWASPFramework.TOP_10_2021)],
            "ssti": [("A03", OWASPFramework.TOP_10_2021)],
            "weak_crypto": [("A02", OWASPFramework.TOP_10_2021)],
            "insecure_cors": [("A05", OWASPFramework.TOP_10_2021), ("API7", OWASPFramework.API_TOP_10)],
            "missing_auth": [("A07", OWASPFramework.TOP_10_2021), ("API2", OWASPFramework.API_TOP_10)],
            "hardcoded_secrets": [("A02", OWASPFramework.TOP_10_2021)],
            "debug_enabled": [("A05", OWASPFramework.TOP_10_2021), ("API7", OWASPFramework.API_TOP_10)],
            "unsafe_deserialization": [("A08", OWASPFramework.TOP_10_2021)],

            # AI/LLM Security -> OWASP LLM Top 10
            "prompt_injection": [("LLM01", OWASPFramework.LLM_TOP_10)],
            "model_extraction": [("LLM10", OWASPFramework.LLM_TOP_10)],
            "training_data_poisoning": [("LLM03", OWASPFramework.LLM_TOP_10)],
            "insecure_model_storage": [("LLM06", OWASPFramework.LLM_TOP_10)],
            "model_inversion": [("LLM06", OWASPFramework.LLM_TOP_10)],
            "adversarial_input": [("LLM02", OWASPFramework.LLM_TOP_10)],
            "unsafe_plugin_execution": [("LLM07", OWASPFramework.LLM_TOP_10)],
            "excessive_agency": [("LLM08", OWASPFramework.LLM_TOP_10)],
            "insecure_model_communication": [("LLM09", OWASPFramework.LLM_TOP_10)],
            "model_supply_chain": [("LLM05", OWASPFramework.LLM_TOP_10)],
        }

    def map_findings_to_compliance(self, findings: List[Dict[str, Any]],
                                 project_name: str = "Unknown Project") -> ComplianceReport:
        """Map security findings to OWASP compliance standards."""

        mappings = []
        framework_counts = {fw: {"total": 0, "compliant": 0} for fw in OWASPFramework}

        for finding in findings:
            rule = finding.get('rule', '')
            severity = finding.get('severity', 'info')

            # Map to OWASP frameworks
            if rule in self.rule_mappings:
                for owasp_id, framework in self.rule_mappings[rule]:
                    if framework in self.frameworks:
                        framework_info = self.frameworks[framework].get(owasp_id, {})

                        compliance_status = self._determine_compliance_status(severity)

                        mapping = ComplianceMapping(
                            finding_rule=rule,
                            framework=framework,
                            owasp_id=owasp_id,
                            owasp_title=framework_info.get('title', 'Unknown'),
                            compliance_status=compliance_status,
                            severity_impact=severity,
                            remediation_priority=self._calculate_priority(severity, framework_info.get('severity_weight', 3))
                        )
                        mappings.append(mapping)

                        # Update framework counts
                        framework_counts[framework]["total"] += 1
                        if compliance_status == "compliant":
                            framework_counts[framework]["compliant"] += 1

        # Calculate compliance scores
        framework_scores = {}
        for framework, counts in framework_counts.items():
            if counts["total"] > 0:
                score = (counts["compliant"] / counts["total"]) * 100
                framework_scores[framework.value] = round(score, 2)
            else:
                framework_scores[framework.value] = 100.0  # No issues = 100% compliant

        # Overall compliance score (weighted average)
        total_findings = sum(counts["total"] for counts in framework_counts.values())
        if total_findings > 0:
            total_compliant = sum(counts["compliant"] for counts in framework_counts.values())
            overall_score = (total_compliant / total_findings) * 100
        else:
            overall_score = 100.0

        # Generate recommendations
        recommendations = self._generate_recommendations(mappings)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            total_findings, overall_score, framework_scores, mappings
        )

        return ComplianceReport(
            project_name=project_name,
            scan_timestamp=datetime.now().isoformat(),
            frameworks=[fw for fw, counts in framework_counts.items() if counts["total"] > 0],
            total_findings=len(findings),
            compliance_score=round(overall_score, 2),
            framework_scores=framework_scores,
            mappings=mappings,
            recommendations=recommendations,
            executive_summary=executive_summary
        )

    def _determine_compliance_status(self, severity: str) -> str:
        """Determine compliance status based on severity."""
        severity_lower = severity.lower()
        if severity_lower in ['critical', 'high']:
            return "non_compliant"
        elif severity_lower == 'medium':
            return "partial"
        else:
            return "compliant"

    def _calculate_priority(self, severity: str, weight: int) -> int:
        """Calculate remediation priority (1-5, 1 being highest)."""
        severity_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4, 'info': 5}
        base_priority = severity_map.get(severity.lower(), 5)

        # Adjust based on OWASP weight
        adjusted_priority = max(1, min(5, base_priority - (weight - 3)))
        return adjusted_priority

    def _generate_recommendations(self, mappings: List[ComplianceMapping]) -> List[str]:
        """Generate prioritized recommendations based on mappings."""
        recommendations = []

        # Group by priority
        priority_groups = {}
        for mapping in mappings:
            priority = mapping.remediation_priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(mapping)

        # Generate recommendations by priority
        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]

            if priority <= 2:  # High priority
                recommendations.append(
                    f"🚨 CRITICAL: Address {len(group)} high-priority OWASP violations immediately "
                    f"({', '.join(set(m.owasp_id for m in group))})"
                )
            elif priority == 3:  # Medium priority
                recommendations.append(
                    f"⚠️ MEDIUM: Plan remediation for {len(group)} medium-priority issues "
                    f"({', '.join(set(m.owasp_id for m in group))})"
                )
            else:  # Low priority
                recommendations.append(
                    f"📝 LOW: Consider addressing {len(group)} lower-priority items in next iteration"
                )

        # Framework-specific recommendations
        frameworks_with_issues = set(m.framework for m in mappings)
        if OWASPFramework.LLM_TOP_10 in frameworks_with_issues:
            recommendations.append(
                "🤖 AI/LLM Security: Implement LLM-specific security controls and monitoring"
            )
        if OWASPFramework.API_TOP_10 in frameworks_with_issues:
            recommendations.append(
                "🔌 API Security: Strengthen API security with proper authentication and rate limiting"
            )

        return recommendations

    def _generate_executive_summary(self, total_findings: int, overall_score: float,
                                  framework_scores: Dict[str, float],
                                  mappings: List[ComplianceMapping]) -> str:
        """Generate executive summary of compliance status."""

        if total_findings == 0:
            return "✅ Excellent security posture with no major vulnerabilities detected."

        # Determine overall status
        if overall_score >= 90:
            status_icon = "✅"
            status_text = "GOOD"
        elif overall_score >= 70:
            status_icon = "⚠️"
            status_text = "NEEDS IMPROVEMENT"
        else:
            status_icon = "🚨"
            status_text = "CRITICAL"

        critical_count = len([m for m in mappings if m.remediation_priority <= 2])

        summary = f"""
{status_icon} SECURITY COMPLIANCE STATUS: {status_text}

Overall Compliance Score: {overall_score:.1f}%
Total Security Findings: {total_findings}
Critical/High Priority Issues: {critical_count}

Framework Breakdown:"""

        for framework, score in framework_scores.items():
            if score >= 90:
                icon = "✅"
            elif score >= 70:
                icon = "⚠️"
            else:
                icon = "🚨"
            summary += f"\n  {icon} {framework.replace('_', ' ').title()}: {score:.1f}%"

        if critical_count > 0:
            summary += f"\n\n🎯 IMMEDIATE ACTION REQUIRED: {critical_count} critical security issues need urgent attention."
        else:
            summary += "\n\n🎯 NEXT STEPS: Focus on improving medium and low priority findings."

        return summary.strip()

    def generate_compliance_report_json(self, report: ComplianceReport) -> str:
        """Generate JSON format compliance report."""
        report_dict = {
            "project_name": report.project_name,
            "scan_timestamp": report.scan_timestamp,
            "compliance_score": report.compliance_score,
            "total_findings": report.total_findings,
            "framework_scores": report.framework_scores,
            "executive_summary": report.executive_summary,
            "recommendations": report.recommendations,
            "detailed_mappings": [
                {
                    "rule": mapping.finding_rule,
                    "framework": mapping.framework.value,
                    "owasp_id": mapping.owasp_id,
                    "owasp_title": mapping.owasp_title,
                    "compliance_status": mapping.compliance_status,
                    "severity": mapping.severity_impact,
                    "priority": mapping.remediation_priority
                }
                for mapping in report.mappings
            ]
        }
        return json.dumps(report_dict, indent=2)

    def generate_compliance_report_markdown(self, report: ComplianceReport) -> str:
        """Generate Markdown format compliance report."""
        md = f"""# OWASP Compliance Report

## Project: {report.project_name}
**Scan Date:** {report.scan_timestamp}
**Overall Compliance Score:** {report.compliance_score}%
**Total Findings:** {report.total_findings}

## Executive Summary

{report.executive_summary}

## Framework Compliance Scores

| Framework | Score | Status |
|-----------|-------|---------|"""

        for framework, score in report.framework_scores.items():
            if score >= 90:
                status = "✅ Good"
            elif score >= 70:
                status = "⚠️ Needs Improvement"
            else:
                status = "🚨 Critical"

            framework_name = framework.replace('_', ' ').title()
            md += f"\n| {framework_name} | {score}% | {status} |"

        md += "\n\n## Recommendations\n"
        for i, rec in enumerate(report.recommendations, 1):
            md += f"\n{i}. {rec}"

        md += "\n\n## Detailed Findings\n"

        # Group by framework
        framework_groups = {}
        for mapping in report.mappings:
            fw = mapping.framework.value
            if fw not in framework_groups:
                framework_groups[fw] = []
            framework_groups[fw].append(mapping)

        for framework, mappings in framework_groups.items():
            md += f"\n### {framework.replace('_', ' ').title()}\n"

            for mapping in sorted(mappings, key=lambda x: x.remediation_priority):
                priority_icon = "🚨" if mapping.remediation_priority <= 2 else "⚠️" if mapping.remediation_priority == 3 else "📝"
                status_icon = "❌" if mapping.compliance_status == "non_compliant" else "⚠️" if mapping.compliance_status == "partial" else "✅"

                md += f"- {priority_icon} **{mapping.owasp_id}: {mapping.owasp_title}** {status_icon}\n"
                md += f"  - Rule: `{mapping.finding_rule}`\n"
                md += f"  - Severity: {mapping.severity_impact}\n"
                md += f"  - Priority: {mapping.remediation_priority}/5\n\n"

        return md