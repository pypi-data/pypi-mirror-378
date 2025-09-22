"""
Tool integration implementations for various code quality and security tools.

This module provides wrapper classes for integrating external tools like ruff,
mypy, bandit, etc. into the scanning pipeline.
"""

import asyncio
import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .scanner import ScanResult


class ToolExecutor(ABC):
    """Abstract base class for tool executors."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute the tool and return scan results."""
        pass
    
    async def _run_command(
        self, 
        command: List[str], 
        cwd: Optional[Path] = None,
        timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """Run a command asynchronously."""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                args=command,
                returncode=process.returncode,
                stdout=stdout.decode('utf-8', errors='replace') if stdout else '',
                stderr=stderr.decode('utf-8', errors='replace') if stderr else ''
            )
        
        except asyncio.TimeoutError:
            if 'process' in locals():
                process.terminate()
                await process.wait()
            raise
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")


class RuffExecutor(ToolExecutor):
    """Ruff linter and formatter executor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ruff", config)
    
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute Ruff linter."""
        start_time = asyncio.get_event_loop().time()
        
        command = ['ruff', 'check', '--output-format=json', str(project_path)]
        
        # Add auto-fix if configured
        if self.config.get('auto_fix', False):
            command.append('--fix')
        
        try:
            result = await self._run_command(command)
            issues = []
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
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
                                'severity': self._map_severity(issue.get('code', '')),
                                'source': 'ruff',
                                'fixable': issue.get('fix', {}).get('applicability') == 'automatic'
                            })
                    except json.JSONDecodeError:
                        pass
                
                execution_time = asyncio.get_event_loop().time() - start_time
                return ScanResult(
                    tool='ruff',
                    success=True,
                    issues=issues,
                    execution_time=execution_time,
                    metadata={'returncode': result.returncode}
                )
            else:
                execution_time = asyncio.get_event_loop().time() - start_time
                return ScanResult(
                    tool='ruff',
                    success=False,
                    errors=[result.stderr or 'Unknown error'],
                    execution_time=execution_time
                )
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='ruff',
                success=False,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def _map_severity(self, rule_code: str) -> str:
        """Map Ruff rule codes to severity levels."""
        if rule_code.startswith(('E9', 'F')):
            return 'error'
        elif rule_code.startswith(('E', 'W')):
            return 'warning'
        elif rule_code.startswith('S'):
            return 'critical'
        else:
            return 'info'


class MyPyExecutor(ToolExecutor):
    """MyPy static type checker executor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("mypy", config)
    
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute MyPy type checker."""
        start_time = asyncio.get_event_loop().time()
        
        command = [
            'mypy',
            '--show-error-codes',
            '--show-column-numbers',
            '--no-error-summary',
            str(project_path)
        ]
        
        try:
            result = await self._run_command(command)
            issues = []
            
            if result.stderr:
                # Parse MyPy output from stderr
                for line in result.stderr.strip().split('\n'):
                    if line.strip() and ':' in line:
                        # Parse MyPy output format: file:line:column: error: message [code]
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            try:
                                file_path = parts[0].strip()
                                line_no = int(parts[1]) if parts[1].isdigit() else 0
                                column_no = int(parts[2]) if parts[2].isdigit() else 0
                                message = parts[3].strip()
                                
                                # Extract error code if present
                                rule = ''
                                if '[' in message and ']' in message:
                                    start_bracket = message.rfind('[')
                                    end_bracket = message.rfind(']')
                                    if start_bracket < end_bracket:
                                        rule = message[start_bracket+1:end_bracket]
                                        message = message[:start_bracket].strip()
                                
                                issues.append({
                                    'file': file_path,
                                    'line': line_no,
                                    'column': column_no,
                                    'rule': rule,
                                    'message': message,
                                    'severity': 'error' if 'error:' in line else 'warning',
                                    'source': 'mypy'
                                })
                            except (ValueError, IndexError):
                                continue
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='mypy',
                success=result.returncode == 0,
                issues=issues,
                execution_time=execution_time,
                errors=[result.stderr] if result.returncode != 0 and not issues else []
            )
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='mypy',
                success=False,
                errors=[str(e)],
                execution_time=execution_time
            )


class BanditExecutor(ToolExecutor):
    """Bandit security scanner executor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("bandit", config)
    
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute Bandit security scanner."""
        start_time = asyncio.get_event_loop().time()
        
        command = [
            'bandit',
            '-r',
            '-f', 'json',
            str(project_path)
        ]
        
        # Add configuration options
        if 'exclude_dirs' in self.config:
            exclude = ','.join(self.config['exclude_dirs'])
            command.extend(['--exclude', exclude])
        
        if 'confidence' in self.config:
            command.extend(['-i', self.config['confidence']])
        
        if 'severity' in self.config:
            command.extend(['-l', self.config['severity']])
        
        try:
            result = await self._run_command(command)
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
                            'source': 'bandit',
                            'cwe': issue.get('issue_cwe', {}).get('id', ''),
                            'more_info': issue.get('more_info', '')
                        })
                except json.JSONDecodeError:
                    pass
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='bandit',
                success=True,  # Bandit can return non-zero but still provide valid results
                issues=issues,
                execution_time=execution_time,
                metadata={
                    'total_files_scanned': len(list(project_path.rglob('*.py'))),
                    'bandit_version': bandit_output.get('generated_at', '') if 'bandit_output' in locals() else ''
                }
            )
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='bandit',
                success=False,
                errors=[str(e)],
                execution_time=execution_time
            )


