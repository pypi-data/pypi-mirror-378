"""
Command-line interface for the MCP Code Scanner.

This module provides a CLI for the code quality scanner that can be used
standalone or as part of the MCP server functionality.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.scanner import CodeScanner, ScanConfig
from ..core.reports import ReportGenerator
from ..mcp.server import mcp
from ..scanners.fastapi_scanner import FastAPISecurityScanner
from ..scanners.ai_security_scanner import AISecurityScanner
from ..compliance.owasp_mapper import OWASPMapper
from ..reports import EnterpriseReportGenerator, ReportConfig, CICDGenerator, SARIFGenerator
from ..core.models import ScanResult, ScanReport


console = Console()


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """MCP Code Scanner - Automated code quality and security scanning."""
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--config', '-c',
    type=click.Choice(['default', 'strict', 'security', 'fast']),
    default='default',
    help='Scan configuration preset'
)
@click.option(
    '--tools', '-t',
    multiple=True,
    type=click.Choice(['ruff', 'mypy', 'bandit', 'safety', 'pylint', 'black', 'isort', 'pytest', 'coverage', 'fastapi_security', 'ai_security']),
    help='Specific tools to run (can be used multiple times)'
)
@click.option(
    '--output', '-o',
    type=click.Choice(['json', 'text', 'markdown']),
    default='text',
    help='Output format'
)
@click.option(
    '--output-file', '-f',
    type=click.Path(path_type=Path),
    help='Save output to file'
)
@click.option(
    '--fix/--no-fix',
    default=False,
    help='Automatically fix issues where possible'
)
@click.option(
    '--safe-only/--all-fixes',
    default=True,
    help='Only apply safe fixes that don\'t change behavior'
)
@click.option(
    '--exclude-tests/--include-tests',
    default=False,
    help='Exclude test files from scanning'
)
@click.option(
    '--severity',
    type=click.Choice(['info', 'warning', 'error', 'critical']),
    default='info',
    help='Minimum severity level to report'
)
@click.option('--quiet', '-q', is_flag=True, help='Suppress progress output')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
async def scan(
    project_path: Path,
    config: str,
    tools: List[str],
    output: str,
    output_file: Optional[Path],
    fix: bool,
    safe_only: bool,
    exclude_tests: bool,
    severity: str,
    quiet: bool,
    verbose: bool
):
    """Scan a Python project for code quality and security issues."""
    
    try:
        # Configure scanner
        scan_config = ScanConfig.get_preset(config)
        
        if tools:
            scan_config.enabled_tools = set(tools)
        
        scan_config.auto_fix = fix
        scan_config.safe_fixes_only = safe_only
        scan_config.include_tests = not exclude_tests
        scan_config.min_severity = severity
        scan_config.output_format = output
        
        scanner = CodeScanner(scan_config)
        
        # Show progress if not quiet
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Scanning project...", total=None)
                report = await scanner.scan_project(project_path)
                progress.update(task, description="Scan complete!")
        else:
            report = await scanner.scan_project(project_path)
        
        # Generate output
        if output == 'json':
            output_text = report.model_dump_json(indent=2)
        elif output == 'markdown':
            generator = ReportGenerator()
            output_text = generator.generate_markdown(report)
        else:  # text
            output_text = _format_text_output(report, verbose)
        
        # Save to file or print
        if output_file:
            output_file.write_text(output_text, encoding='utf-8')
            if not quiet:
                console.print(f"✅ Report saved to {output_file}")
        else:
            if output == 'text' and not quiet:
                _display_rich_output(report)
            else:
                console.print(output_text)
        
        # Exit with appropriate code
        if report.critical_issues > 0:
            sys.exit(1)
        elif report.total_issues > 0:
            sys.exit(2)  # Issues found but not critical
        else:
            sys.exit(0)  # No issues
    
    except Exception as e:
        console.print(f"❌ Scan failed: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(3)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option('--safe-only/--all-fixes', default=True, help='Only apply safe fixes')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without making changes')
@click.option('--tools', '-t', multiple=True, help='Specific tools to use for fixing')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
async def fix(
    project_path: Path,
    safe_only: bool,
    dry_run: bool,
    tools: List[str],
    quiet: bool
):
    """Automatically fix code quality issues where possible."""
    try:
        # Configure for auto-fixing
        config = ScanConfig.get_preset("default")
        config.auto_fix = not dry_run
        config.safe_fixes_only = safe_only
        
        if tools:
            config.enabled_tools = set(tools) & config.enabled_tools
        
        scanner = CodeScanner(config)
        
        if not quiet:
            action = "Would fix" if dry_run else "Fixing"
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[progress.description]{action} issues..."),
                console=console
            ) as progress:
                task = progress.add_task("Running auto-fix...", total=None)
                report = await scanner.scan_project(project_path)
        else:
            report = await scanner.scan_project(project_path)
        
        if not quiet:
            if dry_run:
                console.print("🔍 Dry run complete - no changes made")
            else:
                console.print("✅ Auto-fix complete")
            
            console.print(f"Tools used: {', '.join(config.enabled_tools)}")
            console.print(f"Remaining issues: {report.total_issues}")
    
    except Exception as e:
        console.print(f"❌ Fix operation failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option('--include-dependencies/--skip-dependencies', default=True)
@click.option('--severity', type=click.Choice(['info', 'warning', 'error', 'critical']), default='warning')
@click.option('--output', '-o', type=click.Choice(['json', 'text']), default='text')
async def security(
    project_path: Path,
    include_dependencies: bool,
    severity: str,
    output: str
):
    """Perform security-focused scanning."""
    try:
        config = ScanConfig.get_preset("security")
        config.min_severity = severity
        
        if include_dependencies:
            config.enabled_tools.add('safety')
        
        scanner = CodeScanner(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running security scan...", total=None)
            report = await scanner.scan_project(project_path)
        
        # Filter security issues
        security_issues = []
        for result in report.results:
            if result.tool in ['bandit', 'safety']:
                security_issues.extend(result.issues)
        
        if output == 'json':
            console.print(json.dumps({
                "security_issues": security_issues,
                "critical_count": len([i for i in security_issues if i.get('severity') == 'critical']),
                "total_security_issues": len(security_issues)
            }, indent=2))
        else:
            _display_security_results(security_issues)
    
    except Exception as e:
        console.print(f"❌ Security scan failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option('--config', default='default', help='Default scan configuration')
async def serve(config: str):
    """Start the MCP server (stdio communication protocol)."""
    try:
        console.print(f"🚀 Starting MCP Code Scanner server (stdio mode)")
        console.print(f"Default configuration: {config}")
        console.print(f"💡 This server communicates via stdin/stdout for AI assistant integration")

        # Import and run the MCP server
        from ..mcp.server import mcp

        # Run the FastMCP server in stdio mode
        await mcp.run_stdio_async()

    except KeyboardInterrupt:
        console.print("\n👋 Server stopped")
    except Exception as e:
        console.print(f"❌ Server failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
async def info(project_path: Path):
    """Get information about a Python project."""
    try:
        from ..utils.file_utils import find_python_files, is_python_project
        
        path = Path(project_path).resolve()
        python_files = find_python_files(path)
        
        # Project files check
        project_files = {
            "pyproject.toml": (path / "pyproject.toml").exists(),
            "setup.py": (path / "setup.py").exists(),
            "requirements.txt": (path / "requirements.txt").exists(),
            "Pipfile": (path / "Pipfile").exists(),
            "poetry.lock": (path / "poetry.lock").exists(),
        }
        
        # Display info
        table = Table(title=f"Project Information: {path.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Path", str(path))
        table.add_row("Is Python Project", "✅" if is_python_project(path) else "❌")
        table.add_row("Python Files", str(len(python_files)))
        table.add_row("Has pyproject.toml", "✅" if project_files["pyproject.toml"] else "❌")
        table.add_row("Has requirements.txt", "✅" if project_files["requirements.txt"] else "❌")
        
        console.print(table)
        
        # Recommendations
        recommendations = []
        if not project_files["pyproject.toml"] and not project_files["setup.py"]:
            recommendations.append("Consider adding pyproject.toml for modern Python packaging")
        
        if recommendations:
            console.print("\n📋 Recommendations:")
            for rec in recommendations:
                console.print(f"• {rec}")
    
    except Exception as e:
        console.print(f"❌ Failed to get project info: {e}", style="red")


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--report-type', '-t',
    type=click.Choice(['executive', 'technical', 'sarif']),
    default='executive',
    help='Type of enterprise report to generate'
)
@click.option(
    '--company-name', '-c',
    default='Your Organization',
    help='Company name for the report header'
)
@click.option(
    '--output-file', '-o',
    type=click.Path(path_type=Path),
    help='Save report to file'
)
@click.option(
    '--include-compliance/--skip-compliance',
    default=True,
    help='Include OWASP compliance analysis'
)
async def enterprise_report(
    project_path: Path,
    report_type: str,
    company_name: str,
    output_file: Optional[Path],
    include_compliance: bool
):
    """Generate enterprise-grade security reports for stakeholders."""
    try:
        console.print(f"🏢 Generating {report_type} report for {project_path.name}...")

        # Run security scans
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            scan_task = progress.add_task("Running security scans...", total=None)

            fastapi_scanner = FastAPISecurityScanner()
            ai_scanner = AISecurityScanner()

            fastapi_result = await fastapi_scanner.scan_fastapi_project(project_path)
            ai_result = await ai_scanner.scan_ai_project(project_path)

            progress.update(scan_task, description="Generating compliance analysis...")

            # Create scan report
            scan_report = ScanReport(
                project_path=str(project_path),
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

            # Generate OWASP compliance if requested
            compliance_report = None
            if include_compliance:
                owasp_mapper = OWASPMapper()
                all_issues = []
                for result in scan_report.results:
                    all_issues.extend(result.issues)
                compliance_report = owasp_mapper.map_findings_to_compliance(all_issues)

            progress.update(scan_task, description=f"Generating {report_type} report...")

            # Configure and generate report
            report_config = ReportConfig(
                company_name=company_name,
                include_executive_summary=True,
                include_compliance_mapping=include_compliance,
                include_remediation_guide=True
            )

            if report_type == "executive":
                generator = EnterpriseReportGenerator(report_config)
                report_content = generator.generate_executive_report(
                    scan_report, compliance_report, project_path.name
                )
            elif report_type == "technical":
                generator = EnterpriseReportGenerator(report_config)
                report_content = generator.generate_technical_report(
                    scan_report, compliance_report, project_path.name
                )
            elif report_type == "sarif":
                generator = SARIFGenerator()
                report_content = generator.generate_sarif(scan_report, compliance_report)

            progress.update(scan_task, description="Report generation complete!")

        # Save or display report
        if output_file:
            output_file.write_text(report_content, encoding='utf-8')
            console.print(f"✅ {report_type.title()} report saved to {output_file}")
        else:
            if report_type == "sarif":
                # For SARIF, show summary instead of full JSON
                console.print("📄 SARIF Report Generated:")
                console.print(f"Total issues: {len([i for r in scan_report.results for i in r.issues])}")
                if compliance_report:
                    console.print(f"Compliance score: {compliance_report.compliance_score:.1f}%")
            else:
                console.print(report_content)

        # Show summary
        if compliance_report:
            console.print(f"\n📊 Compliance Score: {compliance_report.compliance_score:.1f}%")
            console.print(f"🎯 Total Findings: {compliance_report.total_findings}")

    except Exception as e:
        console.print(f"❌ Enterprise report generation failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--template-type', '-t',
    type=click.Choice(['github', 'gitlab', 'precommit', 'makefile', 'docker', 'all']),
    default='all',
    help='Type of CI/CD template to generate'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    default='./cicd_templates',
    help='Directory to save generated templates'
)
async def cicd_templates(
    project_path: Path,
    template_type: str,
    output_dir: Path
):
    """Generate CI/CD integration templates for enterprise deployment."""
    try:
        console.print(f"🚀 Generating {template_type} CI/CD templates...")

        output_dir.mkdir(exist_ok=True)
        generator = CICDGenerator()
        generated_files = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating templates...", total=None)

            if template_type in ["github", "all"]:
                github_workflow = generator.generate_github_actions_workflow(project_path.name)
                github_file = output_dir / "security_workflow.yml"
                github_file.write_text(github_workflow)
                generated_files.append(("GitHub Actions Workflow", github_file))
                progress.update(task, description="Generated GitHub Actions workflow...")

            if template_type in ["gitlab", "all"]:
                gitlab_pipeline = generator.generate_gitlab_ci_pipeline(project_path.name)
                gitlab_file = output_dir / ".gitlab-ci.yml"
                gitlab_file.write_text(gitlab_pipeline)
                generated_files.append(("GitLab CI Pipeline", gitlab_file))
                progress.update(task, description="Generated GitLab CI pipeline...")

            if template_type in ["precommit", "all"]:
                precommit_config = generator.generate_precommit_hooks(project_path)
                precommit_file = output_dir / ".pre-commit-config.yaml"
                precommit_file.write_text(precommit_config)
                generated_files.append(("Pre-commit Hooks", precommit_file))
                progress.update(task, description="Generated pre-commit hooks...")

            if template_type in ["makefile", "all"]:
                makefile_content = generator.generate_makefile()
                makefile = output_dir / "Makefile"
                makefile.write_text(makefile_content)
                generated_files.append(("Makefile", makefile))
                progress.update(task, description="Generated Makefile...")

            if template_type in ["docker", "all"]:
                docker_content = generator.generate_docker_security_example()
                docker_file = output_dir / "Dockerfile.security"
                docker_file.write_text(docker_content)
                generated_files.append(("Docker Security Example", docker_file))
                progress.update(task, description="Generated Docker security example...")

        # Display results
        console.print(f"✅ Generated {len(generated_files)} CI/CD templates in {output_dir}")

        table = Table(title="Generated Files")
        table.add_column("Template Type", style="cyan")
        table.add_column("File Path", style="green")
        table.add_column("Size", justify="right", style="yellow")

        for template_name, file_path in generated_files:
            size_kb = file_path.stat().st_size / 1024
            table.add_row(template_name, str(file_path), f"{size_kb:.1f} KB")

        console.print(table)

        # Usage instructions
        console.print("\n📋 Quick Start Guide:")
        console.print("• Copy .pre-commit-config.yaml to your project root and run 'pre-commit install'")
        console.print("• Add security_workflow.yml to .github/workflows/ for GitHub Actions")
        console.print("• Use .gitlab-ci.yml for GitLab CI/CD pipeline")
        console.print("• Run 'make security' or 'make ci-full' using the generated Makefile")

    except Exception as e:
        console.print(f"❌ CI/CD template generation failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    default='./security_reports',
    help='Directory to save reports'
)
@click.option(
    '--company-name', '-c',
    default='Security Analysis',
    help='Company name for reports'
)
async def comprehensive_scan(
    project_path: Path,
    output_dir: Path,
    company_name: str
):
    """Perform comprehensive security scan with all professional reports."""
    try:
        console.print(f"🔍 Running comprehensive security scan for {project_path.name}...")

        output_dir.mkdir(exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Run security scans
            scan_task = progress.add_task("Running security scans...", total=None)

            fastapi_scanner = FastAPISecurityScanner()
            ai_scanner = AISecurityScanner()
            owasp_mapper = OWASPMapper()

            fastapi_result = await fastapi_scanner.scan_fastapi_project(project_path)
            ai_result = await ai_scanner.scan_ai_project(project_path)

            progress.update(scan_task, description="Analyzing compliance...")

            # Create comprehensive scan report
            scan_report = ScanReport(
                project_path=str(project_path),
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

            # Generate OWASP compliance
            all_issues = []
            for result in scan_report.results:
                all_issues.extend(result.issues)
            compliance_report = owasp_mapper.map_findings_to_compliance(all_issues)

            progress.update(scan_task, description="Generating executive report...")

            # Generate all reports
            report_config = ReportConfig(company_name=company_name)
            enterprise_generator = EnterpriseReportGenerator(report_config)
            sarif_generator = SARIFGenerator()

            # Executive report
            executive_report = enterprise_generator.generate_executive_report(
                scan_report, compliance_report, project_path.name
            )
            exec_file = output_dir / "executive_summary.md"
            exec_file.write_text(executive_report)

            progress.update(scan_task, description="Generating technical report...")

            # Technical report
            technical_report = enterprise_generator.generate_technical_report(
                scan_report, compliance_report, project_path.name
            )
            tech_file = output_dir / "technical_report.md"
            tech_file.write_text(technical_report)

            progress.update(scan_task, description="Generating SARIF report...")

            # SARIF report
            sarif_report = sarif_generator.generate_sarif(scan_report, compliance_report)
            sarif_file = output_dir / "security_results.sarif"
            sarif_file.write_text(sarif_report)

            progress.update(scan_task, description="Comprehensive scan complete!")

        # Display results
        console.print(f"✅ Comprehensive security scan complete!")
        console.print(f"📂 Reports saved to: {output_dir.absolute()}")

        # Summary panel
        summary = f"""
