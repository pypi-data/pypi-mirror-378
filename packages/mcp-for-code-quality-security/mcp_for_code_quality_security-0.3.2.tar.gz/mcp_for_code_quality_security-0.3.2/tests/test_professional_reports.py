#!/usr/bin/env python3
"""
Test script for professional reporting system (Option B implementation).

Demonstrates enterprise-grade CI/CD integration capabilities:
- Executive reports for C-level stakeholders
- Technical reports for development teams
- SARIF format for GitHub Security integration
- CI/CD templates (GitHub Actions, GitLab CI, pre-commit hooks)
- Makefile with quality targets
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from src.mcp_code_scanner.scanners.fastapi_scanner import FastAPISecurityScanner
from src.mcp_code_scanner.scanners.ai_security_scanner import AISecurityScanner
from src.mcp_code_scanner.compliance.owasp_mapper import OWASPMapper
from src.mcp_code_scanner.reports import (
    EnterpriseReportGenerator,
    ReportConfig,
    CICDGenerator,
    SARIFGenerator
)
from src.mcp_code_scanner.core.models import ScanReport, ScanResult


async def test_professional_reporting():
    """Test complete professional reporting system."""

    print("🏢 Testing Professional Reporting System (Option B)")
    print("=" * 60)

    # Setup test environment
    project_path = Path(".")
    output_dir = Path("reports_output")
    output_dir.mkdir(exist_ok=True)

    # Initialize scanners
    fastapi_scanner = FastAPISecurityScanner()
    ai_scanner = AISecurityScanner()
    owasp_mapper = OWASPMapper()

    # Initialize report generators
    report_config = ReportConfig(
        company_name="Your Enterprise",
        include_executive_summary=True,
        include_compliance_mapping=True,
        include_remediation_guide=True,
        include_cicd_examples=True
    )

    enterprise_generator = EnterpriseReportGenerator(report_config)
    sarif_generator = SARIFGenerator()
    cicd_generator = CICDGenerator()

    print("1. Running Security Scans...")
    print("-" * 30)

    # Run FastAPI security scan
    print("   🔍 FastAPI Security Scan...")
    fastapi_result = await fastapi_scanner.scan_fastapi_project(project_path)

    # Run AI security scan
    print("   🤖 AI Security Scan...")
    ai_result = await ai_scanner.scan_ai_project(project_path)

    # Create mock scan report
    scan_report = ScanReport(
        project_path=str(project_path),
        timestamp=datetime.now().isoformat(),
        scan_config="professional_demo",
        results=[
            ScanResult(
                tool="fastapi_security",
                success=True,
                issues=fastapi_result.issues,
                execution_time=1.2,
                metadata={"version": "2.0.0", "files_scanned": 5}
            ),
            ScanResult(
                tool="ai_security",
                success=True,
                issues=ai_result.issues,
                execution_time=0.8,
                metadata={"version": "2.0.0", "files_scanned": 3}
            )
        ],
        summary={
            "execution_time": 2.0,
            "total_issues": len(fastapi_result.issues) + len(ai_result.issues)
        }
    )

    print(f"   ✅ Found {scan_report.summary['total_issues']} security issues")

    print("\n2. Generating OWASP Compliance Report...")
    print("-" * 40)

    # Generate OWASP compliance mapping
    all_issues = []
    for result in scan_report.results:
        all_issues.extend(result.issues)

    compliance_report = owasp_mapper.map_findings_to_compliance(all_issues)

    print(f"   📊 Overall Compliance Score: {compliance_report.compliance_score:.1f}%")
    print(f"   🎯 Total Findings: {compliance_report.total_findings}")
    print(f"   📋 OWASP Mappings: {len(compliance_report.mappings)}")

    print("\n3. Generating Enterprise Reports...")
    print("-" * 35)

    # Generate executive report
    print("   📊 Executive Summary Report...")
    executive_report = enterprise_generator.generate_executive_report(
        scan_report, compliance_report, "MCP Security Scanner Demo"
    )

    executive_file = output_dir / "executive_summary.md"
    executive_file.write_text(executive_report)
    print(f"   ✅ Saved: {executive_file}")

    # Generate technical report
    print("   🔧 Technical Development Report...")
    technical_report = enterprise_generator.generate_technical_report(
        scan_report, compliance_report, "MCP Security Scanner Demo"
    )

    technical_file = output_dir / "technical_report.md"
    technical_file.write_text(technical_report)
    print(f"   ✅ Saved: {technical_file}")

    print("\n4. Generating CI/CD Integration Files...")
    print("-" * 40)

    # Generate SARIF report
    print("   📄 SARIF Format (GitHub Security)...")
    sarif_report = sarif_generator.generate_sarif(scan_report, compliance_report)

    sarif_file = output_dir / "security_results.sarif"
    sarif_file.write_text(sarif_report)
    print(f"   ✅ Saved: {sarif_file}")

    # Generate GitHub-optimized SARIF
    github_sarif = sarif_generator.generate_github_security_sarif(
        scan_report, compliance_report
    )

    github_sarif_file = output_dir / "github_security.sarif"
    github_sarif_file.write_text(github_sarif)
    print(f"   ✅ Saved: {github_sarif_file}")

    # Generate pre-commit hooks
    print("   🪝 Pre-commit Hooks Configuration...")
    precommit_config = cicd_generator.generate_precommit_hooks(project_path)

    precommit_file = output_dir / ".pre-commit-config.yaml"
    precommit_file.write_text(precommit_config)
    print(f"   ✅ Saved: {precommit_file}")

    # Generate GitHub Actions workflow
    print("   🚀 GitHub Actions Workflow...")
    github_workflow = cicd_generator.generate_github_actions_workflow("MCP Security Scanner")

    github_file = output_dir / "security_workflow.yml"
    github_file.write_text(github_workflow)
    print(f"   ✅ Saved: {github_file}")

    # Generate GitLab CI pipeline
    print("   🦊 GitLab CI Pipeline...")
    gitlab_pipeline = cicd_generator.generate_gitlab_ci_pipeline("MCP Security Scanner")

    gitlab_file = output_dir / ".gitlab-ci.yml"
    gitlab_file.write_text(gitlab_pipeline)
    print(f"   ✅ Saved: {gitlab_file}")

    # Generate Makefile
    print("   🔨 Makefile with Quality Targets...")
    makefile_content = cicd_generator.generate_makefile()

    makefile = output_dir / "Makefile"
    makefile.write_text(makefile_content)
    print(f"   ✅ Saved: {makefile}")

    # Generate Docker security example
    print("   🐳 Docker Security Example...")
    docker_content = cicd_generator.generate_docker_security_example()

    docker_file = output_dir / "Dockerfile.security"
    docker_file.write_text(docker_content)
    print(f"   ✅ Saved: {docker_file}")

    print("\n5. Summary of Generated Files...")
    print("-" * 35)

    files_generated = list(output_dir.glob("*"))
    for file in sorted(files_generated):
        size_kb = file.stat().st_size / 1024
        print(f"   📁 {file.name:<25} ({size_kb:.1f} KB)")

    print(f"\n✅ Professional Reporting System Complete!")
    print(f"📂 All files saved to: {output_dir.absolute()}")
    print(f"🏢 Enterprise-ready CI/CD integration templates generated")

    # Print quick usage instructions
    print("\n📋 Quick Start Guide:")
    print("-" * 20)
    print("• Copy .pre-commit-config.yaml to your project root")
    print("• Add security_workflow.yml to .github/workflows/")
    print("• Use Makefile targets: make security, make ci-full")
    print("• Upload SARIF files to GitHub Security tab")
    print("• Share executive_summary.md with C-level stakeholders")
    print("• Use technical_report.md for development team reviews")


if __name__ == "__main__":
    asyncio.run(test_professional_reporting())