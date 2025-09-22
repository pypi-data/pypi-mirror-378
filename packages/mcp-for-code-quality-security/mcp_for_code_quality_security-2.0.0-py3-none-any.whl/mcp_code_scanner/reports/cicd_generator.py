"""
CI/CD integration generator for enterprise deployments (V1 architectural pattern).
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

from ..core.models import ScanReport
from ..compliance.owasp_mapper import ComplianceReport


class CICDGenerator:
    """
    CI/CD integration generator for enterprise deployment.

    Generates:
    - Pre-commit hooks configurations
    - GitHub Actions security workflows
    - GitLab CI security pipelines
    - Makefile with quality targets
    - Docker security scanning examples
    - Jenkins pipeline examples
    """

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_precommit_hooks(self, project_path: Path) -> str:
        """Generate .pre-commit-config.yaml for git hooks."""

        # Detect project characteristics
        has_fastapi = self._has_fastapi_dependencies(project_path)
        has_ai_libs = self._has_ai_dependencies(project_path)

        config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-added-large-files"},
                        {"id": "check-merge-conflict"},
                        {"id": "debug-statements"},
                        {"id": "check-docstring-first"}
                    ]
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.1",
                    "hooks": [
                        {
                            "id": "black",
                            "language_version": "python3"
                        }
                    ]
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.13.2",
                    "hooks": [
                        {
                            "id": "isort",
                            "args": ["--profile", "black"]
                        }
                    ]
                },
                {
                    "repo": "https://github.com/charliermarsh/ruff-pre-commit",
                    "rev": "v0.1.8",
                    "hooks": [
                        {
                            "id": "ruff",
                            "args": ["--fix", "--exit-non-zero-on-fix"]
                        }
                    ]
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.8.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML"
                            ]
                        }
                    ]
                },
                {
                    "repo": "https://github.com/PyCQA/bandit",
                    "rev": "1.7.5",
                    "hooks": [
                        {
                            "id": "bandit",
                            "args": ["-c", "pyproject.toml"],
                            "exclude": "^tests/"
                        }
                    ]
                },
                {
                    "repo": "https://github.com/your-org/mcp-security-scanner",
                    "rev": "v2.0.0",
                    "hooks": [
                        {
                            "id": "mcp-security-scan",
                            "name": "MCP Security Scanner",
                            "entry": "mcp-code-scanner scan",
                            "language": "python",
                            "types": ["python"],
                            "args": ["--config", "security", "--sarif-output", "security-results.sarif"]
                        }
                    ]
                }
            ]
        }

        # Add FastAPI-specific hooks
        if has_fastapi:
            config["repos"].append({
                "repo": "local",
                "hooks": [
                    {
                        "id": "fastapi-security-check",
                        "name": "FastAPI Security Check",
                        "entry": "mcp-code-scanner scan",
                        "language": "python",
                        "files": r"\.py$",
                        "args": ["--fastapi-focus", "--critical-only"]
                    }
                ]
            })

        # Add AI/LLM-specific hooks
        if has_ai_libs:
            config["repos"].append({
                "repo": "local",
                "hooks": [
                    {
                        "id": "ai-security-check",
                        "name": "AI/LLM Security Check",
                        "entry": "mcp-code-scanner scan",
                        "language": "python",
                        "files": r"\.py$",
                        "args": ["--ai-security", "--prompt-injection-check"]
                    }
                ]
            })

        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def generate_github_actions_workflow(self, project_name: str) -> str:
        """Generate GitHub Actions security workflow."""

        workflow = f"""name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run security scan daily at 2 AM
    - cron: '0 2 * * *'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      actions: read

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv pip install --system -e .
        uv pip install --system mcp-security-scanner

    - name: Run MCP Security Scanner
      run: |
        mcp-code-scanner scan . \\
          --config security \\
          --sarif-output security-results.sarif \\
          --json-output security-results.json \\
          --compliance-report compliance-report.json

    - name: Upload SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: security-results.sarif
        category: mcp-security-scanner

    - name: Upload Security Results Artifacts
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: security-scan-results
        path: |
          security-results.sarif
          security-results.json
          compliance-report.json

    - name: Comment PR with Security Results
      if: github.event_name == 'pull_request' && always()
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');

          // Read compliance report
          let complianceData;
          try {{
            complianceData = JSON.parse(fs.readFileSync('compliance-report.json', 'utf8'));
          }} catch (e) {{
            console.log('No compliance report found');
            return;
          }}

          const score = complianceData.compliance_score || 0;
          const findings = complianceData.total_findings || 0;
          const critical = complianceData.mappings?.filter(m => m.remediation_priority <= 2)?.length || 0;

          const emoji = score >= 90 ? '✅' : score >= 70 ? '⚠️' : '🚨';
          const status = score >= 90 ? 'EXCELLENT' : score >= 70 ? 'GOOD' : 'NEEDS IMPROVEMENT';

          const comment = `## 🛡️ Security Scan Results {{emoji}}

**Overall Security Score:** {{score.toFixed(1)}}% - **{{status}}**

### Summary
- **Total Findings:** {{findings}}
- **Critical/High Priority:** {{critical}}
- **OWASP Compliance:** {{score >= 80 ? 'Compliant' : 'Non-Compliant'}}

### Framework Scores
{{Object.entries(complianceData.framework_scores || {{}}).map(([fw, score]) =>
  `- **${{fw.replace('_', ' ').toUpperCase()}}:** ${{score.toFixed(1)}}%`
).join('\\n')}}

{{critical > 0 ? `
### ⚠️ Action Required
This PR introduces **{{critical}} critical/high priority security issue(s)**. Please review and address before merging.
` : `
### ✅ Security Status
No critical security issues detected. Good to merge!
`}}

*Powered by MCP Security Scanner v2.0*`;

          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});

  compliance-check:
    runs-on: ubuntu-latest
    needs: security-scan
    if: always()

    steps:
    - name: Download security results
      uses: actions/download-artifact@v4
      with:
        name: security-scan-results

    - name: Check compliance threshold
      run: |
        if [ -f compliance-report.json ]; then
          SCORE=$(python3 -c "import json; data=json.load(open('compliance-report.json')); print(data.get('compliance_score', 0))")
          echo "Compliance Score: $SCORE%"

          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "❌ Compliance check failed. Score ($SCORE%) is below threshold (70%)"
            exit 1
          else
            echo "✅ Compliance check passed. Score: $SCORE%"
          fi
        else
          echo "⚠️ No compliance report found"
          exit 1
        fi

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Dependency Scan
      run: |
        pip install safety
        safety check --json --output safety-report.json || true

    - name: Upload dependency scan results
      uses: actions/upload-artifact@v4
      with:
        name: dependency-scan
        path: safety-report.json
