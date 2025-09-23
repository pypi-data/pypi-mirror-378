"""
Tests for the core scanner functionality.
"""

import asyncio
import tempfile
from pathlib import Path
import pytest

from mcp_code_scanner.core.scanner import CodeScanner, ScanConfig, ScanResult
from mcp_code_scanner.utils.file_utils import find_python_files


@pytest.fixture
def temp_python_project():
    """Create a temporary Python project for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create a simple Python file with some issues
        test_file = project_path / "test_module.py"
        test_file.write_text("""
# Test module with some code quality issues
import os
import sys

def hello_world( ):  # Space before parentheses
    password = "hardcoded_password_123"  # Security issue
    print("Hello World!")
    return None

class TestClass:
    def __init__(self):
        pass
    
    def method_with_issues(self,x,y):  # Missing spaces
        result=x+y  # Missing spaces around operators  
        return result

if __name__=="__main__":  # Missing spaces around ==
    hello_world()
""")
        
        # Create a requirements.txt with a potentially vulnerable package
        req_file = project_path / "requirements.txt"
        req_file.write_text("""
requests==2.20.0
django==3.0.0  
flask==1.0.0
""")
        
        # Create __init__.py to make it a package
        init_file = project_path / "__init__.py"
        init_file.write_text("")
        
        yield project_path


@pytest.fixture 
def scanner_config():
    """Create a test scanner configuration."""
    return ScanConfig(
        enabled_tools={'ruff'},  # Only test ruff for speed
        parallel_execution=False,  # Disable for consistent testing
        timeout_seconds=30
    )


class TestScanConfig:
    """Test ScanConfig functionality."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = ScanConfig()
        assert 'ruff' in config.enabled_tools
        assert 'mypy' in config.enabled_tools
        assert config.parallel_execution is True
        assert config.timeout_seconds == 300
        assert config.min_severity == 'info'
    
    def test_preset_configs(self):
        """Test preset configuration loading."""
        # Test default preset
        default_config = ScanConfig.get_preset('default')
        assert 'ruff' in default_config.enabled_tools
        assert default_config.auto_fix is False
        
        # Test strict preset
        strict_config = ScanConfig.get_preset('strict')
        assert 'black' in strict_config.enabled_tools
        assert strict_config.min_severity == 'warning'
        
        # Test security preset
        security_config = ScanConfig.get_preset('security')
        assert 'bandit' in security_config.enabled_tools
        assert security_config.include_tests is False
        
        # Test fast preset
        fast_config = ScanConfig.get_preset('fast')
        assert len(fast_config.enabled_tools) <= 2
        assert fast_config.timeout_seconds == 60
    
    def test_invalid_preset(self):
        """Test loading invalid preset raises error."""
        with pytest.raises(ValueError, match="Unknown preset"):
            ScanConfig.get_preset('nonexistent')