📊 **Scan Summary**
• Project: {project_path.name}
• Total Issues: {compliance_report.total_findings}
• Compliance Score: {compliance_report.compliance_score:.1f}%
• Critical Issues: {sum(1 for m in compliance_report.mappings if m.remediation_priority <= 2)}

📋 **Framework Scores**
{chr(10).join(f'• {fw.replace("_", " ").title()}: {score:.1f}%' for fw, score in compliance_report.framework_scores.items())}
"""

        console.print(Panel(summary, title="Security Analysis Results", border_style="blue"))

        # Generated files
        files_table = Table(title="Generated Reports")
        files_table.add_column("Report Type", style="cyan")
        files_table.add_column("File", style="green")
        files_table.add_column("Purpose", style="yellow")

        files_table.add_row("Executive Summary", "executive_summary.md", "C-level stakeholders")
        files_table.add_row("Technical Report", "technical_report.md", "Development teams")
        files_table.add_row("SARIF Format", "security_results.sarif", "GitHub Security integration")

        console.print(files_table)

        # Next steps
        console.print("\n🚀 Next Steps:")
        console.print("• Share executive_summary.md with business stakeholders")
        console.print("• Review technical_report.md with development team")
        console.print("• Upload security_results.sarif to GitHub Security tab")
        console.print("• Run 'mcp-scanner cicd-templates' to generate CI/CD integration")

    except Exception as e:
        console.print(f"❌ Comprehensive scan failed: {e}", style="red")
        sys.exit(1)


def _format_text_output(report: ScanReport, verbose: bool = False) -> str:
    """Format scan report as text."""
    lines = []
    lines.append(f"Scan Report for {report.project_path}")
    lines.append("=" * 50)
    lines.append(f"Timestamp: {report.timestamp}")
    lines.append(f"Configuration: {report.scan_config}")
    lines.append(f"Total Issues: {report.total_issues}")
    lines.append(f"Critical Issues: {report.critical_issues}")
    lines.append("")
    
    for result in report.results:
        if result.success and result.issues:
            lines.append(f"{result.tool.upper()} ({len(result.issues)} issues)")
            lines.append("-" * 30)
            
            for issue in result.issues:
                severity = issue.get('severity', 'info').upper()
                file_path = issue.get('file', 'unknown')
                line_no = issue.get('line', 0)
                message = issue.get('message', 'No message')
                
                if verbose:
                    lines.append(f"  [{severity}] {file_path}:{line_no}")
                    lines.append(f"    {message}")
                    lines.append(f"    Rule: {issue.get('rule', 'unknown')}")
                else:
                    lines.append(f"  [{severity}] {file_path}:{line_no} - {message}")
                
                lines.append("")
        elif not result.success:
            lines.append(f"{result.tool.upper()} - FAILED")
            for error in result.errors:
                lines.append(f"  Error: {error}")
            lines.append("")
    
    if report.fix_suggestions:
        lines.append("Fix Suggestions:")
        lines.append("-" * 20)
        for suggestion in report.fix_suggestions:
            lines.append(f"• {suggestion}")
    
    return "\n".join(lines)


def _display_rich_output(report: ScanReport):
    """Display scan report with rich formatting."""
    # Summary panel
    summary_text = f"""