"""

        return workflow

    def generate_gitlab_ci_pipeline(self, project_name: str) -> str:
        """Generate GitLab CI security pipeline."""

        pipeline = f"""# GitLab CI Security Pipeline for {project_name}
# Generated by MCP Security Scanner v2.0 on {self.timestamp}

variables:
  PIP_CACHE_DIR: "${{CI_PROJECT_DIR}}/.cache/pip"
  SECURITY_THRESHOLD: "70"

cache:
  paths:
    - .cache/pip/
    - .venv/

stages:
  - security-scan
  - compliance-check
  - reporting

before_script:
  - python -m pip install --upgrade pip
  - pip install uv
  - uv venv .venv
  - source .venv/bin/activate
  - uv pip install -e .
  - uv pip install mcp-security-scanner

security-scan:
  stage: security-scan
  script:
    - source .venv/bin/activate
    - mcp-code-scanner scan . --config security --sarif-output security-results.sarif --json-output security-results.json --compliance-report compliance-report.json
  artifacts:
    when: always
    reports:
      sast: security-results.sarif
    paths:
      - security-results.sarif
      - security-results.json
      - compliance-report.json
    expire_in: 30 days
  allow_failure: false

fastapi-security:
  stage: security-scan
  script:
    - source .venv/bin/activate
    - mcp-code-scanner scan . --fastapi-focus --critical-only --json-output fastapi-security.json
  artifacts:
    paths:
      - fastapi-security.json
    expire_in: 7 days
  only:
    changes:
      - "**/*.py"
  allow_failure: true

ai-security:
  stage: security-scan
  script:
    - source .venv/bin/activate
    - mcp-code-scanner scan . --ai-security --prompt-injection-check --json-output ai-security.json
  artifacts:
    paths:
      - ai-security.json
    expire_in: 7 days
  only:
    changes:
      - "**/*.py"
  allow_failure: true

