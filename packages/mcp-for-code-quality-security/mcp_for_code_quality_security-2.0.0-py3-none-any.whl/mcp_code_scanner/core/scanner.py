"""
Core code scanner engine that orchestrates various code quality and security tools.
"""

import asyncio
import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml
from pydantic import BaseModel, ConfigDict

from ..utils.file_utils import find_python_files, is_python_project
from ..scanners.fastapi_scanner import FastAPISecurityScanner
from ..scanners.ai_security_scanner import AISecurityScanner
from ..compliance.owasp_mapper import OWASPMapper
from .models import ScanResult, ScanReport


@dataclass
class ScanConfig:
    """Configuration for code scanning operations."""

    # Tool selection
    enabled_tools: Set[str] = field(default_factory=lambda: {
        'ruff', 'mypy', 'bandit', 'safety', 'pylint', 'fastapi_security', 'ai_security'
    })

    # Scan options
    include_tests: bool = True
    auto_fix: bool = False
    safe_fixes_only: bool = True
    max_line_length: int = 88

    # Output options
    output_format: str = 'json'  # json, yaml, text, markdown
    show_source: bool = True
    group_by_file: bool = True

    # Severity filtering
    min_severity: str = 'info'  # info, warning, error, critical
    exclude_rules: Set[str] = field(default_factory=set)

    # Performance
    parallel_execution: bool = True
    timeout_seconds: int = 300

    # Extended configuration (for YAML compatibility)
    tool_configs: Dict[str, Any] = field(default_factory=dict)
    project_structure: Dict[str, Any] = field(default_factory=dict)
    quality_gates: Dict[str, Any] = field(default_factory=dict)
    reporting: Dict[str, Any] = field(default_factory=dict)
    security_checks: Dict[str, Any] = field(default_factory=dict)
    vulnerability_db: Dict[str, Any] = field(default_factory=dict)
    custom_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'ScanConfig':
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Convert enabled_tools list to set
        if 'enabled_tools' in config_data and isinstance(config_data['enabled_tools'], list):
            config_data['enabled_tools'] = set(config_data['enabled_tools'])

        # Convert exclude_rules list to set if present
        if 'exclude_rules' in config_data and isinstance(config_data['exclude_rules'], list):
            config_data['exclude_rules'] = set(config_data['exclude_rules'])

        return cls(**config_data)
    
    @classmethod
    def get_preset(cls, preset_name: str) -> 'ScanConfig':
        """Get a preset configuration by loading from YAML files."""
        # Define available presets and their corresponding config files
        preset_files = {
            'default': 'configs/config_default.yaml',
            'strict': 'configs/config_strict.yaml',
            'security': 'configs/config_security.yaml',
            'fast': 'configs/config_fast.yaml'
        }

        if preset_name not in preset_files:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(preset_files.keys())}")

        # Try to load from YAML file first
        config_path = Path(preset_files[preset_name])
        if config_path.exists():
            return cls.from_file(config_path)

        # Fallback to hard-coded presets if YAML file doesn't exist
        fallback_presets = {
            'default': cls(),
            'strict': cls(
                min_severity='warning',
                auto_fix=False,
                enabled_tools={'ruff', 'mypy', 'bandit', 'safety', 'pylint', 'black', 'isort'}
            ),
            'security': cls(
                enabled_tools={'bandit', 'safety', 'ruff', 'fastapi_security', 'ai_security'},
                min_severity='warning',
                include_tests=False,  # Fix the test expectation
                exclude_rules=set()
            ),
            'fast': cls(
                enabled_tools={'ruff', 'mypy'},
                parallel_execution=True,
                timeout_seconds=60
            )
        }

        return fallback_presets[preset_name]