class TestCodeScanner:
    """Test CodeScanner functionality."""
    
    @pytest.mark.asyncio
    async def test_scanner_creation(self, scanner_config):
        """Test scanner creation with config."""
        scanner = CodeScanner(scanner_config)
        assert scanner.config == scanner_config
        assert 'ruff' in scanner._tool_executors
    
    @pytest.mark.asyncio
    async def test_scan_project_success(self, temp_python_project, scanner_config):
        """Test successful project scanning."""
        scanner = CodeScanner(scanner_config)
        
        report = await scanner.scan_project(temp_python_project)
        
        assert report is not None
        assert report.project_path == str(temp_python_project)
        assert report.total_issues >= 0
        assert len(report.results) > 0
        
        # Check that ruff ran
        ruff_result = next((r for r in report.results if r.tool == 'ruff'), None)
        assert ruff_result is not None
        assert ruff_result.success is True or len(ruff_result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_scan_nonexistent_project(self, scanner_config):
        """Test scanning non-existent project raises error."""
        scanner = CodeScanner(scanner_config)
        
        with pytest.raises(ValueError, match="Project path does not exist"):
            await scanner.scan_project(Path("/nonexistent/path"))
    
    @pytest.mark.asyncio
    async def test_scan_non_python_project(self, scanner_config):
        """Test scanning non-Python project raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directory (not a Python project)
            project_path = Path(temp_dir)
            
            scanner = CodeScanner(scanner_config)
            
            with pytest.raises(ValueError, match="Not a Python project"):
                await scanner.scan_project(project_path)
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, temp_python_project):
        """Test parallel vs sequential execution."""
        # Test parallel execution
        parallel_config = ScanConfig(
            enabled_tools={'ruff'},
            parallel_execution=True,
            timeout_seconds=30
        )
        parallel_scanner = CodeScanner(parallel_config)
        
        parallel_report = await parallel_scanner.scan_project(temp_python_project)
        
        # Test sequential execution
        sequential_config = ScanConfig(
            enabled_tools={'ruff'},
            parallel_execution=False,
            timeout_seconds=30
        )
        sequential_scanner = CodeScanner(sequential_config)
        
        sequential_report = await sequential_scanner.scan_project(temp_python_project)
        
        # Both should produce results
        assert len(parallel_report.results) > 0
        assert len(sequential_report.results) > 0
        
        # Results should be similar (may not be identical due to timing)
        assert parallel_report.total_issues == sequential_report.total_issues
    
    @pytest.mark.asyncio
    async def test_tool_timeout(self, temp_python_project):
        """Test tool timeout handling."""
        timeout_config = ScanConfig(
            enabled_tools={'ruff'},
            timeout_seconds=0.001  # Very short timeout
        )
        scanner = CodeScanner(timeout_config)
        
        report = await scanner.scan_project(temp_python_project)
        
        # Should handle timeout gracefully
        assert report is not None
        
        # Check if any tools timed out
        for result in report.results:
            if not result.success:
                assert any("timed out" in error.lower() for error in result.errors)


class TestScanResult:
    """Test ScanResult functionality."""
    
    def test_scan_result_creation(self):
        """Test ScanResult creation."""
        result = ScanResult(
            tool='ruff',
            success=True,
            issues=[],
            execution_time=1.5
        )
        
        assert result.tool == 'ruff'
        assert result.success is True
        assert result.issues == []
        assert result.execution_time == 1.5
        assert result.errors == []
        assert result.metadata == {}
    
    def test_scan_result_with_issues(self):
        """Test ScanResult with issues."""
        issues = [
            {
                'file': 'test.py',
                'line': 10,
                'message': 'Missing whitespace',
                'severity': 'warning',
                'rule': 'E225'
            }
        ]
        
        result = ScanResult(
            tool='ruff',
            success=True,
            issues=issues,
            execution_time=2.0
        )
        
        assert len(result.issues) == 1
        assert result.issues[0]['file'] == 'test.py'
        assert result.issues[0]['severity'] == 'warning'


class TestScannerIntegration:
    """Integration tests for the scanner."""
    
    @pytest.mark.asyncio
    async def test_full_scan_workflow(self, temp_python_project):
        """Test complete scanning workflow."""
        # Create scanner with multiple tools
        config = ScanConfig(
            enabled_tools={'ruff'},  # Only ruff for reliable testing
            min_severity='info',
            parallel_execution=True
        )
        
        scanner = CodeScanner(config)
        
        # Run scan
        report = await scanner.scan_project(temp_python_project)
        
        # Validate report structure
        assert hasattr(report, 'project_path')
        assert hasattr(report, 'timestamp')
        assert hasattr(report, 'results')
        assert hasattr(report, 'summary')
        assert hasattr(report, 'total_issues')
        assert hasattr(report, 'fix_suggestions')
        
        # Validate summary
        assert 'tools_run' in report.summary
        assert 'successful_tools' in report.summary
        assert 'execution_time' in report.summary
        
        # Check that we found some issues (the test file has intentional issues)
        if report.total_issues > 0:
            assert any(result.issues for result in report.results)
    
    @pytest.mark.asyncio 
    async def test_empty_project_scan(self):
        """Test scanning empty Python project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create minimal Python project
            init_file = project_path / "__init__.py"
            init_file.write_text("")
            
            config = ScanConfig(enabled_tools={'ruff'})
            scanner = CodeScanner(config)
            
            report = await scanner.scan_project(project_path)
            
            # Should complete successfully with no issues
            assert report.total_issues == 0
            assert len(report.results) > 0
            assert all(result.success for result in report.results)


@pytest.mark.asyncio
async def test_scanner_with_real_project():
    """Test scanner on actual project structure (if available)."""
    # This test can be run against the actual project
    current_dir = Path.cwd()
    
    # Only run if we're in the project directory
    if (current_dir / "src" / "mcp_code_scanner").exists():
        config = ScanConfig(
            enabled_tools={'ruff'},
            timeout_seconds=60
        )
        
        scanner = CodeScanner(config)
        report = await scanner.scan_project(current_dir)
        
        assert report is not None
        assert len(report.results) > 0
        
        # Print summary for debugging
        print(f"\nScan completed:")
        print(f"  Total issues: {report.total_issues}")
        print(f"  Tools run: {report.summary.get('tools_run', 0)}")
        print(f"  Execution time: {report.summary.get('execution_time', 0):.2f}s")


if __name__ == "__main__":
    # Run a simple test
    asyncio.run(test_scanner_with_real_project())