compliance-check:
  stage: compliance-check
  script:
    - source .venv/bin/activate
    - |
      if [ -f compliance-report.json ]; then
        SCORE=$(python3 -c "import json; data=json.load(open('compliance-report.json')); print(data.get('compliance_score', 0))")
        echo "Compliance Score: $SCORE%"

        if (( $(echo "$SCORE < $SECURITY_THRESHOLD" | bc -l) )); then
          echo "❌ Compliance check failed. Score ($SCORE%) is below threshold ($SECURITY_THRESHOLD%)"
          exit 1
        else
          echo "✅ Compliance check passed. Score: $SCORE%"
        fi
      else
        echo "⚠️ No compliance report found"
        exit 1
      fi
  dependencies:
    - security-scan
  allow_failure: false

generate-report:
  stage: reporting
  script:
    - source .venv/bin/activate
    - |
      python3 << 'EOF'
      import json
      from datetime import datetime

      # Load compliance report
      try:
          with open('compliance-report.json') as f:
              compliance = json.load(f)
      except:
          compliance = {{"compliance_score": 0, "total_findings": 0}}

      # Generate GitLab Pages report
      score = compliance.get('compliance_score', 0)
      findings = compliance.get('total_findings', 0)

      css_class = 'good' if score >= 90 else 'warning' if score >= 70 else 'critical'

      html_report = f'''<!DOCTYPE html>
<html>
<head>
    <title>Security Report - {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .score {{ font-size: 2em; margin: 20px 0; }}
        .good {{ color: green; }}
        .warning {{ color: orange; }}
        .critical {{ color: red; }}
    </style>
</head>
<body>
    <h1>🛡️ Security Report</h1>
    <div class="score {{css_class}}">
        Security Score: {{score:.1f}}%
    </div>
    <p>Total Findings: {{findings}}</p>
    <p>Generated: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}</p>
    <p>Powered by MCP Security Scanner v2.0</p>
</body>
</html>'''

      with open('public/index.html', 'w') as f:
          f.write(html_report)
      EOF
    - mkdir -p public
    - cp security-results.sarif public/
    - cp compliance-report.json public/
  artifacts:
    paths:
      - public
  dependencies:
    - security-scan
  only:
    - main

pages:
  stage: reporting
  script:
    - echo "Deploying security reports to GitLab Pages"
  artifacts:
    paths:
      - public
  dependencies:
    - generate-report
  only:
    - main
"""

        return pipeline

    def generate_makefile(self) -> str:
        """Generate Makefile with quality targets."""

        makefile = f"""# Makefile for {self.timestamp} MCP Security Scanner Integration
# Generated by MCP Security Scanner v2.0

.PHONY: help install test security lint format type-check all clean

# Default Python version
PYTHON := python3
PIP := pip
UV := uv

# Virtual environment
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

help: ## Show this help message
	@echo "MCP Security Scanner - Available Targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

# Installation targets
install: $(VENV) ## Install dependencies and setup virtual environment
	$(VENV_PIP) install -e .
	$(VENV_PIP) install mcp-security-scanner

$(VENV):
	$(UV) venv $(VENV) --python $(PYTHON)
	$(VENV_PIP) install --upgrade pip setuptools wheel

install-dev: install ## Install with development dependencies
	$(VENV_PIP) install -e ".[dev]"
	$(VENV_PIP) install pre-commit
	pre-commit install

# Security targets
security: ## Run comprehensive security scan
	$(VENV_PYTHON) -m mcp_code_scanner scan . --config security --sarif-output security-results.sarif

security-critical: ## Run security scan for critical issues only
	$(VENV_PYTHON) -m mcp_code_scanner scan . --config security --critical-only

security-fastapi: ## Run FastAPI-specific security scan
	$(VENV_PYTHON) -m mcp_code_scanner scan . --fastapi-focus

security-ai: ## Run AI/LLM security scan
	$(VENV_PYTHON) -m mcp_code_scanner scan . --ai-security

compliance-report: ## Generate OWASP compliance report
	$(VENV_PYTHON) -m mcp_code_scanner scan . --compliance-report compliance-report.json
	@echo "Compliance report generated: compliance-report.json"

# Code quality targets
lint: ## Run all linters
	$(VENV_PYTHON) -m ruff check .
	$(VENV_PYTHON) -m pylint src/
	$(VENV_PYTHON) -m bandit -r src/

