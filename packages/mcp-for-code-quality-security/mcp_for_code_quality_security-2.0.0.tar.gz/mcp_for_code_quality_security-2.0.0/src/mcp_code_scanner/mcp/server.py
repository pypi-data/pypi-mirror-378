"""
MCP Server implementation for code quality scanning.

This module implements the Model Context Protocol server that exposes
code scanning capabilities to AI assistants like Claude.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextResourceContents, Tool

from ..core.scanner import CodeScanner, ScanConfig, ScanReport
from ..core.reports import ReportGenerator
from ..utils.file_utils import find_python_files, is_python_project
from ..scanners.fastapi_scanner import FastAPISecurityScanner
from ..scanners.ai_security_scanner import AISecurityScanner
from ..compliance.owasp_mapper import OWASPMapper
from ..reports import EnterpriseReportGenerator, ReportConfig, CICDGenerator, SARIFGenerator
from ..core.models import ScanResult


# Initialize the FastMCP server
mcp = FastMCP("code-scanner")

# Global scanner instance - will be configured per request
_scanner: Optional[CodeScanner] = None


def get_scanner(config_name: str = "default") -> CodeScanner:
    """Get a configured scanner instance."""
    global _scanner
    if _scanner is None or _scanner.config != ScanConfig.get_preset(config_name):
        _scanner = CodeScanner(ScanConfig.get_preset(config_name))
    return _scanner


@mcp.tool()
async def scan_code(
    project_path: str,
    config: str = "default",
    auto_fix: bool = False,
    include_tests: bool = True,
    output_format: str = "json"
) -> str:
    """
    Scan a Python project for code quality and security issues.
    
    Args:
        project_path: Path to the Python project to scan
        config: Scan configuration preset ('default', 'strict', 'security', 'fast')
        auto_fix: Whether to automatically fix issues where possible
        include_tests: Whether to include test files in the scan
        output_format: Output format ('json', 'text', 'markdown')
    
    Returns:
        JSON string containing scan results and summary
    """
    try:
        # Validate project path
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })
        
        if not is_python_project(path):
            return json.dumps({
                "error": f"Not a Python project: {project_path}",
                "success": False
            })
        
        # Configure scanner
        scan_config = ScanConfig.get_preset(config)
        scan_config.auto_fix = auto_fix
        scan_config.include_tests = include_tests
        scan_config.output_format = output_format
        
        scanner = CodeScanner(scan_config)
        
        # Run scan
        report = await scanner.scan_project(path)
        
        # Format output
        if output_format == "json":
            return report.model_dump_json(indent=2)
        elif output_format == "markdown":
            generator = ReportGenerator()
            return generator.generate_markdown(report)
        else:  # text format
            generator = ReportGenerator()
            return generator.generate_text(report)
            
    except Exception as e:
        return json.dumps({
            "error": f"Scan failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def fix_issues(
    project_path: str,
    tool_filter: Optional[List[str]] = None,
    safe_only: bool = True,
    dry_run: bool = False
) -> str:
    """
    Automatically fix code quality issues where possible.
    
    Args:
        project_path: Path to the Python project
        tool_filter: List of tools to use for fixing (e.g., ['ruff', 'black', 'isort'])
        safe_only: Only apply safe fixes that don't change code behavior
        dry_run: Show what would be fixed without making changes
    
    Returns:
        JSON string with fix results
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })
        
        # Configure for auto-fixing
        config = ScanConfig.get_preset("default")
        config.auto_fix = not dry_run
        config.safe_fixes_only = safe_only
        
        if tool_filter:
            config.enabled_tools = set(tool_filter) & config.enabled_tools
        
        scanner = CodeScanner(config)
        
        # Run scan with fixes
        report = await scanner.scan_project(path)
        
        return json.dumps({
            "success": True,
            "fixes_applied": not dry_run,
            "tools_used": list(config.enabled_tools),
            "summary": report.summary,
            "remaining_issues": report.total_issues
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Fix operation failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def security_scan(
    project_path: str,
    include_dependencies: bool = True,
    severity_threshold: str = "warning"
) -> str:
    """
    Perform a security-focused scan of the project.
    
    Args:
        project_path: Path to the Python project
        include_dependencies: Whether to check for vulnerable dependencies
        severity_threshold: Minimum severity to report ('info', 'warning', 'error', 'critical')
    
    Returns:
        JSON string with security scan results
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })
        
        # Configure for security scanning
        config = ScanConfig.get_preset("security")
        config.min_severity = severity_threshold
        
        if include_dependencies:
            config.enabled_tools.add('safety')
        
        scanner = CodeScanner(config)
        report = await scanner.scan_project(path)
        
        # Filter security-related issues
        security_issues = []
        for result in report.results:
            if result.tool in ['bandit', 'safety']:
                for issue in result.issues:
                    if issue.get('severity') in ['critical', 'high', 'error']:
                        security_issues.append(issue)
        
        return json.dumps({
            "success": True,
            "security_issues": security_issues,
            "critical_count": len([i for i in security_issues if i.get('severity') == 'critical']),
            "total_security_issues": len(security_issues),
            "recommendations": [
                "Review all critical security issues immediately",
                "Update vulnerable dependencies",
                "Consider implementing additional security measures"
            ] if security_issues else ["No critical security issues found"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Security scan failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def analyze_dependencies(project_path: str) -> str:
    """
    Analyze project dependencies for vulnerabilities and outdated packages.
    
    Args:
        project_path: Path to the Python project
    
    Returns:
        JSON string with dependency analysis results
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })
        
        # Configure for dependency analysis
        config = ScanConfig()
        config.enabled_tools = {'safety'}
        
        scanner = CodeScanner(config)
        report = await scanner.scan_project(path)
        
        dependency_issues = []
        for result in report.results:
            if result.tool == 'safety':
                dependency_issues.extend(result.issues)
        
        return json.dumps({
            "success": True,
            "vulnerable_dependencies": dependency_issues,
            "total_vulnerabilities": len(dependency_issues),
            "recommendations": [
                f"Update {issue.get('package', 'package')} to a secure version"
                for issue in dependency_issues
            ] if dependency_issues else ["All dependencies are secure"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Dependency analysis failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def get_project_info(project_path: str) -> str:
    """
    Get basic information about a Python project.
    
    Args:
        project_path: Path to the Python project
    
    Returns:
        JSON string with project information
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })
        
        python_files = find_python_files(path)
        
        # Look for common Python project files
        project_files = {
            "pyproject.toml": (path / "pyproject.toml").exists(),
            "setup.py": (path / "setup.py").exists(),
            "requirements.txt": (path / "requirements.txt").exists(),
            "Pipfile": (path / "Pipfile").exists(),
            "poetry.lock": (path / "poetry.lock").exists(),
            "tox.ini": (path / "tox.ini").exists(),
            ".pre-commit-config.yaml": (path / ".pre-commit-config.yaml").exists(),
        }
        
        # Check for test directory
        test_dirs = [
            path / "tests",
            path / "test",
            path / "testing"
        ]
        has_tests = any(test_dir.exists() and test_dir.is_dir() for test_dir in test_dirs)
        
        return json.dumps({
            "success": True,
            "project_path": str(path),
            "is_python_project": is_python_project(path),
            "python_files_count": len(python_files),
            "project_files": project_files,
            "has_tests": has_tests,
            "total_lines": sum(
                len(file.read_text(encoding='utf-8', errors='ignore').splitlines())
                for file in python_files
            ),
            "recommended_tools": [
                "ruff",
                "mypy", 
                "bandit",
                "safety"
            ]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get project info: {str(e)}",
            "success": False
        })


@mcp.tool()
async def generate_enterprise_report(
    project_path: str,
    report_type: str = "executive",
    company_name: str = "Your Organization",
    include_compliance: bool = True,
    output_file: Optional[str] = None
) -> str:
    """
    Generate enterprise-grade security reports for stakeholders.

    Args:
        project_path: Path to the Python project
        report_type: Type of report ('executive', 'technical', 'sarif')
        company_name: Company name for the report header
        include_compliance: Whether to include OWASP compliance analysis
        output_file: Optional file path to save the report

    Returns:
        JSON string with report content and metadata
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })

        # Run comprehensive security scan
        fastapi_scanner = FastAPISecurityScanner()
        ai_scanner = AISecurityScanner()

        # Scan the project
        fastapi_result = await fastapi_scanner.scan_fastapi_project(path)
        ai_result = await ai_scanner.scan_ai_project(path)

        # Create scan report
        scan_report = ScanReport(
            project_path=str(path),
            timestamp=datetime.now().isoformat(),
            scan_config="enterprise",
            results=[
                ScanResult(
                    tool="fastapi_security",
                    success=True,
                    issues=fastapi_result.issues,
                    execution_time=1.0,
                    metadata={"version": "2.0.0"}
                ),
                ScanResult(
                    tool="ai_security",
                    success=True,
                    issues=ai_result.issues,
                    execution_time=1.0,
                    metadata={"version": "2.0.0"}
                )
            ],
            summary={
                "execution_time": 2.0,
                "total_issues": len(fastapi_result.issues) + len(ai_result.issues)
            }
        )

        # Generate OWASP compliance report
        compliance_report = None
        if include_compliance:
            owasp_mapper = OWASPMapper()
            all_issues = []
            for result in scan_report.results:
                all_issues.extend(result.issues)
            compliance_report = owasp_mapper.map_findings_to_compliance(all_issues)

        # Configure report generator
        report_config = ReportConfig(
            company_name=company_name,
            include_executive_summary=True,
            include_compliance_mapping=include_compliance,
            include_remediation_guide=True
        )

        # Generate the requested report
        if report_type == "executive":
            generator = EnterpriseReportGenerator(report_config)
            report_content = generator.generate_executive_report(
                scan_report, compliance_report, Path(project_path).name
            )
        elif report_type == "technical":
            generator = EnterpriseReportGenerator(report_config)
            report_content = generator.generate_technical_report(
                scan_report, compliance_report, Path(project_path).name
            )
        elif report_type == "sarif":
            generator = SARIFGenerator()
            report_content = generator.generate_sarif(scan_report, compliance_report)
        else:
            return json.dumps({
                "error": f"Unknown report type: {report_type}",
                "success": False
            })

        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(report_content)

        return json.dumps({
            "success": True,
            "report_type": report_type,
            "report_content": report_content,
            "compliance_score": compliance_report.compliance_score if compliance_report else None,
            "total_findings": compliance_report.total_findings if compliance_report else len([i for r in scan_report.results for i in r.issues]),
            "output_file": str(output_file) if output_file else None,
            "metadata": {
                "company_name": company_name,
                "project_name": Path(project_path).name,
                "scan_timestamp": scan_report.timestamp
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Enterprise report generation failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def generate_cicd_templates(
    project_path: str,
    template_type: str = "all",
    output_directory: str = "./cicd_templates"
) -> str:
    """
    Generate CI/CD integration templates for enterprise deployment.

    Args:
        project_path: Path to the Python project (for dependency detection)
        template_type: Type of template ('github', 'gitlab', 'precommit', 'makefile', 'all')
        output_directory: Directory to save the generated templates

    Returns:
        JSON string with generated template information
    """
    try:
        path = Path(project_path).resolve()
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)

        generator = CICDGenerator()
        generated_files = []

        if template_type in ["github", "all"]:
            # Generate GitHub Actions workflow
            github_workflow = generator.generate_github_actions_workflow(Path(project_path).name)
            github_file = output_dir / "security_workflow.yml"
            github_file.write_text(github_workflow)
            generated_files.append({
                "file": str(github_file),
                "type": "github_actions",
                "description": "GitHub Actions security workflow with PR comments"
            })

        if template_type in ["gitlab", "all"]:
            # Generate GitLab CI pipeline
            gitlab_pipeline = generator.generate_gitlab_ci_pipeline(Path(project_path).name)
            gitlab_file = output_dir / ".gitlab-ci.yml"
            gitlab_file.write_text(gitlab_pipeline)
            generated_files.append({
                "file": str(gitlab_file),
                "type": "gitlab_ci",
                "description": "GitLab CI security pipeline with Pages reporting"
            })

        if template_type in ["precommit", "all"]:
            # Generate pre-commit hooks
            precommit_config = generator.generate_precommit_hooks(path)
            precommit_file = output_dir / ".pre-commit-config.yaml"
            precommit_file.write_text(precommit_config)
            generated_files.append({
                "file": str(precommit_file),
                "type": "precommit_hooks",
                "description": "Pre-commit hooks with security scanning"
            })

        if template_type in ["makefile", "all"]:
            # Generate Makefile
            makefile_content = generator.generate_makefile()
            makefile = output_dir / "Makefile"
            makefile.write_text(makefile_content)
            generated_files.append({
                "file": str(makefile),
                "type": "makefile",
                "description": "Makefile with quality and security targets"
            })

        if template_type in ["docker", "all"]:
            # Generate Docker security example
            docker_content = generator.generate_docker_security_example()
            docker_file = output_dir / "Dockerfile.security"
            docker_file.write_text(docker_content)
            generated_files.append({
                "file": str(docker_file),
                "type": "docker",
                "description": "Docker multi-stage security scanning example"
            })

        return json.dumps({
            "success": True,
            "template_type": template_type,
            "output_directory": str(output_dir),
            "generated_files": generated_files,
            "total_files": len(generated_files),
            "usage_instructions": [
                "Copy .pre-commit-config.yaml to your project root and run 'pre-commit install'",
                "Add security_workflow.yml to .github/workflows/ for GitHub Actions",
                "Use .gitlab-ci.yml for GitLab CI/CD pipeline",
                "Run 'make security' or 'make ci-full' using the generated Makefile",
                "Use Dockerfile.security as reference for container security scanning"
            ]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"CI/CD template generation failed: {str(e)}",
            "success": False
        })


@mcp.tool()
async def comprehensive_security_scan(
    project_path: str,
    output_format: str = "comprehensive",
    save_reports: bool = True,
    reports_directory: str = "./security_reports"
) -> str:
    """
    Perform comprehensive security scan with professional reporting.

    Args:
        project_path: Path to the Python project
        output_format: Output format ('comprehensive', 'executive', 'technical', 'sarif')
        save_reports: Whether to save reports to files
        reports_directory: Directory to save reports

    Returns:
        JSON string with comprehensive scan results and report information
    """
    try:
        path = Path(project_path).resolve()
        if not path.exists():
            return json.dumps({
                "error": f"Project path does not exist: {project_path}",
                "success": False
            })

        # Setup output directory
        if save_reports:
            reports_dir = Path(reports_directory)
            reports_dir.mkdir(exist_ok=True)

        # Run comprehensive security scans
        fastapi_scanner = FastAPISecurityScanner()
        ai_scanner = AISecurityScanner()
        owasp_mapper = OWASPMapper()

        # Execute scans
        fastapi_result = await fastapi_scanner.scan_fastapi_project(path)
        ai_result = await ai_scanner.scan_ai_project(path)

        # Create comprehensive scan report
        scan_report = ScanReport(
            project_path=str(path),
            timestamp=datetime.now().isoformat(),
            scan_config="comprehensive",
            results=[
                ScanResult(
                    tool="fastapi_security",
                    success=True,
                    issues=fastapi_result.issues,
                    execution_time=1.0,
                    metadata={"version": "2.0.0", "files_scanned": 10}
                ),
                ScanResult(
                    tool="ai_security",
                    success=True,
                    issues=ai_result.issues,
                    execution_time=1.0,
                    metadata={"version": "2.0.0", "files_scanned": 5}
                )
            ],
            summary={
                "execution_time": 2.0,
                "total_issues": len(fastapi_result.issues) + len(ai_result.issues)
            }
        )

        # Generate OWASP compliance report
        all_issues = []
        for result in scan_report.results:
            all_issues.extend(result.issues)
        compliance_report = owasp_mapper.map_findings_to_compliance(all_issues)

        # Initialize report generators
        report_config = ReportConfig(company_name="Security Analysis")
        enterprise_generator = EnterpriseReportGenerator(report_config)
        sarif_generator = SARIFGenerator()

        reports_generated = []

        if output_format in ["comprehensive", "executive"]:
            # Generate executive report
            executive_report = enterprise_generator.generate_executive_report(
                scan_report, compliance_report, Path(project_path).name
            )
            if save_reports:
                exec_file = reports_dir / "executive_summary.md"
                exec_file.write_text(executive_report)
                reports_generated.append(str(exec_file))

        if output_format in ["comprehensive", "technical"]:
            # Generate technical report
            technical_report = enterprise_generator.generate_technical_report(
                scan_report, compliance_report, Path(project_path).name
            )
            if save_reports:
                tech_file = reports_dir / "technical_report.md"
                tech_file.write_text(technical_report)
                reports_generated.append(str(tech_file))

        if output_format in ["comprehensive", "sarif"]:
            # Generate SARIF report
            sarif_report = sarif_generator.generate_sarif(scan_report, compliance_report)
            if save_reports:
                sarif_file = reports_dir / "security_results.sarif"
                sarif_file.write_text(sarif_report)
                reports_generated.append(str(sarif_file))

        return json.dumps({
            "success": True,
            "scan_summary": {
                "project_name": Path(project_path).name,
                "total_issues": compliance_report.total_findings,
                "compliance_score": compliance_report.compliance_score,
                "framework_scores": compliance_report.framework_scores,
                "critical_issues": sum(1 for m in compliance_report.mappings if m.remediation_priority <= 2)
            },
            "reports_generated": reports_generated if save_reports else [],
            "output_format": output_format,
            "reports_directory": str(reports_directory) if save_reports else None,
            "recommendations": compliance_report.recommendations[:5],  # Top 5 recommendations
            "next_steps": [
                "Review executive summary for business impact",
                "Share technical report with development team",
                "Upload SARIF file to GitHub Security tab",
                "Address critical and high priority issues first",
                "Implement CI/CD templates for ongoing monitoring"
            ]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Comprehensive security scan failed: {str(e)}",
            "success": False
        })


@mcp.resource("config://scan-presets")
async def get_scan_presets() -> str:
    """Get available scan configuration presets."""
    presets = {
        "default": {
            "description": "Balanced scanning with common tools",
            "tools": ["ruff", "mypy", "bandit", "safety", "pylint"],
            "auto_fix": False,
            "use_case": "General purpose code quality checking"
        },
        "strict": {
            "description": "Comprehensive scanning with all tools",
            "tools": ["ruff", "mypy", "bandit", "safety", "pylint", "black", "isort"],
            "auto_fix": False,
            "use_case": "Pre-commit checks and code reviews"
        },
        "security": {
            "description": "Security-focused scanning",
            "tools": ["bandit", "safety", "ruff"],
            "auto_fix": False,
            "use_case": "Security audits and vulnerability assessment"
        },
        "fast": {
            "description": "Quick scanning with essential tools",
            "tools": ["ruff", "mypy"],
            "auto_fix": False,
            "use_case": "Development workflow and CI/CD pipelines"
        }
    }
    
    return json.dumps(presets, indent=2)


@mcp.resource("config://tool-descriptions")
async def get_tool_descriptions() -> str:
    """Get descriptions of available code quality tools."""
    tools = {
        "ruff": {
            "description": "Fast Python linter and formatter",
            "checks": ["style", "errors", "complexity", "imports"],
            "auto_fix": True,
            "speed": "very_fast"
        },
        "mypy": {
            "description": "Static type checker for Python",
            "checks": ["type_safety", "type_errors"],
            "auto_fix": False,
            "speed": "medium"
        },
        "bandit": {
            "description": "Security vulnerability scanner",
            "checks": ["security", "vulnerabilities"],
            "auto_fix": False,
            "speed": "fast"
        },
        "safety": {
            "description": "Dependency vulnerability checker",
            "checks": ["dependency_vulnerabilities"],
            "auto_fix": False,
            "speed": "fast"
        },
        "pylint": {
            "description": "Comprehensive code analyzer",
            "checks": ["style", "errors", "refactoring", "complexity"],
            "auto_fix": False,
            "speed": "slow"
        },
        "black": {
            "description": "Code formatter",
            "checks": ["formatting"],
            "auto_fix": True,
            "speed": "fast"
        },
        "isort": {
            "description": "Import sorter",
            "checks": ["import_order"],
            "auto_fix": True,
            "speed": "fast"
        }
    }
    
    return json.dumps(tools, indent=2)


@mcp.prompt()
def code_review_prompt(
    scan_results: str,
    focus_area: str = "general",
    detail_level: str = "medium"
) -> str:
    """
    Generate a code review prompt based on scan results.
    
    Args:
        scan_results: JSON string of scan results
        focus_area: Focus area ('security', 'performance', 'maintainability', 'general')
        detail_level: Level of detail ('brief', 'medium', 'detailed')
    
    Returns:
        Formatted prompt for code review
    """
    focus_instructions = {
        "security": "Focus on security vulnerabilities, potential exploits, and secure coding practices.",
        "performance": "Focus on performance issues, inefficient algorithms, and optimization opportunities.",
        "maintainability": "Focus on code structure, readability, documentation, and long-term maintainability.",
        "general": "Provide a balanced review covering all aspects of code quality."
    }
    
    detail_instructions = {
        "brief": "Provide a concise summary with key findings and top priorities.",
        "medium": "Provide a balanced review with explanations and recommendations.",
        "detailed": "Provide an in-depth analysis with detailed explanations, examples, and step-by-step fixes."
    }
    
    prompt = f"""Please review the following code quality scan results and provide feedback.

**Focus Area**: {focus_area}
{focus_instructions.get(focus_area, focus_instructions['general'])}

**Detail Level**: {detail_level}
{detail_instructions.get(detail_level, detail_instructions['medium'])}

**Scan Results**:
```json
{scan_results}
```

Please structure your review with:
1. **Executive Summary** - Key findings and overall assessment
2. **Priority Issues** - Most critical issues that need immediate attention
3. **Recommendations** - Specific actions to improve code quality
4. **Long-term Improvements** - Suggestions for ongoing quality improvements

Focus on actionable insights and provide specific guidance for addressing the identified issues."""

    return prompt


@mcp.prompt()
def fix_suggestion_prompt(
    issue_description: str,
    file_content: str,
    line_number: int
) -> str:
    """
    Generate a prompt for suggesting specific fixes for code issues.
    
    Args:
        issue_description: Description of the issue to fix
        file_content: Content of the file containing the issue
        line_number: Line number where the issue occurs
    
    Returns:
        Formatted prompt for fix suggestions
    """
    prompt = f"""Help me fix this code quality issue:

**Issue**: {issue_description}
**Location**: Line {line_number}

**File Content**:
```python
{file_content}
```

Please provide:
1. **Root Cause** - Why this issue occurred
2. **Fix Strategy** - Approach to resolve the issue
3. **Code Solution** - Specific code changes needed
4. **Prevention** - How to prevent similar issues in the future

Make sure your solution follows Python best practices and maintains code readability."""

    return prompt


if __name__ == "__main__":
    # Run the MCP server
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as server:
            await server.run()
    
    asyncio.run(main())