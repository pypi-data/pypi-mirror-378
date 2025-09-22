"""
Security-related utility functions for code analysis.

This module provides utilities for detecting security issues,
validating file paths, and ensuring safe operation of the scanner.
"""

import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Common patterns for detecting potential security issues
SECURITY_PATTERNS = {
    'hardcoded_passwords': [
        r'(?i)(password|pwd|pass)\s*[=:]\s*["\'][^"\']{3,}["\']',
        r'(?i)(secret|key|token)\s*[=:]\s*["\'][^"\']{10,}["\']',
    ],
    'api_keys': [
        r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']{10,}["\']',
        r'(?i)(access[_-]?token|accesstoken)\s*[=:]\s*["\'][^"\']{10,}["\']',
    ],
    'database_connections': [
        r'(?i)(db|database)[_-]?(url|uri|connection)\s*[=:]\s*["\'].*://.*["\']',
        r'(?i)mongodb://.*',
        r'(?i)mysql://.*',
        r'(?i)postgresql://.*',
    ],
    'sql_injection': [
        r'(?i)execute\s*\(\s*["\'].*%s.*["\']',
        r'(?i)cursor\.execute\s*\(\s*["\'].*\+.*["\']',
        r'(?i)query\s*=\s*["\'].*\+.*["\']',
    ],
    'command_injection': [
        r'(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*input\s*\(',
        r'(?i)eval\s*\(\s*input\s*\(',
        r'(?i)exec\s*\(\s*input\s*\(',
    ],
    'debug_code': [
        r'(?i)debug\s*=\s*true',
        r'(?i)print\s*\(\s*.*password.*\)',
        r'(?i)console\.log\s*\(\s*.*secret.*\)',
    ]
}

# File extensions that should be excluded from security scanning
EXCLUDED_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv',
}

# Directories that should be excluded from security scanning
EXCLUDED_DIRECTORIES = {
    '__pycache__', '.git', '.svn', '.hg',
    'node_modules', '.venv', 'venv', 'env',
    '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'build', 'dist', '.egg-info', '.tox',
    '.coverage', 'htmlcov', '.nyc_output'
}


def is_safe_path(file_path: Path, base_path: Path) -> bool:
    """
    Check if a file path is safe (within base directory and not suspicious).
    
    Args:
        file_path: Path to check
        base_path: Base directory that should contain the file
    
    Returns:
        True if the path is safe
    """
    try:
        # Resolve paths to handle symlinks and relative components
        resolved_file = file_path.resolve()
        resolved_base = base_path.resolve()
        
        # Check if file is within base directory (prevent directory traversal)
        try:
            resolved_file.relative_to(resolved_base)
        except ValueError:
            return False
        
        # Check for suspicious path components
        path_parts = resolved_file.parts
        suspicious_parts = {'..', '.', '~'}
        if any(part in suspicious_parts for part in path_parts):
            return False
        
        # Check file extension
        if resolved_file.suffix.lower() in EXCLUDED_EXTENSIONS:
            return False
        
        # Check directory components
        for part in path_parts:
            if part in EXCLUDED_DIRECTORIES:
                return False
        
        return True
    
    except Exception:
        return False


def validate_project_path(project_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate that a project path is safe to scan.
    
    Args:
        project_path: Path to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not project_path.exists():
            return False, f"Path does not exist: {project_path}"
        
        if not project_path.is_dir():
            return False, f"Path is not a directory: {project_path}"
        
        # Check if path is readable
        if not os.access(project_path, os.R_OK):
            return False, f"Path is not readable: {project_path}"
        
        # Check for suspicious directory names
        resolved_path = project_path.resolve()
        path_str = str(resolved_path).lower()
        
        suspicious_patterns = [
            '/etc/', '/proc/', '/sys/', '/dev/',  # System directories
            'windows/system32', 'program files',  # Windows system
            '/.ssh/', '/.gnupg/',  # Sensitive user directories
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path_str:
                return False, f"Cannot scan system or sensitive directory: {project_path}"
        
        return True, None
    
    except Exception as e:
        return False, f"Error validating path: {e}"


def scan_file_for_secrets(file_path: Path, max_file_size: int = 1024 * 1024) -> List[Dict[str, any]]:
    """
    Scan a file for potential hardcoded secrets and security issues.
    
    Args:
        file_path: Path to the file to scan
        max_file_size: Maximum file size to scan (in bytes)
    
    Returns:
        List of potential security issues found
    """
    issues = []
    
    try:
        # Check file size to avoid scanning very large files
        if file_path.stat().st_size > max_file_size:
            return issues
        
        # Only scan text files
        if not _is_text_file(file_path):
            return issues
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines for some patterns
            if line_stripped.startswith('#') or not line_stripped:
                continue
            
            # Check each security pattern category
            for category, patterns in SECURITY_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'column': match.start() + 1,
                            'category': category,
                            'pattern': pattern,
                            'matched_text': match.group(),
                            'context': line.strip(),
                            'severity': _get_pattern_severity(category),
                            'confidence': _get_pattern_confidence(category, match.group())
                        })
    
    except Exception:
        pass  # Skip files that can't be read
    
    return issues