lint-fix: ## Run linters with auto-fix
	$(VENV_PYTHON) -m ruff check --fix .
	$(VENV_PYTHON) -m black .
	$(VENV_PYTHON) -m isort .

format: ## Format code
	$(VENV_PYTHON) -m black .
	$(VENV_PYTHON) -m isort .

type-check: ## Run type checking
	$(VENV_PYTHON) -m mypy src/

# Testing targets
test: ## Run tests
	$(VENV_PYTHON) -m pytest

test-verbose: ## Run tests with verbose output
	$(VENV_PYTHON) -m pytest -v

test-coverage: ## Run tests with coverage report
	$(VENV_PYTHON) -m pytest --cov=src/ --cov-report=html --cov-report=term

# CI/CD targets
ci-security: ## CI security check with threshold
	$(VENV_PYTHON) -m mcp_code_scanner scan . --config security --compliance-report compliance-report.json
	@python3 -c "import json; data=json.load(open('compliance-report.json')); score=data.get('compliance_score', 0); print(f'Security Score: {{score}}%'); exit(0 if score >= 70 else 1)"

ci-full: lint type-check test security ## Run full CI pipeline
	@echo "✅ All CI checks passed!"

# Quality gates
quality-gate: ## Enforce quality standards
	@echo "🔍 Running quality gate checks..."
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) ci-security
	@echo "✅ Quality gate passed!"

# Utility targets
clean: ## Clean up generated files
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -f security-results.sarif
	rm -f compliance-report.json
	find . -type d -name __pycache__ -exec rm -rf {{}} +
	find . -type f -name "*.pyc" -delete

docker-security: ## Run security scan in Docker
	docker run --rm -v $(PWD):/app -w /app python:3.12-slim bash -c "pip install mcp-security-scanner && mcp-code-scanner scan . --config security"

# Development workflow
dev-setup: install-dev ## Complete development setup
	pre-commit install
	$(MAKE) security
	@echo "🚀 Development environment ready!"

dev-check: ## Quick development check
	$(MAKE) lint-fix
	$(MAKE) test
	$(MAKE) security-critical

# Release targets
pre-release: ## Run pre-release checks
	$(MAKE) clean
	$(MAKE) install-dev
	$(MAKE) quality-gate
	@echo "🎉 Ready for release!"

# Monitoring targets
security-daily: ## Daily security check (for cron)
	$(VENV_PYTHON) -m mcp_code_scanner scan . --config security --json-output daily-security-$$(date +%Y%m%d).json

dependency-check: ## Check for vulnerable dependencies
	$(VENV_PYTHON) -m safety check --json --output dependency-security.json

# Help is default target
.DEFAULT_GOAL := help
"""

        return makefile

    def generate_docker_security_example(self) -> str:
        """Generate Docker security scanning example."""

        dockerfile = """# Multi-stage Docker security scanning
FROM python:3.12-slim as security-scanner

WORKDIR /app

# Install security scanner
RUN pip install mcp-security-scanner

# Copy source code
COPY . .

# Run security scan
RUN mcp-code-scanner scan . --config security --sarif-output /tmp/security-results.sarif

# Production stage
FROM python:3.12-slim as production

WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

# Copy security results from scanner stage
COPY --from=security-scanner /tmp/security-results.sarif /app/security-results.sarif

# Add security metadata
LABEL security.scanner="mcp-security-scanner" \\
      security.version="2.0" \\
      security.scan-date="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

CMD ["python", "-m", "src.main"]
"""

        return dockerfile

    def _has_fastapi_dependencies(self, project_path: Path) -> bool:
        """Check if project uses FastAPI."""
        requirements_files = [
            project_path / "requirements.txt",
            project_path / "pyproject.toml",
            project_path / "setup.py"
        ]

        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text()
                if "fastapi" in content.lower():
                    return True

        return False

    def _has_ai_dependencies(self, project_path: Path) -> bool:
        """Check if project uses AI/ML libraries."""
        ai_libs = ["openai", "langchain", "transformers", "torch", "tensorflow", "anthropic"]

        requirements_files = [
            project_path / "requirements.txt",
            project_path / "pyproject.toml",
            project_path / "setup.py"
        ]

        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text().lower()
                for lib in ai_libs:
                    if lib in content:
                        return True

        return False