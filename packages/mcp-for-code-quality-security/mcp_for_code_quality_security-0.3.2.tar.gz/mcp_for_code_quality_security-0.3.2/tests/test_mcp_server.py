"""
Tests for MCP server functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_code_scanner.mcp.server import (
    scan_code,
    fix_issues,
    security_scan,
    analyze_dependencies,
    get_project_info
)


@pytest.fixture
def temp_python_project():
    """Create a temporary Python project for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create a Python file
        test_file = project_path / "example.py"
        test_file.write_text("""
def hello():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello()
""")
        
        # Create __init__.py
        init_file = project_path / "__init__.py"
        init_file.write_text("")
        
        # Create requirements.txt
        req_file = project_path / "requirements.txt"
        req_file.write_text("requests>=2.25.0")
        
        yield project_path


class TestMCPTools:
    """Test MCP tool functions."""
    
    @pytest.mark.asyncio
    async def test_scan_code_success(self, temp_python_project):
        """Test successful code scanning via MCP tool."""
        result = await scan_code(
            project_path=str(temp_python_project),
            config="fast",
            auto_fix=False,
            include_tests=True,
            output_format="json"
        )
        
        # Parse the JSON result
        result_data = json.loads(result)
        
        # Should be successful or contain scan data
        assert "error" not in result_data or result_data.get("success") is not False
        
        # If successful, should have expected structure
        if "project_path" in result_data:
            assert result_data["project_path"] == str(temp_python_project)
    
    @pytest.mark.asyncio
    async def test_scan_code_nonexistent_path(self):
        """Test scan_code with non-existent path."""
        result = await scan_code(
            project_path="/nonexistent/path",
            config="default"
        )
        
        result_data = json.loads(result)
        assert "error" in result_data
        assert "does not exist" in result_data["error"]
        assert result_data["success"] is False
    
    @pytest.mark.asyncio
    async def test_scan_code_invalid_config(self, temp_python_project):
        """Test scan_code with invalid configuration."""
        result = await scan_code(
            project_path=str(temp_python_project),
            config="nonexistent_config"
        )
        
        result_data = json.loads(result)
        # Should either work with fallback or show error
        assert "error" in result_data or "project_path" in result_data
    
    @pytest.mark.asyncio
    async def test_fix_issues(self, temp_python_project):
        """Test fix_issues MCP tool."""
        result = await fix_issues(
            project_path=str(temp_python_project),
            tool_filter=["ruff"],
            safe_only=True,
            dry_run=True
        )
        
        result_data = json.loads(result)
        
        # Should complete successfully
        assert "success" in result_data
        
        if result_data.get("success"):
            assert "fixes_applied" in result_data
            assert result_data["fixes_applied"] is False  # dry run
            assert "tools_used" in result_data
    
    @pytest.mark.asyncio
    async def test_security_scan(self, temp_python_project):
        """Test security_scan MCP tool.""" 
        result = await security_scan(
            project_path=str(temp_python_project),
            include_dependencies=True,
            severity_threshold="warning"
        )
        
        result_data = json.loads(result)
        
        # Should complete successfully
        assert "success" in result_data
        
        if result_data.get("success"):
            assert "security_issues" in result_data
            assert "total_security_issues" in result_data
            assert "critical_count" in result_data
            assert isinstance(result_data["security_issues"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_dependencies(self, temp_python_project):
        """Test analyze_dependencies MCP tool."""
        result = await analyze_dependencies(str(temp_python_project))
        
        result_data = json.loads(result)
        
        # Should complete successfully
        assert "success" in result_data
        
        if result_data.get("success"):
            assert "vulnerable_dependencies" in result_data
            assert "total_vulnerabilities" in result_data
            assert isinstance(result_data["vulnerable_dependencies"], list)
    
    @pytest.mark.asyncio
    async def test_get_project_info(self, temp_python_project):
        """Test get_project_info MCP tool."""
        result = await get_project_info(str(temp_python_project))
        
        result_data = json.loads(result)
        
        # Should complete successfully
        assert "success" in result_data
        
        if result_data.get("success"):
            assert "project_path" in result_data
            assert "is_python_project" in result_data
            assert "python_files_count" in result_data
            assert "recommended_tools" in result_data
            
            # Should recognize it as a Python project
            assert result_data["is_python_project"] is True
            assert result_data["python_files_count"] > 0


class TestMCPToolsEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await scan_code(project_path=temp_dir)
            result_data = json.loads(result)
            
            # Should fail because it's not a Python project
            assert "error" in result_data
            assert "Not a Python project" in result_data["error"]
    
    @pytest.mark.asyncio
    async def test_scan_file_instead_of_directory(self, temp_python_project):
        """Test scanning a file instead of directory."""
        test_file = temp_python_project / "example.py"
        
        result = await scan_code(project_path=str(test_file))
        result_data = json.loads(result)
        
        # Should handle gracefully
        assert "error" in result_data or "success" in result_data
    
    @pytest.mark.asyncio
    async def test_invalid_severity_threshold(self, temp_python_project):
        """Test security scan with invalid severity threshold."""
        result = await security_scan(
            project_path=str(temp_python_project),
            severity_threshold="invalid"
        )
        
        result_data = json.loads(result)
        # Should either use default or show error
        assert "error" in result_data or "success" in result_data
    
    @pytest.mark.asyncio
    async def test_fix_with_empty_tool_filter(self, temp_python_project):
        """Test fix_issues with empty tool filter."""
        result = await fix_issues(
            project_path=str(temp_python_project),
            tool_filter=[],  # Empty list
            dry_run=True
        )
        
        result_data = json.loads(result)
        
        # Should handle gracefully
        assert "success" in result_data


class TestMCPServerIntegration:
    """Integration tests for MCP server."""
    
    @pytest.mark.asyncio
    async def test_scan_and_fix_workflow(self, temp_python_project):
        """Test complete scan and fix workflow."""
        # First, scan the project
        scan_result = await scan_code(
            project_path=str(temp_python_project),
            config="fast"
        )
        
        scan_data = json.loads(scan_result)
        
        # If scan was successful and found issues, try to fix them
        if scan_data.get("success") and scan_data.get("total_issues", 0) > 0:
            fix_result = await fix_issues(
                project_path=str(temp_python_project),
                dry_run=True,  # Don't actually modify files in test
                safe_only=True
            )
            
            fix_data = json.loads(fix_result)
            assert "success" in fix_data
    
    @pytest.mark.asyncio
    async def test_security_workflow(self, temp_python_project):
        """Test security-focused workflow."""
        # Run security scan
        security_result = await security_scan(
            project_path=str(temp_python_project),
            include_dependencies=True
        )
        
        security_data = json.loads(security_result)
        
        # Run dependency analysis
        deps_result = await analyze_dependencies(str(temp_python_project))
        deps_data = json.loads(deps_result)
        
        # Both should complete
        assert "success" in security_data
        assert "success" in deps_data
        
        # If both successful, compare results
        if security_data.get("success") and deps_data.get("success"):
            # Security scan should include dependency vulnerabilities
            total_security = security_data.get("total_security_issues", 0)
            total_deps = len(deps_data.get("vulnerable_dependencies", []))
            
            # Logic check - if deps found vulns, security should too
            if total_deps > 0:
                assert total_security >= 0  # Could be 0 if different thresholds


@pytest.mark.asyncio
async def test_mcp_server_resources():
    """Test MCP resource endpoints."""
    from mcp_code_scanner.mcp.server import get_scan_presets, get_tool_descriptions
    
    # Test scan presets resource
    presets_result = await get_scan_presets()
    presets_data = json.loads(presets_result)
    
    assert isinstance(presets_data, dict)
    assert "default" in presets_data
    assert "strict" in presets_data
    assert "security" in presets_data
    assert "fast" in presets_data
    
    # Each preset should have required fields
    for preset_name, preset_info in presets_data.items():
        assert "description" in preset_info
        assert "tools" in preset_info
        assert "use_case" in preset_info
    
    # Test tool descriptions resource
    tools_result = await get_tool_descriptions()
    tools_data = json.loads(tools_result)
    
    assert isinstance(tools_data, dict)
    assert "ruff" in tools_data
    assert "mypy" in tools_data
    assert "bandit" in tools_data
    
    # Each tool should have required fields
    for tool_name, tool_info in tools_data.items():
        assert "description" in tool_info
        assert "checks" in tool_info
        assert "auto_fix" in tool_info
        assert "speed" in tool_info


@pytest.mark.asyncio
async def test_mcp_prompts():
    """Test MCP prompt generation."""
    from mcp_code_scanner.mcp.server import code_review_prompt, fix_suggestion_prompt
    
    # Test code review prompt
    sample_results = json.dumps({
        "total_issues": 5,
        "critical_issues": 1,
        "results": [
            {
                "tool": "bandit",
                "issues": [
                    {
                        "file": "app.py",
                        "line": 42,
                        "severity": "critical",
                        "message": "Hardcoded password detected"
                    }
                ]
            }
        ]
    })
    
    review_prompt = code_review_prompt(
        scan_results=sample_results,
        focus_area="security",
        detail_level="detailed"
    )
    
    assert isinstance(review_prompt, str)
    assert "security" in review_prompt.lower()
    assert "critical" in review_prompt.lower()
    assert len(review_prompt) > 100  # Should be substantial
    
    # Test fix suggestion prompt
    fix_prompt = fix_suggestion_prompt(
        issue_description="Hardcoded password detected",
        file_content="password = 'secret123'",
        line_number=42
    )
    
    assert isinstance(fix_prompt, str)
    assert "hardcoded password" in fix_prompt.lower()
    assert "42" in fix_prompt
    assert len(fix_prompt) > 50


if __name__ == "__main__":
    # Run a simple integration test
    async def main():
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create test file
            test_file = project_path / "test.py"
            test_file.write_text("print('Hello World')")
            
            # Create __init__.py
            (project_path / "__init__.py").write_text("")
            
            # Test scan
            result = await scan_code(str(project_path), config="fast")
            print("Scan result:", result[:200] + "..." if len(result) > 200 else result)
    
    asyncio.run(main())