📊 **Scan Summary**
• Total Issues: {report.total_issues}
• Critical Issues: {report.critical_issues}
• Tools Run: {report.summary.get('tools_run', 0)}
• Successful: {report.summary.get('successful_tools', 0)}
• Failed: {report.summary.get('failed_tools', 0)}
"""
    
    console.print(Panel(summary_text, title="Scan Results", border_style="blue"))
    
    # Issues by tool
    if report.results:
        table = Table(title="Issues by Tool")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Issues", justify="right", style="yellow")
        table.add_column("Execution Time", justify="right", style="blue")
        
        for result in report.results:
            status = "✅ Success" if result.success else "❌ Failed"
            exec_time = f"{result.execution_time:.2f}s"
            table.add_row(result.tool, status, str(len(result.issues)), exec_time)
        
        console.print(table)
    
    # Show critical issues
    critical_issues = []
    for result in report.results:
        for issue in result.issues:
            if issue.get('severity') == 'critical':
                critical_issues.append(issue)
    
    if critical_issues:
        console.print("\n🚨 Critical Issues:")
        for issue in critical_issues[:5]:  # Show first 5
            file_path = issue.get('file', 'unknown')
            line_no = issue.get('line', 0)
            message = issue.get('message', 'No message')
            console.print(f"  • {file_path}:{line_no} - {message}", style="red")
        
        if len(critical_issues) > 5:
            console.print(f"  ... and {len(critical_issues) - 5} more")
    
    # Fix suggestions
    if report.fix_suggestions:
        console.print("\n💡 Fix Suggestions:")
        for suggestion in report.fix_suggestions:
            console.print(f"  • {suggestion}", style="green")


def _display_security_results(security_issues: List[Dict]):
    """Display security scan results."""
    if not security_issues:
        console.print("✅ No security issues found!", style="green")
        return
    
    console.print(f"🛡️  Found {len(security_issues)} security issues:", style="yellow")
    
    # Group by severity
    by_severity = {}
    for issue in security_issues:
        severity = issue.get('severity', 'info')
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(issue)
    
    # Display by severity
    severity_order = ['critical', 'high', 'error', 'warning', 'info']
    
    for severity in severity_order:
        if severity in by_severity:
            issues = by_severity[severity]
            console.print(f"\n{severity.upper()} ({len(issues)} issues):", style="red" if severity == 'critical' else "yellow")
            
            for issue in issues[:3]:  # Show first 3 per severity
                file_path = issue.get('file', 'unknown')
                line_no = issue.get('line', 0)
                message = issue.get('message', 'No message')
                console.print(f"  • {file_path}:{line_no}")
                console.print(f"    {message}")
            
            if len(issues) > 3:
                console.print(f"    ... and {len(issues) - 3} more {severity} issues")


def main():
    """Main entry point for the CLI."""
    import asyncio
    
    def run_async_command(coro):
        """Run an async command in the event loop."""
        try:
            asyncio.run(coro)
        except KeyboardInterrupt:
            console.print("\n👋 Operation cancelled")
            sys.exit(130)
    
    # Patch click commands to run async
    for command in cli.commands.values():
        if asyncio.iscoroutinefunction(command.callback):
            original_callback = command.callback
            def make_sync_wrapper(async_func):
                def wrapper(*args, **kwargs):
                    return run_async_command(async_func(*args, **kwargs))
                return wrapper
            command.callback = make_sync_wrapper(original_callback)
    
    cli()


if __name__ == "__main__":
    main()