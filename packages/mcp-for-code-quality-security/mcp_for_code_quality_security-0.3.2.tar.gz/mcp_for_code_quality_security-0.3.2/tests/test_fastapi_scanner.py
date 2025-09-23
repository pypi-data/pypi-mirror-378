#!/usr/bin/env python3
"""
Test script for the enhanced MCP scanner with FastAPI and AI security capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_code_scanner.core.scanner import CodeScanner, ScanConfig
from mcp_code_scanner.compliance.owasp_mapper import OWASPMapper


async def test_vulnerable_fastapi():
    """Test the scanner on the vulnerable FastAPI application."""

    # Path to the vulnerable FastAPI app
    vfapi_path = Path(__file__).parent / "tests" / "vulnerable_apps" / "vfapi"

    if not vfapi_path.exists():
        print(f"❌ Vulnerable FastAPI app not found at {vfapi_path}")
        return

    print(f"🔍 Testing enhanced MCP scanner on vulnerable FastAPI app: {vfapi_path}")

    # Create scanner with security preset
    config = ScanConfig.get_preset('security')
    scanner = CodeScanner(config)

    try:
        # Run the scan
        print("\n📊 Running security scan...")
        scan_report = await scanner.scan_project(vfapi_path)

        print(f"\n✅ Scan completed successfully!")
        print(f"📈 Total tools run: {len(scan_report.results)}")
        print(f"🔍 Total issues found: {scan_report.total_issues}")
        print(f"🚨 Critical issues: {scan_report.critical_issues}")

        # Show results by tool
        print("\n📋 Results by tool:")
        for result in scan_report.results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.tool}: {len(result.issues)} issues")

            # Show sample issues for security tools
            if result.tool in ['fastapi_security', 'ai_security'] and result.issues:
                print(f"    Sample issues:")
                for issue in result.issues[:3]:  # Show first 3 issues
                    print(f"      - {issue.get('rule', 'unknown')}: {issue.get('message', 'No message')}")
                if len(result.issues) > 3:
                    print(f"      ... and {len(result.issues) - 3} more")

        # Generate OWASP compliance report
        print("\n🏛️ Generating OWASP compliance report...")
        compliance_report = scanner.generate_compliance_report(scan_report, "Vulnerable FastAPI Test")

        print(f"\n📊 OWASP Compliance Report:")
        print(f"Overall Compliance Score: {compliance_report.compliance_score}%")
        print(f"Total Findings: {compliance_report.total_findings}")

        print("\nFramework Scores:")
        for framework, score in compliance_report.framework_scores.items():
            print(f"  {framework}: {score}%")

        print(f"\nExecutive Summary:")
        print(compliance_report.executive_summary)

        print(f"\nRecommendations:")
        for i, rec in enumerate(compliance_report.recommendations, 1):
            print(f"  {i}. {rec}")

        # Save reports
        reports_dir = Path(__file__).parent / "test_reports"
        reports_dir.mkdir(exist_ok=True)

        # Save scan report as JSON
        with open(reports_dir / "scan_report.json", "w") as f:
            f.write(scan_report.model_dump_json(indent=2))

        # Save compliance report as Markdown
        mapper = OWASPMapper()
        markdown_report = mapper.generate_compliance_report_markdown(compliance_report)
        with open(reports_dir / "compliance_report.md", "w") as f:
            f.write(markdown_report)

        # Save compliance report as JSON
        compliance_json = mapper.generate_compliance_report_json(compliance_report)
        with open(reports_dir / "compliance_report.json", "w") as f:
            f.write(compliance_json)

        print(f"\n📁 Reports saved to {reports_dir}:")
        print(f"  - scan_report.json")
        print(f"  - compliance_report.md")
        print(f"  - compliance_report.json")

    except Exception as e:
        print(f"❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()


async def test_vulnerable_llm_agent():
    """Test the scanner on the vulnerable LLM agent."""

    # Path to the vulnerable LLM agent
    llm_agent_path = Path(__file__).parent / "tests" / "vulnerable_apps" / "damn-vulnerable-llm-agent"

    if not llm_agent_path.exists():
        print(f"❌ Vulnerable LLM agent not found at {llm_agent_path}")
        return

    print(f"\n🤖 Testing enhanced MCP scanner on vulnerable LLM agent: {llm_agent_path}")

    # Create scanner with AI security focus
    config = ScanConfig(
        enabled_tools={'ai_security', 'bandit', 'ruff'},
        min_severity='info'
    )
    scanner = CodeScanner(config)

    try:
        # Run the scan
        print("📊 Running AI security scan...")
        scan_report = await scanner.scan_project(llm_agent_path)

        print(f"\n✅ AI security scan completed!")
        print(f"🔍 Total issues found: {scan_report.total_issues}")

        # Show AI security specific results
        for result in scan_report.results:
            if result.tool == 'ai_security' and result.issues:
                print(f"\n🤖 AI Security Issues ({len(result.issues)} found):")
                for issue in result.issues:
                    print(f"  - {issue.get('rule', 'unknown')}: {issue.get('message', 'No message')}")
                    if 'owasp_llm_mapping' in issue:
                        print(f"    OWASP LLM: {', '.join(issue['owasp_llm_mapping'])}")

        # Generate compliance report focused on LLM
        compliance_report = scanner.generate_compliance_report(scan_report, "Vulnerable LLM Agent Test")

        print(f"\n🏛️ LLM Security Compliance:")
        if 'owasp_llm_top10' in compliance_report.framework_scores:
            score = compliance_report.framework_scores['owasp_llm_top10']
            print(f"OWASP LLM Top 10 Score: {score}%")

    except Exception as e:
        print(f"❌ AI security scan failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("🚀 Enhanced MCP Agent Security Scanner Test")
    print("=" * 50)

    # Test 1: Vulnerable FastAPI application
    await test_vulnerable_fastapi()

    # Test 2: Vulnerable LLM agent
    await test_vulnerable_llm_agent()

    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    asyncio.run(main())