class CodeScanner:
    """Main code scanner that orchestrates various quality and security tools."""
    
    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.fastapi_scanner = FastAPISecurityScanner()
        self.ai_scanner = AISecurityScanner()
        self.owasp_mapper = OWASPMapper()
        self._tool_executors = {
            'ruff': self._run_ruff,
            'mypy': self._run_mypy,
            'bandit': self._run_bandit,
            'safety': self._run_safety,
            'pylint': self._run_pylint,
            'black': self._run_black,
            'isort': self._run_isort,
            'pytest': self._run_pytest,
            'coverage': self._run_coverage,
            'fastapi_security': self._run_fastapi_security,
            'ai_security': self._run_ai_security,
        }
    
    async def scan_project(self, project_path: Union[str, Path]) -> ScanReport:
        """Scan a Python project for code quality and security issues."""
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        if not is_python_project(project_path):
            raise ValueError(f"Not a Python project: {project_path}")
        
        # Prepare scan report
        from datetime import datetime
        report = ScanReport(
            project_path=str(project_path),
            scan_config=self.config.__class__.__name__,
            timestamp=datetime.now().isoformat()
        )
        
        # Run enabled tools
        if self.config.parallel_execution:
            tasks = []
            for tool in self.config.enabled_tools:
                if tool in self._tool_executors:
                    task = self._run_tool_safe(tool, project_path)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, ScanResult):
                    report.results.append(result)
                elif isinstance(result, Exception):
                    # Log error but continue
                    print(f"Tool execution failed: {result}")
        else:
            # Sequential execution
            for tool in self.config.enabled_tools:
                if tool in self._tool_executors:
                    try:
                        result = await self._run_tool_safe(tool, project_path)
                        report.results.append(result)
                    except Exception as e:
                        print(f"Tool {tool} failed: {e}")
        
        # Generate summary
        report.summary = self._generate_summary(report.results)
        report.total_issues = sum(len(r.issues) for r in report.results)
        report.critical_issues = sum(
            len([i for i in r.issues if i.get('severity') == 'critical'])
            for r in report.results
        )
        report.fix_suggestions = self._generate_fix_suggestions(report.results)
        
        return report
    
    async def _run_tool_safe(self, tool: str, project_path: Path) -> ScanResult:
        """Safely run a tool with timeout and error handling."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await asyncio.wait_for(
                self._tool_executors[tool](project_path),
                timeout=self.config.timeout_seconds
            )
            result.execution_time = asyncio.get_event_loop().time() - start_time
            return result
        except asyncio.TimeoutError:
            return ScanResult(
                tool=tool,
                success=False,
                errors=[f"Tool execution timed out after {self.config.timeout_seconds}s"]
            )
        except Exception as e:
            return ScanResult(
                tool=tool,
                success=False,
                errors=[f"Tool execution failed: {str(e)}"]
            )
    
    async def _run_ruff(self, project_path: Path) -> ScanResult:
        """Run Ruff linter and formatter."""
        cmd = ['ruff', 'check', '--output-format=json', str(project_path)]
        
        if self.config.auto_fix:
            cmd.append('--fix')
        
        try:
            result = await self._run_subprocess(cmd)
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                issues = []
                if result.stdout:
                    try:
                        ruff_output = json.loads(result.stdout)
                        for issue in ruff_output:
                            issues.append({
                                'file': issue.get('filename', ''),
                                'line': issue.get('location', {}).get('row', 0),
                                'column': issue.get('location', {}).get('column', 0),
                                'rule': issue.get('code', ''),
                                'message': issue.get('message', ''),
                                'severity': self._map_ruff_severity(issue.get('code', '')),
                                'source': 'ruff'
                            })
                    except json.JSONDecodeError:
                        pass
                
                return ScanResult(
                    tool='ruff',
                    success=True,
                    issues=issues,
                    metadata={'returncode': result.returncode}
                )
            else:
                return ScanResult(
                    tool='ruff',
                    success=False,
                    errors=[result.stderr or 'Unknown error']
                )
        
        except Exception as e:
            return ScanResult(
                tool='ruff',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_mypy(self, project_path: Path) -> ScanResult:
        """Run MyPy static type checker."""
        cmd = [
            'mypy',
            '--show-error-codes',
            '--show-column-numbers',
            '--output-format=json',
            str(project_path)
        ]
        
        try:
            result = await self._run_subprocess(cmd)
            issues = []
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            issue_data = json.loads(line)
                            issues.append({
                                'file': issue_data.get('file', ''),
                                'line': issue_data.get('line', 0),
                                'column': issue_data.get('column', 0),
                                'rule': issue_data.get('code', ''),
                                'message': issue_data.get('message', ''),
                                'severity': issue_data.get('severity', 'error'),
                                'source': 'mypy'
                            })
                        except json.JSONDecodeError:
                            continue
            
            return ScanResult(
                tool='mypy',
                success=result.returncode == 0,
                issues=issues,
                errors=[result.stderr] if result.stderr else []
            )
        
        except Exception as e:
            return ScanResult(
                tool='mypy',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_bandit(self, project_path: Path) -> ScanResult:
        """Run Bandit security linter."""
        cmd = [
            'bandit',
            '-r',
            '-f', 'json',
            '--exclude', '**/tests/**,**/test/**,**/testing/**,**/__pycache__/**,**/venv/**,**/.venv/**,**/node_modules/**,**/vulnerable_apps/**',
            str(project_path)
        ]
        
        try:
            result = await self._run_subprocess(cmd)
            issues = []
            
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for issue in bandit_output.get('results', []):
                        issues.append({
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'column': 0,
                            'rule': issue.get('test_id', ''),
                            'message': issue.get('issue_text', ''),
                            'severity': issue.get('issue_severity', 'info').lower(),
                            'confidence': issue.get('issue_confidence', 'unknown'),
                            'source': 'bandit'
                        })
                except json.JSONDecodeError:
                    pass
            
            return ScanResult(
                tool='bandit',
                success=True,  # Bandit can return non-zero even with successful scan
                issues=issues,
                metadata={'total_lines_scanned': len(find_python_files(project_path))}
            )
        
        except Exception as e:
            return ScanResult(
                tool='bandit',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_safety(self, project_path: Path) -> ScanResult:
        """Run Safety dependency vulnerability checker."""
        cmd = ['safety', 'check', '--json']
        
        try:
            result = await self._run_subprocess(cmd, cwd=project_path)
            issues = []
            
            if result.stdout:
                try:
                    safety_output = json.loads(result.stdout)

                    # Handle new safety output format (v2.3+)
                    vulnerabilities = []
                    if isinstance(safety_output, dict):
                        # New format with metadata
                        vulnerabilities = safety_output.get('vulnerabilities', [])
                    elif isinstance(safety_output, list):
                        # Old format (direct list)
                        vulnerabilities = safety_output

                    for vuln in vulnerabilities:
                        if isinstance(vuln, dict):
                            issues.append({
                                'file': 'requirements/dependencies',
                                'line': 0,
                                'column': 0,
                                'rule': vuln.get('id', ''),
                                'message': f"Vulnerability in {vuln.get('package_name', 'unknown')}: {vuln.get('advisory', '')}",
                                'severity': 'critical',
                                'source': 'safety',
                                'package': vuln.get('package_name', ''),
                                'vulnerable_spec': vuln.get('vulnerable_spec', ''),
                                'installed_version': vuln.get('installed_version', '')
                            })
                except json.JSONDecodeError:
                    pass
            
            return ScanResult(
                tool='safety',
                success=result.returncode == 0,
                issues=issues
            )
        
        except Exception as e:
            return ScanResult(
                tool='safety',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_pylint(self, project_path: Path) -> ScanResult:
        """Run Pylint comprehensive code analyzer."""
        cmd = [
            'pylint',
            '--output-format=json',
            '--reports=n',
            str(project_path)
        ]
        
        try:
            result = await self._run_subprocess(cmd)
            issues = []
            
            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    for issue in pylint_output:
                        issues.append({
                            'file': issue.get('path', ''),
                            'line': issue.get('line', 0),
                            'column': issue.get('column', 0),
                            'rule': issue.get('message-id', ''),
                            'message': issue.get('message', ''),
                            'severity': issue.get('type', 'info'),
                            'source': 'pylint'
                        })
                except json.JSONDecodeError:
                    pass
            
            return ScanResult(
                tool='pylint',
                success=True,  # Pylint can return non-zero but still provide valid results
                issues=issues
            )
        
        except Exception as e:
            return ScanResult(
                tool='pylint',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_black(self, project_path: Path) -> ScanResult:
        """Run Black code formatter."""
        cmd = ['black', '--check', '--diff', str(project_path)]
        
        if self.config.auto_fix:
            cmd.remove('--check')
            cmd.remove('--diff')
        
        try:
            result = await self._run_subprocess(cmd)
            issues = []
            
            if result.returncode != 0 and '--check' in cmd:
                # Parse diff output to identify files that need formatting
                if result.stdout:
                    lines = result.stdout.split('\n')
                    current_file = None
                    for line in lines:
                        if line.startswith('---') and '.py' in line:
                            current_file = line.split('---')[1].strip()
                        elif line.startswith('+++') and current_file:
                            issues.append({
                                'file': current_file,
                                'line': 0,
                                'column': 0,
                                'rule': 'format',
                                'message': 'File would be reformatted by Black',
                                'severity': 'info',
                                'source': 'black'
                            })
            
            return ScanResult(
                tool='black',
                success=result.returncode == 0,
                issues=issues
            )
        
        except Exception as e:
            return ScanResult(
                tool='black',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_isort(self, project_path: Path) -> ScanResult:
        """Run isort import sorter."""
        cmd = ['isort', '--check-only', '--diff', str(project_path)]
        
        if self.config.auto_fix:
            cmd.remove('--check-only')
            cmd.remove('--diff')
        
        try:
            result = await self._run_subprocess(cmd)
            issues = []
            
            if result.returncode != 0 and '--check-only' in cmd:
                # Parse output to identify files with import issues
                if result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'would reorder imports' in line.lower():
                            file_path = line.split(':')[0] if ':' in line else 'unknown'
                            issues.append({
                                'file': file_path,
                                'line': 0,
                                'column': 0,
                                'rule': 'import-order',
                                'message': 'Imports would be reordered by isort',
                                'severity': 'info',
                                'source': 'isort'
                            })
            
            return ScanResult(
                tool='isort',
                success=result.returncode == 0,
                issues=issues
            )
        
        except Exception as e:
            return ScanResult(
                tool='isort',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_pytest(self, project_path: Path) -> ScanResult:
        """Run pytest test suite."""
        cmd = ['pytest', '--json-report', '--json-report-file=/tmp/pytest-report.json']
        
        try:
            result = await self._run_subprocess(cmd, cwd=project_path)
            issues = []
            
            # Read pytest JSON report
            try:
                with open('/tmp/pytest-report.json', 'r') as f:
                    pytest_data = json.load(f)
                
                for test in pytest_data.get('tests', []):
                    if test.get('outcome') == 'failed':
                        issues.append({
                            'file': test.get('nodeid', '').split('::')[0],
                            'line': 0,
                            'column': 0,
                            'rule': 'test-failure',
                            'message': f"Test failed: {test.get('nodeid', '')}",
                            'severity': 'error',
                            'source': 'pytest'
                        })
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
            return ScanResult(
                tool='pytest',
                success=result.returncode == 0,
                issues=issues,
                metadata={'test_results': pytest_data if 'pytest_data' in locals() else {}}
            )
        
        except Exception as e:
            return ScanResult(
                tool='pytest',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_coverage(self, project_path: Path) -> ScanResult:
        """Run coverage analysis."""
        cmd = ['coverage', 'run', '-m', 'pytest', '&&', 'coverage', 'json']
        
        try:
            # Run coverage with pytest
            result = await self._run_subprocess(
                ['coverage', 'run', '-m', 'pytest'], 
                cwd=project_path
            )
            
            # Generate JSON report
            json_result = await self._run_subprocess(
                ['coverage', 'json'], 
                cwd=project_path
            )
            
            issues = []
            
            # Read coverage report
            coverage_file = project_path / 'coverage.json'
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    
                    if total_coverage < 80:  # Configurable threshold
                        issues.append({
                            'file': 'project',
                            'line': 0,
                            'column': 0,
                            'rule': 'low-coverage',
                            'message': f"Test coverage is {total_coverage:.1f}% (below 80% threshold)",
                            'severity': 'warning',
                            'source': 'coverage'
                        })
                    
                    # Check individual file coverage
                    for file_path, file_data in coverage_data.get('files', {}).items():
                        file_coverage = file_data.get('summary', {}).get('percent_covered', 0)
                        if file_coverage < 70:  # Individual file threshold
                            issues.append({
                                'file': file_path,
                                'line': 0,
                                'column': 0,
                                'rule': 'file-low-coverage',
                                'message': f"File coverage is {file_coverage:.1f}% (below 70% threshold)",
                                'severity': 'info',
                                'source': 'coverage'
                            })
                
                except (json.JSONDecodeError, KeyError):
                    pass
            
            return ScanResult(
                tool='coverage',
                success=result.returncode == 0 and json_result.returncode == 0,
                issues=issues,
                metadata={'coverage_data': coverage_data if 'coverage_data' in locals() else {}}
            )
        
        except Exception as e:
            return ScanResult(
                tool='coverage',
                success=False,
                errors=[str(e)]
            )
    
    async def _run_subprocess(
        self, 
        cmd: List[str], 
        cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Run a subprocess command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode('utf-8', errors='replace') if stdout else '',
            stderr=stderr.decode('utf-8', errors='replace') if stderr else ''
        )
    
    def _map_ruff_severity(self, rule_code: str) -> str:
        """Map Ruff rule codes to severity levels."""
        if rule_code.startswith(('E9', 'F')):
            return 'error'
        elif rule_code.startswith(('E', 'W')):
            return 'warning'
        elif rule_code.startswith('S'):
            return 'critical'
        else:
            return 'info'
    
    def _generate_summary(self, results: List[ScanResult]) -> Dict[str, Any]:
        """Generate a summary of scan results."""
        summary = {
            'tools_run': len(results),
            'successful_tools': sum(1 for r in results if r.success),
            'failed_tools': sum(1 for r in results if not r.success),
            'total_issues': sum(len(r.issues) for r in results),
            'issues_by_severity': {},
            'issues_by_tool': {},
            'execution_time': sum(r.execution_time for r in results)
        }
        
        # Count issues by severity
        severity_counts = {}
        for result in results:
            for issue in result.issues:
                severity = issue.get('severity', 'info')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary['issues_by_severity'] = severity_counts
        
        # Count issues by tool
        for result in results:
            summary['issues_by_tool'][result.tool] = len(result.issues)
        
        return summary
    
    def _generate_fix_suggestions(self, results: List[ScanResult]) -> List[str]:
        """Generate fix suggestions based on scan results."""
        suggestions = []
        
        # Analyze common issues and provide suggestions
        for result in results:
            if result.tool == 'ruff' and result.issues:
                suggestions.append("Run 'ruff --fix' to automatically fix many style issues")
            
            if result.tool == 'black' and result.issues:
                suggestions.append("Run 'black .' to automatically format your code")
            
            if result.tool == 'isort' and result.issues:
                suggestions.append("Run 'isort .' to automatically sort your imports")
            
            if result.tool == 'mypy' and result.issues:
                suggestions.append("Add type hints to resolve MyPy type checking issues")
            
            if result.tool == 'bandit' and result.issues:
                critical_security = [i for i in result.issues if i.get('severity') == 'critical']
                if critical_security:
                    suggestions.append("Review and fix critical security vulnerabilities immediately")
            
            if result.tool == 'safety' and result.issues:
                suggestions.append("Update vulnerable dependencies to secure versions")
        
        return list(set(suggestions))  # Remove duplicates

    async def _run_fastapi_security(self, project_path: Path) -> ScanResult:
        """Run FastAPI security scanner."""
        try:
            return await self.fastapi_scanner.scan_fastapi_project(project_path)
        except Exception as e:
            return ScanResult(
                tool='fastapi_security',
                success=False,
                errors=[str(e)]
            )

    async def _run_ai_security(self, project_path: Path) -> ScanResult:
        """Run AI security scanner."""
        try:
            return await self.ai_scanner.scan_ai_project(project_path)
        except Exception as e:
            return ScanResult(
                tool='ai_security',
                success=False,
                errors=[str(e)]
            )

    def generate_compliance_report(self, scan_report: 'ScanReport', project_name: str = "Unknown Project"):
        """Generate OWASP compliance report from scan results."""
        # Flatten all issues from all scan results
        all_issues = []
        for result in scan_report.results:
            all_issues.extend(result.issues)

        # Generate compliance report
        compliance_report = self.owasp_mapper.map_findings_to_compliance(all_issues, project_name)
        return compliance_report


# Factory function for easy usage
def create_scanner(preset: str = 'default') -> CodeScanner:
    """Create a code scanner with a preset configuration."""
    config = ScanConfig.get_preset(preset)
    return CodeScanner(config)