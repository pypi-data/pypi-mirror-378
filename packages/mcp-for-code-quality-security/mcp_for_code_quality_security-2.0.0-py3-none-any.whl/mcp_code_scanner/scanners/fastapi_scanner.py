"""
FastAPI Security Scanner - Detects security vulnerabilities in FastAPI applications.
"""

import ast
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from ..core.models import ScanResult


@dataclass
class FastAPIVulnerability:
    """Represents a FastAPI-specific security vulnerability."""
    category: str
    owasp_mapping: List[str]
    cwe_id: Optional[str]
    severity: str
    description: str
    remediation: str


class FastAPISecurityScanner:
    """Scanner for FastAPI-specific security vulnerabilities."""

    # Define FastAPI vulnerability patterns
    VULNERABILITIES = {
        "sql_injection": FastAPIVulnerability(
            category="SQL Injection",
            owasp_mapping=["A03:2021 - Injection"],
            cwe_id="CWE-89",
            severity="critical",
            description="SQL injection vulnerability in database queries",
            remediation="Use parameterized queries or ORM methods"
        ),
        "nosql_injection": FastAPIVulnerability(
            category="NoSQL Injection",
            owasp_mapping=["A03:2021 - Injection"],
            cwe_id="CWE-943",
            severity="critical",
            description="NoSQL injection vulnerability",
            remediation="Sanitize and validate user inputs before database queries"
        ),
        "path_traversal": FastAPIVulnerability(
            category="Path Traversal",
            owasp_mapping=["A01:2021 - Broken Access Control"],
            cwe_id="CWE-22",
            severity="high",
            description="Path traversal vulnerability in file operations",
            remediation="Validate and sanitize file paths, use safe path operations"
        ),
        "ssti": FastAPIVulnerability(
            category="Server-Side Template Injection",
            owasp_mapping=["A03:2021 - Injection"],
            cwe_id="CWE-94",
            severity="critical",
            description="Server-side template injection via unsafe template rendering",
            remediation="Use safe template rendering, avoid user input in templates"
        ),
        "weak_crypto": FastAPIVulnerability(
            category="Weak Cryptography",
            owasp_mapping=["A02:2021 - Cryptographic Failures"],
            cwe_id="CWE-327",
            severity="medium",
            description="Weak cryptographic algorithms or practices",
            remediation="Use strong cryptographic algorithms and proper key management"
        ),
        "insecure_cors": FastAPIVulnerability(
            category="Insecure CORS Configuration",
            owasp_mapping=["A05:2021 - Security Misconfiguration"],
            cwe_id="CWE-346",
            severity="medium",
            description="Insecure CORS configuration allowing unauthorized access",
            remediation="Configure CORS with specific origins and methods"
        ),
        "missing_auth": FastAPIVulnerability(
            category="Missing Authentication",
            owasp_mapping=["A07:2021 - Identification and Authentication Failures"],
            cwe_id="CWE-306",
            severity="high",
            description="Endpoints missing authentication requirements",
            remediation="Implement proper authentication for sensitive endpoints"
        ),
        "hardcoded_secrets": FastAPIVulnerability(
            category="Hardcoded Secrets",
            owasp_mapping=["A02:2021 - Cryptographic Failures"],
            cwe_id="CWE-798",
            severity="critical",
            description="Hardcoded secrets or credentials in source code",
            remediation="Use environment variables or secure secret management"
        ),
        "debug_enabled": FastAPIVulnerability(
            category="Debug Mode Enabled",
            owasp_mapping=["A05:2021 - Security Misconfiguration"],
            cwe_id="CWE-489",
            severity="medium",
            description="Debug mode enabled in production",
            remediation="Disable debug mode in production environments"
        ),
        "unsafe_deserialization": FastAPIVulnerability(
            category="Unsafe Deserialization",
            owasp_mapping=["A08:2021 - Software and Data Integrity Failures"],
            cwe_id="CWE-502",
            severity="high",
            description="Unsafe deserialization of user input",
            remediation="Validate and sanitize all user inputs before deserialization"
        )
    }

    def __init__(self):
        self.sql_injection_patterns = [
            r'f["\'].*SELECT.*{.*}.*["\']',  # f-strings with user input
            r'\.execute\(["\'].*\+.*["\']',  # String concatenation in SQL
            r'\.execute\(f["\'].*{.*}.*["\']',  # f-strings in execute
            r'query\s*=.*\+',  # Variable concatenation
            r'WHERE.*=.*["\']["\'].*\+',  # Direct concatenation in WHERE
        ]

        self.nosql_injection_patterns = [
            r'\.find\(\{.*\$.*\}\)',  # MongoDB operators from user input
            r'\.find\(.*request\.',  # Direct request data in find
            r'\.find\(.*user\.',  # User input in find operations
        ]

        self.path_traversal_patterns = [
            r'open\(.*\+',  # File path concatenation
            r'FileResponse\(.*\+',  # Path concatenation in FileResponse
            r'\.\./',  # Directory traversal sequences
            r'os\.path\.join.*request\.',  # Request data in path operations
        ]

        self.ssti_patterns = [
            r'from_string\(.*request\.',  # Jinja2 from_string with user input
            r'Template\(.*request\.',  # Template with user input
            r'render_template_string\(',  # Flask-style template strings
        ]

        self.weak_crypto_patterns = [
            r'hashlib\.md5\(',  # MD5 usage
            r'hashlib\.sha1\(',  # SHA1 usage
            r'\.encode\(\)\.decode\(',  # Base64 for security
            r'random\.randint\(',  # Weak random for security
        ]

        self.hardcoded_secret_patterns = [
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'SECRET_KEY\s*=\s*["\'][^"\']+["\']',
        ]

    async def scan_fastapi_project(self, project_path: Path) -> ScanResult:
        """Scan a FastAPI project for security vulnerabilities."""
        issues = []

        # Find Python files
        python_files = self._find_python_files(project_path)

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Skip if not a FastAPI file
                if not self._is_fastapi_file(content):
                    continue

                # Scan for vulnerabilities
                file_issues = await self._scan_file(file_path, content)
                issues.extend(file_issues)

            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                continue

        return ScanResult(
            tool="fastapi_security",
            success=True,
            issues=issues,
            metadata={
                "files_scanned": len(python_files),
                "fastapi_files": len([f for f in python_files if self._is_fastapi_file_path(f)]),
                "vulnerability_categories": len(set(issue['rule'] for issue in issues))
            }
        )

    def _find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for pattern in ['**/*.py']:
            python_files.extend(project_path.glob(pattern))
        return python_files

    def _is_fastapi_file(self, content: str) -> bool:
        """Check if file contains FastAPI imports/usage."""
        fastapi_indicators = [
            'from fastapi',
            'import fastapi',
            'FastAPI(',
            '@app.get',
            '@app.post',
            '@app.put',
            '@app.delete',
            '@app.patch'
        ]
        return any(indicator in content for indicator in fastapi_indicators)

    def _is_fastapi_file_path(self, file_path: Path) -> bool:
        """Check if file path suggests FastAPI usage."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._is_fastapi_file(f.read())
        except:
            return False

    async def _scan_file(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Scan a single file for vulnerabilities."""
        issues = []

        # Parse AST for more sophisticated analysis
        try:
            tree = ast.parse(content)
            ast_issues = self._analyze_ast(tree, file_path)
            issues.extend(ast_issues)
        except SyntaxError:
            pass  # Skip files with syntax errors

        # Pattern-based analysis
        pattern_issues = self._analyze_patterns(file_path, content)
        issues.extend(pattern_issues)

        return issues

    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze AST for security vulnerabilities."""
        issues = []

        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, scanner, file_path):
                self.scanner = scanner
                self.file_path = file_path
                self.issues = []

            def visit_Call(self, node):
                """Visit function calls to detect vulnerabilities."""
                # SQL injection detection
                if self._is_sql_execute_call(node):
                    if self._has_user_input_concat(node):
                        vuln = self.scanner.VULNERABILITIES["sql_injection"]
                        self.issues.append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'column': node.col_offset,
                            'rule': 'sql_injection',
                            'message': f"{vuln.description}: Potential SQL injection via string concatenation",
                            'severity': vuln.severity,
                            'source': 'fastapi_security',
                            'owasp_mapping': vuln.owasp_mapping,
                            'cwe_id': vuln.cwe_id,
                            'remediation': vuln.remediation
                        })

                # NoSQL injection detection
                if self._is_nosql_call(node):
                    if self._has_user_input(node):
                        vuln = self.scanner.VULNERABILITIES["nosql_injection"]
                        self.issues.append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'column': node.col_offset,
                            'rule': 'nosql_injection',
                            'message': f"{vuln.description}: User input passed to NoSQL query",
                            'severity': vuln.severity,
                            'source': 'fastapi_security',
                            'owasp_mapping': vuln.owasp_mapping,
                            'cwe_id': vuln.cwe_id,
                            'remediation': vuln.remediation
                        })

                # Template injection detection
                if self._is_template_call(node):
                    if self._has_user_input(node):
                        vuln = self.scanner.VULNERABILITIES["ssti"]
                        self.issues.append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'column': node.col_offset,
                            'rule': 'ssti',
                            'message': f"{vuln.description}: User input in template rendering",
                            'severity': vuln.severity,
                            'source': 'fastapi_security',
                            'owasp_mapping': vuln.owasp_mapping,
                            'cwe_id': vuln.cwe_id,
                            'remediation': vuln.remediation
                        })

                # Weak crypto detection
                if self._is_weak_crypto_call(node):
                    vuln = self.scanner.VULNERABILITIES["weak_crypto"]
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'column': node.col_offset,
                        'rule': 'weak_crypto',
                        'message': f"{vuln.description}: Use of weak cryptographic algorithm",
                        'severity': vuln.severity,
                        'source': 'fastapi_security',
                        'owasp_mapping': vuln.owasp_mapping,
                        'cwe_id': vuln.cwe_id,
                        'remediation': vuln.remediation
                    })

                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                """Visit function definitions to check for missing auth."""
                if self._is_fastapi_endpoint(node):
                    if not self._has_authentication(node):
                        vuln = self.scanner.VULNERABILITIES["missing_auth"]
                        self.issues.append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'column': node.col_offset,
                            'rule': 'missing_auth',
                            'message': f"{vuln.description}: Endpoint {node.name} may lack authentication",
                            'severity': vuln.severity,
                            'source': 'fastapi_security',
                            'owasp_mapping': vuln.owasp_mapping,
                            'cwe_id': vuln.cwe_id,
                            'remediation': vuln.remediation
                        })

                self.generic_visit(node)

            def _is_sql_execute_call(self, node):
                """Check if this is a SQL execute call."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr in ['execute', 'executemany']
                return False

            def _is_nosql_call(self, node):
                """Check if this is a NoSQL operation call."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr in ['find', 'find_one', 'insert', 'update', 'delete']
                return False

            def _is_template_call(self, node):
                """Check if this is a template rendering call."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr in ['from_string', 'render_template_string']
                elif isinstance(node.func, ast.Name):
                    return node.func.id in ['Template']
                return False

            def _is_weak_crypto_call(self, node):
                """Check if this uses weak cryptography."""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'hashlib':
                            return node.func.attr in ['md5', 'sha1']
                return False

            def _is_fastapi_endpoint(self, node):
                """Check if function is a FastAPI endpoint."""
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Name):
                            if decorator.value.id == 'app':
                                return decorator.attr in ['get', 'post', 'put', 'delete', 'patch']
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if isinstance(decorator.func.value, ast.Name):
                                if decorator.func.value.id == 'app':
                                    return decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']
                return False

            def _has_authentication(self, node):
                """Check if endpoint has authentication."""
                # Look for Depends() with auth functions
                for arg in node.args.args:
                    if hasattr(arg, 'annotation') and arg.annotation:
                        if isinstance(arg.annotation, ast.Call):
                            if isinstance(arg.annotation.func, ast.Name):
                                if arg.annotation.func.id == 'Depends':
                                    return True
                return False

            def _has_user_input_concat(self, node):
                """Check if call has string concatenation with user input."""
                # Simplified check for f-strings or concatenation
                for arg in node.args:
                    if isinstance(arg, ast.JoinedStr):  # f-string
                        return True
                    elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                        return True
                return False

            def _has_user_input(self, node):
                """Check if call contains user input."""
                # Look for request.* or user.* in arguments
                for arg in node.args:
                    if self._contains_user_reference(arg):
                        return True
                return False

            def _contains_user_reference(self, node):
                """Check if node contains reference to user input."""
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        return node.value.id in ['request', 'user', 'query', 'body']
                elif isinstance(node, ast.Name):
                    return node.id in ['username', 'password', 'query', 'data']
                return False

        visitor = SecurityVisitor(self, file_path)
        visitor.visit(tree)
        return visitor.issues

    def _analyze_patterns(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Analyze file content using regex patterns."""
        issues = []
        lines = content.split('\n')

        # Check each pattern category
        pattern_checks = [
            (self.sql_injection_patterns, 'sql_injection'),
            (self.nosql_injection_patterns, 'nosql_injection'),
            (self.path_traversal_patterns, 'path_traversal'),
            (self.ssti_patterns, 'ssti'),
            (self.weak_crypto_patterns, 'weak_crypto'),
            (self.hardcoded_secret_patterns, 'hardcoded_secrets'),
        ]

        for patterns, vuln_type in pattern_checks:
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vuln = self.VULNERABILITIES[vuln_type]
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'column': 0,
                            'rule': vuln_type,
                            'message': f"{vuln.description}: Pattern detected in line",
                            'severity': vuln.severity,
                            'source': 'fastapi_security',
                            'owasp_mapping': vuln.owasp_mapping,
                            'cwe_id': vuln.cwe_id,
                            'remediation': vuln.remediation,
                            'code_snippet': line.strip()
                        })

        return issues