def _is_text_file(file_path: Path) -> bool:
    """Check if a file is likely a text file."""
    try:
        # Check by extension first
        text_extensions = {
            '.py', '.pyw', '.txt', '.md', '.rst', '.yaml', '.yml',
            '.json', '.xml', '.html', '.htm', '.css', '.js', '.ts',
            '.sql', '.sh', '.bat', '.ps1', '.cfg', '.conf', '.ini',
            '.toml', '.env', '.dockerfile', '.gitignore'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Check file content (read first few bytes)
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            
        # If we can decode as UTF-8 and it's mostly printable, it's likely text
        try:
            decoded = chunk.decode('utf-8')
            printable_chars = sum(1 for c in decoded if c.isprintable() or c.isspace())
            return printable_chars / len(decoded) > 0.7
        except UnicodeDecodeError:
            return False
    
    except Exception:
        return False


def _get_pattern_severity(category: str) -> str:
    """Get severity level for a security pattern category."""
    severity_map = {
        'hardcoded_passwords': 'critical',
        'api_keys': 'critical',
        'database_connections': 'high',
        'sql_injection': 'high',
        'command_injection': 'critical',
        'debug_code': 'medium'
    }
    return severity_map.get(category, 'medium')


def _get_pattern_confidence(category: str, matched_text: str) -> str:
    """Get confidence level for a pattern match."""
    # Higher confidence for longer matches
    if len(matched_text) > 50:
        return 'high'
    elif len(matched_text) > 20:
        return 'medium'
    else:
        return 'low'


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file for integrity checking.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
    
    Returns:
        Hex digest of the file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing potentially dangerous characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    
    # Remove/replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Ensure filename isn't too long
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    # Avoid reserved names on Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if filename.upper().split('.')[0] in reserved_names:
        filename = f"safe_{filename}"
    
    return filename


def check_dependency_vulnerabilities(requirements_file: Path) -> List[Dict[str, str]]:
    """
    Parse requirements file and return list of known vulnerable patterns.
    
    Args:
        requirements_file: Path to requirements.txt or similar
    
    Returns:
        List of potential vulnerability indicators
    """
    vulnerabilities = []
    
    # Known vulnerable packages/versions (this would be updated from a real DB)
    known_issues = {
        'django': ['<3.2.13', '<4.0.4'],
        'pillow': ['<9.1.1'],
        'requests': ['<2.25.1'],
        'pyyaml': ['<5.4.1'],
        'jinja2': ['<2.11.3'],
    }
    
    try:
        if not requirements_file.exists():
            return vulnerabilities
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse requirement line
            # Simple parsing - would use packaging library in real implementation
            if '==' in line:
                package, version = line.split('==', 1)
                package = package.strip()
                version = version.strip()
                
                if package.lower() in known_issues:
                    vulnerabilities.append({
                        'file': str(requirements_file),
                        'line': line_num,
                        'package': package,
                        'version': version,
                        'issue': f'Package {package} version {version} may have known vulnerabilities',
                        'severity': 'medium'
                    })
    
    except Exception:
        pass
    
    return vulnerabilities


def validate_configuration_security(config_dict: Dict) -> List[str]:
    """
    Validate configuration for security issues.
    
    Args:
        config_dict: Configuration dictionary to validate
    
    Returns:
        List of security warnings
    """
    warnings = []
    
    # Check for potentially unsafe auto-fix settings
    if config_dict.get('auto_fix') and not config_dict.get('safe_fixes_only'):
        warnings.append(
            "Auto-fix is enabled without safe_fixes_only - this may introduce security issues"
        )
    
    # Check for overly permissive exclusions
    exclude_patterns = config_dict.get('exclude_patterns', [])
    dangerous_exclusions = ['*.py', '**/*', '*']
    for pattern in exclude_patterns:
        if pattern in dangerous_exclusions:
            warnings.append(
                f"Dangerous exclusion pattern '{pattern}' may skip security-critical files"
            )
    
    # Check timeout settings
    timeout = config_dict.get('timeout_seconds', 0)
    if timeout > 3600:  # 1 hour
        warnings.append(
            f"Very long timeout ({timeout}s) may indicate resource exhaustion risk"
        )
    
    # Check for debug settings in production-like configs
    if config_dict.get('name', '').lower() in ['production', 'prod', 'release']:
        if config_dict.get('debug', False):
            warnings.append("Debug mode should not be enabled in production configuration")
    
    return warnings


def create_security_report(scan_results: List[Dict]) -> Dict[str, any]:
    """
    Create a security-focused report from scan results.
    
    Args:
        scan_results: List of security issues from scanning
    
    Returns:
        Structured security report
    """
    report = {
        'total_issues': len(scan_results),
        'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
        'by_category': {},
        'files_affected': set(),
        'recommendations': []
    }
    
    for issue in scan_results:
        severity = issue.get('severity', 'medium')
        category = issue.get('category', 'unknown')
        file_path = issue.get('file', '')
        
        # Count by severity
        if severity in report['by_severity']:
            report['by_severity'][severity] += 1
        
        # Count by category
        if category not in report['by_category']:
            report['by_category'][category] = 0
        report['by_category'][category] += 1
        
        # Track affected files
        if file_path:
            report['files_affected'].add(file_path)
    
    # Convert set to list for JSON serialization
    report['files_affected'] = list(report['files_affected'])
    
    # Generate recommendations based on findings
    if report['by_severity']['critical'] > 0:
        report['recommendations'].append(
            "Critical security issues found - review and fix immediately"
        )
    
    if 'hardcoded_passwords' in report['by_category']:
        report['recommendations'].append(
            "Remove hardcoded passwords and use environment variables or secure vaults"
        )
    
    if 'api_keys' in report['by_category']:
        report['recommendations'].append(
            "Move API keys to environment variables or configuration files"
        )
    
    if 'sql_injection' in report['by_category']:
        report['recommendations'].append(
            "Use parameterized queries to prevent SQL injection"
        )
    
    if 'command_injection' in report['by_category']:
        report['recommendations'].append(
            "Validate and sanitize all user inputs before executing commands"
        )
    
    return report


def generate_security_checklist(project_path: Path) -> List[str]:
    """
    Generate a security checklist for a Python project.
    
    Args:
        project_path: Path to the project
    
    Returns:
        List of security recommendations
    """
    checklist = [
        "Enable all security-focused linters (bandit, safety)",
        "Keep dependencies up to date and monitor for vulnerabilities",
        "Use environment variables for sensitive configuration",
        "Implement proper input validation and sanitization",
        "Use HTTPS for all external communications",
        "Enable logging and monitoring for security events",
        "Implement proper authentication and authorization",
        "Use parameterized queries for database operations",
        "Validate file uploads and restrict file types",
        "Implement rate limiting and CSRF protection",
    ]
    
    # Add project-specific recommendations
    if (project_path / 'requirements.txt').exists():
        checklist.append("Review requirements.txt for vulnerable packages")
    
    if (project_path / 'setup.py').exists():
        checklist.append("Ensure setup.py doesn't contain sensitive information")
    
    # Check for web frameworks
    python_files = list(project_path.rglob('*.py'))
    frameworks_found = set()
    
    for py_file in python_files[:10]:  # Check first 10 files
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if 'from django' in content or 'import django' in content:
                frameworks_found.add('django')
            elif 'from flask' in content or 'import flask' in content:
                frameworks_found.add('flask')
            elif 'from fastapi' in content or 'import fastapi' in content:
                frameworks_found.add('fastapi')
        except Exception:
            continue
    
    # Add framework-specific recommendations
    if 'django' in frameworks_found:
        checklist.extend([
            "Configure Django security settings (SECURE_SSL_REDIRECT, etc.)",
            "Use Django's built-in CSRF protection",
            "Enable Django security middleware"
        ])
    
    if 'flask' in frameworks_found:
        checklist.extend([
            "Use Flask-WTF for CSRF protection",
            "Configure secure session cookies",
            "Validate all Flask routes and inputs"
        ])
    
    if 'fastapi' in frameworks_found:
        checklist.extend([
            "Use FastAPI security utilities for authentication",
            "Validate all request models with Pydantic",
            "Configure CORS properly if needed"
        ])
    
    return checklist


class SecurityScanner:
    """Security-focused file and project scanner."""
    
    def __init__(self, max_file_size: int = 1024 * 1024):
        self.max_file_size = max_file_size
        self.scanned_files = 0
        self.total_issues = 0
    
    def scan_project(self, project_path: Path) -> Dict[str, any]:
        """
        Perform comprehensive security scan of a project.
        
        Args:
            project_path: Path to the project to scan
        
        Returns:
            Security scan results
        """
        # Validate project path
        is_valid, error_msg = validate_project_path(project_path)
        if not is_valid:
            return {'error': error_msg, 'issues': []}
        
        all_issues = []
        self.scanned_files = 0
        
        # Scan Python files for security issues
        for py_file in project_path.rglob('*.py'):
            if is_safe_path(py_file, project_path):
                issues = scan_file_for_secrets(py_file, self.max_file_size)
                all_issues.extend(issues)
                self.scanned_files += 1
        
        # Check requirements files
        for req_file in ['requirements.txt', 'requirements-dev.txt', 'Pipfile']:
            req_path = project_path / req_file
            if req_path.exists():
                vuln_issues = check_dependency_vulnerabilities(req_path)
                all_issues.extend(vuln_issues)
        
        self.total_issues = len(all_issues)
        
        # Generate security report
        security_report = create_security_report(all_issues)
        security_report['scanned_files'] = self.scanned_files
        security_report['project_path'] = str(project_path)
        security_report['checklist'] = generate_security_checklist(project_path)
        
        return {
            'issues': all_issues,
            'report': security_report,
            'success': True
        }