class SafetyExecutor(ToolExecutor):
    """Safety dependency vulnerability checker executor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("safety", config)
    
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute Safety dependency checker."""
        start_time = asyncio.get_event_loop().time()
        
        command = ['safety', 'check', '--json']
        
        try:
            result = await self._run_command(command, cwd=project_path)
            issues = []
            
            if result.stdout:
                try:
                    safety_output = json.loads(result.stdout)
                    
                    # Handle both old and new Safety output formats
                    vulnerabilities = []
                    if isinstance(safety_output, list):
                        vulnerabilities = safety_output
                    elif isinstance(safety_output, dict) and 'vulnerabilities' in safety_output:
                        vulnerabilities = safety_output['vulnerabilities']
                    
                    for vuln in vulnerabilities:
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
                            'installed_version': vuln.get('installed_version', ''),
                            'cve': vuln.get('cve', ''),
                            'advisory': vuln.get('advisory', '')
                        })
                except json.JSONDecodeError:
                    # Try to parse text output as fallback
                    if 'vulnerability' in result.stdout.lower():
                        issues.append({
                            'file': 'requirements/dependencies',
                            'line': 0,
                            'column': 0,
                            'rule': 'safety-check',
                            'message': 'Vulnerabilities found in dependencies (see full output)',
                            'severity': 'critical',
                            'source': 'safety'
                        })
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='safety',
                success=result.returncode == 0,
                issues=issues,
                execution_time=execution_time,
                metadata={'safety_db_updated': True}
            )
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='safety',
                success=False,
                errors=[str(e)],
                execution_time=execution_time
            )


class PylintExecutor(ToolExecutor):
    """Pylint comprehensive code analyzer executor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("pylint", config)
    
    async def execute(self, project_path: Path) -> ScanResult:
        """Execute Pylint analyzer."""
        start_time = asyncio.get_event_loop().time()
        
        command = [
            'pylint',
            '--output-format=json',
            '--reports=n',
            str(project_path)
        ]
        
        # Add disable options from config
        if 'disable' in self.config:
            disable_list = ','.join(self.config['disable'])
            command.extend(['--disable', disable_list])
        
        try:
            result = await self._run_command(command)
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
                            'severity': self._map_pylint_type(issue.get('type', 'info')),
                            'source': 'pylint',
                            'symbol': issue.get('symbol', ''),
                            'category': issue.get('type', '')
                        })
                except json.JSONDecodeError:
                    pass
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='pylint',
                success=True,  # Pylint can return non-zero but still provide valid results
                issues=issues,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ScanResult(
                tool='pylint',
                success=False,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def _map_pylint_type(self, pylint_type: str) -> str:
        """Map Pylint message types to severity levels."""
        mapping = {
            'error': 'error',
            'warning': 'warning', 
            'refactor': 'info',
            'convention': 'info',
            'information': 'info'
        }
        return mapping.get(pylint_type.lower(), 'info')


class ToolManager:
    """Manages tool executors and their execution."""
    
    def __init__(self):
        self._executors = {
            'ruff': RuffExecutor,
            'mypy': MyPyExecutor,
            'bandit': BanditExecutor,
            'safety': SafetyExecutor,
            'pylint': PylintExecutor,
        }
    
    def get_executor(self, tool_name: str, config: Dict[str, Any] = None) -> ToolExecutor:
        """Get an executor instance for a tool."""
        if tool_name not in self._executors:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return self._executors[tool_name](config)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return list(self._executors.keys())
    
    async def check_tool_availability(self, tool_name: str) -> bool:
        """Check if a tool is available in the system."""
        try:
            result = await asyncio.create_subprocess_exec(
                tool_name, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            return result.returncode == 0
        except Exception:
            return False
    
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool."""
        if not await self.check_tool_availability(tool_name):
            return {
                'name': tool_name,
                'available': False,
                'version': None,
                'description': f'{tool_name} is not available'
            }
        
        descriptions = {
            'ruff': 'Fast Python linter and formatter written in Rust',
            'mypy': 'Static type checker for Python',
            'bandit': 'Security linter for Python code',
            'safety': 'Dependency vulnerability scanner',
            'pylint': 'Comprehensive Python code analyzer'
        }
        
        # Try to get version
        version = None
        try:
            result = await asyncio.create_subprocess_exec(
                tool_name, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            if stdout:
                version = stdout.decode('utf-8').strip()
        except Exception:
            pass
        
        return {
            'name': tool_name,
            'available': True,
            'version': version,
            'description': descriptions.get(tool_name, f'{tool_name} code analysis tool')
        }