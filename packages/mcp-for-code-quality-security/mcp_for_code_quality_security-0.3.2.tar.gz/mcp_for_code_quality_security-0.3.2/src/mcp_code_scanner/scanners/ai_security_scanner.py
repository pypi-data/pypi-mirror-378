"""
AI Security Scanner - Detects security vulnerabilities in AI/ML applications.
"""

import ast
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from ..core.models import ScanResult


@dataclass
class AISecurityVulnerability:
    """Represents an AI/ML-specific security vulnerability."""
    category: str
    ai_framework: str
    owasp_llm_mapping: List[str]
    impact: str
    detection_method: str
    severity: str
    description: str
    remediation: str


class AISecurityScanner:
    """Scanner for AI/ML security vulnerabilities."""

    # Define AI security vulnerability patterns
    VULNERABILITIES = {
        "prompt_injection": AISecurityVulnerability(
            category="Prompt Injection",
            ai_framework="llm_serving",
            owasp_llm_mapping=["LLM01: Prompt Injection"],
            impact="Model behavior manipulation",
            detection_method="Pattern analysis of input validation",
            severity="critical",
            description="Prompt injection vulnerability allowing model behavior manipulation",
            remediation="Implement input validation, prompt sanitization, and output filtering"
        ),
        "model_extraction": AISecurityVulnerability(
            category="Model Extraction",
            ai_framework="model_serving",
            owasp_llm_mapping=["LLM04: Model Denial of Service"],
            impact="Intellectual property theft",
            detection_method="API endpoint analysis for model exposure",
            severity="high",
            description="Model extraction vulnerability through API endpoints",
            remediation="Implement rate limiting, query monitoring, and model access controls"
        ),
        "training_data_poisoning": AISecurityVulnerability(
            category="Training Data Poisoning",
            ai_framework="training",
            owasp_llm_mapping=["LLM03: Training Data Poisoning"],
            impact="Model integrity compromise",
            detection_method="Data validation and source verification",
            severity="high",
            description="Training data poisoning through unsanitized input",
            remediation="Validate and sanitize all training data, implement data provenance"
        ),
        "insecure_model_storage": AISecurityVulnerability(
            category="Insecure Model Storage",
            ai_framework="deployment",
            owasp_llm_mapping=["LLM06: Sensitive Information Disclosure"],
            impact="Model theft, data exposure",
            detection_method="File permission and encryption analysis",
            severity="medium",
            description="Insecure storage of model files and weights",
            remediation="Encrypt model files, implement proper access controls"
        ),
        "model_inversion": AISecurityVulnerability(
            category="Model Inversion Attack",
            ai_framework="inference",
            owasp_llm_mapping=["LLM06: Sensitive Information Disclosure"],
            impact="Training data reconstruction",
            detection_method="Analysis of model output patterns",
            severity="high",
            description="Model inversion vulnerability exposing training data",
            remediation="Implement differential privacy, output sanitization"
        ),
        "adversarial_input": AISecurityVulnerability(
            category="Adversarial Input Vulnerability",
            ai_framework="inference",
            owasp_llm_mapping=["LLM02: Insecure Output Handling"],
            impact="Model misclassification",
            detection_method="Input validation analysis",
            severity="medium",
            description="Lack of protection against adversarial inputs",
            remediation="Implement adversarial detection, input preprocessing"
        ),
        "unsafe_plugin_execution": AISecurityVulnerability(
            category="Unsafe Plugin Execution",
            ai_framework="llm_agents",
            owasp_llm_mapping=["LLM07: Insecure Plugin Design"],
            impact="Code execution, system compromise",
            detection_method="Plugin security analysis",
            severity="critical",
            description="Unsafe execution of LLM plugins or tools",
            remediation="Sandbox plugin execution, validate plugin inputs"
        ),
        "excessive_agency": AISecurityVulnerability(
            category="Excessive Agency",
            ai_framework="llm_agents",
            owasp_llm_mapping=["LLM08: Excessive Agency"],
            impact="Unauthorized actions",
            detection_method="Permission analysis",
            severity="high",
            description="LLM agent with excessive permissions or capabilities",
            remediation="Implement principle of least privilege, action approval"
        ),
        "insecure_model_communication": AISecurityVulnerability(
            category="Insecure Model Communication",
            ai_framework="distributed_inference",
            owasp_llm_mapping=["LLM09: Overreliance"],
            impact="Data interception, model manipulation",
            detection_method="Communication security analysis",
            severity="medium",
            description="Insecure communication between model components",
            remediation="Use TLS encryption, implement authentication"
        ),
        "model_supply_chain": AISecurityVulnerability(
            category="Model Supply Chain Risk",
            ai_framework="deployment",
            owasp_llm_mapping=["LLM05: Supply Chain Vulnerabilities"],
            impact="Compromised models, backdoors",
            detection_method="Model provenance analysis",
            severity="high",
            description="Use of untrusted or unverified model components",
            remediation="Verify model signatures, use trusted model repositories"
        )
    }

    def __init__(self):
        # Prompt injection patterns
        self.prompt_injection_patterns = [
            r'input.*\+.*prompt',  # Direct input concatenation to prompts
            r'user_input.*format\(',  # String formatting with user input
            r'f["\'].*{user.*}.*["\']',  # f-strings with user input in prompts
            r'\.completion\(.*user.*\)',  # User input directly to LLM completion
            r'system.*user_input',  # User input in system prompts
        ]

        # Model extraction patterns
        self.model_extraction_patterns = [
            r'model\.state_dict\(\)',  # Exposing model state
            r'torch\.save\(model',  # Saving model without protection
            r'model\.parameters\(\)',  # Exposing model parameters
            r'\.predict\(.*batch.*\)',  # Batch prediction without limits
        ]

        # Training data patterns
        self.training_data_patterns = [
            r'open\(.*user.*\)',  # Opening files from user input
            r'pd\.read_csv\(.*request\.',  # Reading CSV from request
            r'dataset.*user_data',  # User data in training datasets
            r'train.*unsanitized',  # Explicit mention of unsanitized training
        ]

        # Model storage patterns
        self.model_storage_patterns = [
            r'torch\.save\([^,]*,\s*["\'][^"\']*\.pt["\']',  # Saving models without encryption
            r'joblib\.dump\(model',  # Dumping models without protection
            r'pickle\.dump\(model',  # Pickle dumping models
            r'model\.save\(["\'][^"\']*["\']',  # Saving without encryption
        ]

        # Plugin execution patterns
        self.plugin_execution_patterns = [
            r'exec\(.*user',  # Executing user code
            r'eval\(.*user',  # Evaluating user input
            r'subprocess.*user',  # Running subprocesses with user input
            r'os\.system\(.*user',  # System calls with user input
        ]

        # LLM framework indicators
        self.llm_frameworks = [
            'openai', 'anthropic', 'langchain', 'transformers',
            'huggingface', 'llamaindex', 'guidance', 'autogen'
        ]

        # ML framework indicators
        self.ml_frameworks = [
            'torch', 'tensorflow', 'keras', 'sklearn', 'pytorch',
            'jax', 'flax', 'mxnet', 'onnx', 'tensorrt'
        ]

    async def scan_ai_project(self, project_path: Path) -> ScanResult:
        """Scan an AI/ML project for security vulnerabilities."""
        issues = []

        # Find Python files
        python_files = self._find_python_files(project_path)

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Skip if not an AI/ML file
                if not self._is_ai_ml_file(content):
                    continue

                # Scan for vulnerabilities
                file_issues = await self._scan_file(file_path, content)
                issues.extend(file_issues)

            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                continue

        return ScanResult(
            tool="ai_security",
            success=True,
            issues=issues,
            metadata={
                "files_scanned": len(python_files),
                "ai_ml_files": len([f for f in python_files if self._is_ai_ml_file_path(f)]),
                "frameworks_detected": self._detect_frameworks(python_files),
                "vulnerability_categories": len(set(issue['rule'] for issue in issues))
            }
        )

    def _find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for pattern in ['**/*.py', '**/*.ipynb']:
            python_files.extend(project_path.glob(pattern))
        return python_files

    def _is_ai_ml_file(self, content: str) -> bool:
        """Check if file contains AI/ML framework usage."""
        ai_indicators = []
        ai_indicators.extend([f'import {fw}' for fw in self.llm_frameworks])
        ai_indicators.extend([f'from {fw}' for fw in self.llm_frameworks])
        ai_indicators.extend([f'import {fw}' for fw in self.ml_frameworks])
        ai_indicators.extend([f'from {fw}' for fw in self.ml_frameworks])

        # Additional AI/ML indicators
        ai_indicators.extend([
            'torch.nn', 'nn.Module', 'DataLoader', 'Dataset',
            'model.train()', 'model.eval()', 'optimizer',
            'loss_function', 'neural_network', 'deep_learning',
            'machine_learning', 'artificial_intelligence',
            'llm', 'gpt', 'bert', 'transformer', 'embedding'
        ])

        return any(indicator in content.lower() for indicator in ai_indicators)

    def _is_ai_ml_file_path(self, file_path: Path) -> bool:
        """Check if file path suggests AI/ML usage."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._is_ai_ml_file(f.read())
        except:
            return False

    def _detect_frameworks(self, python_files: List[Path]) -> List[str]:
        """Detect which AI/ML frameworks are used in the project."""
        frameworks = set()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for framework in self.llm_frameworks + self.ml_frameworks:
                    if framework in content:
                        frameworks.add(framework)
            except:
                continue

        return list(frameworks)

    async def _scan_file(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Scan a single file for AI security vulnerabilities."""
        issues = []

        # Parse AST for sophisticated analysis
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
        """Analyze AST for AI security vulnerabilities."""
        issues = []

        class AISecurityVisitor(ast.NodeVisitor):
            def __init__(self, scanner, file_path):
                self.scanner = scanner
                self.file_path = file_path
                self.issues = []

            def visit_Call(self, node):
                """Visit function calls to detect AI security issues."""

                # Prompt injection detection
                if self._is_llm_call(node):
                    if self._has_unsafe_user_input(node):
                        vuln = self.scanner.VULNERABILITIES["prompt_injection"]
                        self.issues.append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'column': node.col_offset,
                            'rule': 'prompt_injection',
                            'message': f"{vuln.description}: User input directly passed to LLM",
                            'severity': vuln.severity,
                            'source': 'ai_security',
                            'owasp_llm_mapping': vuln.owasp_llm_mapping,
                            'remediation': vuln.remediation
                        })

                # Model extraction detection
                if self._is_model_exposure_call(node):
                    vuln = self.scanner.VULNERABILITIES["model_extraction"]
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'column': node.col_offset,
                        'rule': 'model_extraction',
                        'message': f"{vuln.description}: Model state exposed",
                        'severity': vuln.severity,
                        'source': 'ai_security',
                        'owasp_llm_mapping': vuln.owasp_llm_mapping,
                        'remediation': vuln.remediation
                    })

                # Unsafe plugin execution
                if self._is_unsafe_execution(node):
                    vuln = self.scanner.VULNERABILITIES["unsafe_plugin_execution"]
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'column': node.col_offset,
                        'rule': 'unsafe_plugin_execution',
                        'message': f"{vuln.description}: Unsafe code execution detected",
                        'severity': vuln.severity,
                        'source': 'ai_security',
                        'owasp_llm_mapping': vuln.owasp_llm_mapping,
                        'remediation': vuln.remediation
                    })

                # Model storage without encryption
                if self._is_unsafe_model_save(node):
                    vuln = self.scanner.VULNERABILITIES["insecure_model_storage"]
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'column': node.col_offset,
                        'rule': 'insecure_model_storage',
                        'message': f"{vuln.description}: Model saved without encryption",
                        'severity': vuln.severity,
                        'source': 'ai_security',
                        'owasp_llm_mapping': vuln.owasp_llm_mapping,
                        'remediation': vuln.remediation
                    })

                self.generic_visit(node)

            def _is_llm_call(self, node):
                """Check if this is an LLM API call."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr in ['completion', 'chat', 'generate', 'predict', 'invoke']
                elif isinstance(node.func, ast.Name):
                    return node.func.id in ['openai', 'anthropic', 'completion']
                return False

            def _is_model_exposure_call(self, node):
                """Check if this exposes model internals."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr in ['state_dict', 'parameters', 'named_parameters', 'modules']
                return False

            def _is_unsafe_execution(self, node):
                """Check if this is unsafe code execution."""
                if isinstance(node.func, ast.Name):
                    return node.func.id in ['exec', 'eval', 'compile']
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'os':
                            return node.func.attr in ['system', 'popen']
                        elif node.func.value.id == 'subprocess':
                            return node.func.attr in ['run', 'call', 'Popen']
                return False

            def _is_unsafe_model_save(self, node):
                """Check if model is saved without proper protection."""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'torch':
                            return node.func.attr == 'save'
                        elif node.func.value.id in ['joblib', 'pickle']:
                            return node.func.attr in ['dump', 'save']
                    elif isinstance(node.func.value, ast.Attribute):
                        return node.func.attr == 'save'  # model.save()
                return False

            def _has_unsafe_user_input(self, node):
                """Check if call contains unsafe user input."""
                for arg in node.args:
                    if self._contains_user_reference(arg):
                        return True
                for keyword in node.keywords:
                    if self._contains_user_reference(keyword.value):
                        return True
                return False

            def _contains_user_reference(self, node):
                """Check if node contains reference to user input."""
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        return node.value.id in ['request', 'user', 'input', 'prompt', 'query']
                elif isinstance(node, ast.Name):
                    return node.id in ['user_input', 'user_prompt', 'query', 'message']
                elif isinstance(node, ast.JoinedStr):  # f-strings
                    for value in node.values:
                        if isinstance(value, ast.FormattedValue):
                            if self._contains_user_reference(value.value):
                                return True
                elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                    return (self._contains_user_reference(node.left) or
                           self._contains_user_reference(node.right))
                return False

        visitor = AISecurityVisitor(self, file_path)
        visitor.visit(tree)
        return visitor.issues

    def _analyze_patterns(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Analyze file content using regex patterns for AI security."""
        issues = []
        lines = content.split('\n')

        # Check each pattern category
        pattern_checks = [
            (self.prompt_injection_patterns, 'prompt_injection'),
            (self.model_extraction_patterns, 'model_extraction'),
            (self.training_data_patterns, 'training_data_poisoning'),
            (self.model_storage_patterns, 'insecure_model_storage'),
            (self.plugin_execution_patterns, 'unsafe_plugin_execution'),
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
                            'message': f"{vuln.description}: Pattern detected",
                            'severity': vuln.severity,
                            'source': 'ai_security',
                            'owasp_llm_mapping': vuln.owasp_llm_mapping,
                            'remediation': vuln.remediation,
                            'code_snippet': line.strip()
                        })

        return issues