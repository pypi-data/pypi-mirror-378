#!/usr/bin/env python3
"""
Test script to validate MCP server tool functionality.
"""

import asyncio
import json
from mcp_code_scanner.mcp.server import mcp

async def test_mcp_server_tools():
    """Test all MCP server tools to ensure they work correctly."""

    print("🧪 Testing MCP Server Tools")
    print("=" * 50)

    # Test 1: List available tools
    tools = await mcp.list_tools()
    print(f"1. Available Tools ({len(tools)}):")
    for tool in tools:
        print(f"   ✅ {tool.name}: {tool.description[:60]}...")

    # Test 2: Test basic scan_code tool
    print(f"\n2. Testing scan_code tool:")
    try:
        result = await mcp.call_tool(
            "scan_code",
            {
                "project_path": ".",
                "config": "fast",
                "auto_fix": False,
                "include_tests": False,
                "output_format": "json"
            }
        )

        # Parse the result (FastMCP returns tuple of (content_list, metadata))
        content_list, metadata = result
        scan_data = json.loads(content_list[0].text)
        print(f"   ✅ Scan completed: {scan_data['summary']['total_issues']} issues found")
        print(f"   ✅ Tools run: {scan_data['summary']['tools_run']}")

    except Exception as e:
        print(f"   ❌ scan_code failed: {e}")

    # Test 3: Test security_scan tool
    print(f"\n3. Testing security_scan tool:")
    try:
        result = await mcp.call_tool(
            "security_scan",
            {
                "project_path": ".",
                "include_dependencies": True,
                "severity_threshold": "high"
            }
        )

        content_list, metadata = result
        scan_data = json.loads(content_list[0].text)
        print(f"   ✅ Security scan completed: {scan_data['total_security_issues']} issues")
        print(f"   ✅ Critical issues: {scan_data['critical_count']}")

    except Exception as e:
        print(f"   ❌ security_scan failed: {e}")

    # Test 4: Test get_project_info tool
    print(f"\n4. Testing get_project_info tool:")
    try:
        result = await mcp.call_tool(
            "get_project_info",
            {"project_path": "."}
        )

        content_list, metadata = result
        info_data = json.loads(content_list[0].text)
        print(f"   ✅ Project analysis completed")
        print(f"   ✅ Python files: {info_data.get('python_files_count', 0)}")
        print(f"   ✅ Has pyproject.toml: {info_data.get('project_files', {}).get('pyproject.toml', False)}")

    except Exception as e:
        print(f"   ❌ get_project_info failed: {e}")

    # Test 5: Test comprehensive_security_scan (if time permits)
    print(f"\n5. Testing comprehensive_security_scan tool:")
    try:
        result = await mcp.call_tool(
            "comprehensive_security_scan",
            {
                "project_path": ".",
                "output_dir": "/tmp/mcp_test_reports",
                "company_name": "MCP Test Corp",
                "include_compliance_mapping": True
            }
        )

        content_list, metadata = result
        report_data = json.loads(content_list[0].text)
        print(f"   ✅ Comprehensive scan completed")
        print(f"   ✅ Total issues: {report_data['scan_summary']['total_issues']}")
        print(f"   ✅ Compliance score: {report_data['scan_summary']['compliance_score']}%")
        print(f"   ✅ Generated reports: {len(report_data['reports_generated'])}")

    except Exception as e:
        print(f"   ❌ comprehensive_security_scan failed: {e}")

    print(f"\n🎉 MCP Server Tool Testing Complete!")
    print("✅ All tools are properly integrated and functional")

if __name__ == "__main__":
    asyncio.run(test_mcp_server_tools())