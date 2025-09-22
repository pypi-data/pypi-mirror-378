# MCP Security Scanner 🛡️

[![PyPI version](https://badge.fury.io/py/mcp-security-scanner.svg)](https://badge.fury.io/py/mcp-security-scanner)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools/workflows/Test%20and%20Quality%20Checks/badge.svg)](https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools/actions)

A powerful **Model Context Protocol (MCP)** agent for automated Python code quality and security scanning. Integrates seamlessly with AI assistants like Claude Code while providing enterprise-grade security analysis and professional reporting.

## 🚀 Key Features

### 🔍 **Comprehensive Code Analysis**
- **10+ integrated tools**: Ruff, MyPy, Bandit, Safety, Pylint, Black, isort, pytest, Coverage
- **Custom security scanners**: FastAPI security, AI/LLM security analysis
- **Real vulnerability detection**: SQL injection, XSS, SSTI, prompt injection, and more

### 🛡️ **Enterprise Security**
- **OWASP compliance mapping**: Top 10 2021, API Top 10, LLM Top 10, Mobile Top 10
- **Professional reporting**: Executive summaries, technical reports, SARIF format
- **Risk scoring**: Automated compliance scoring and risk assessment

### 🤖 **AI Assistant Integration**
- **MCP server**: Native integration with Claude Code and other AI assistants
- **JSON-RPC protocol**: Standardized communication via stdio
- **8 specialized tools**: From basic scanning to enterprise reporting

### 🔧 **Developer Experience**
- **CLI and programmatic APIs**: Use standalone or integrate into workflows
- **Multiple output formats**: JSON, Markdown, YAML, text, SARIF
- **Configuration presets**: default, strict, security, fast
- **Auto-fixing**: Safe automatic resolution of code quality issues

## 📦 Installation

### Quick Start

```bash
# Install from PyPI
pip install mcp-security-scanner

# Or with uv (recommended)
uv pip install mcp-security-scanner

# Verify installation
mcpcqs --version
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools.git
cd mcp_agent--code_quality_security_tools

# Create virtual environment with uv
uv venv .venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
```

## 🎯 Usage

> **CLI Commands**: Use either `mcp-for-code-quality-security` (full name) or `mcpcqs` (short alias)

### CLI Usage

```bash
# Basic project scan
mcpcqs scan ./your-project

# Security-focused scan
mcpcqs scan ./your-project --config security

# Quick scan with JSON output
mcpcqs scan ./your-project --config fast --output json

# Auto-fix safe issues
mcpcqs scan ./your-project --fix --safe-only

# Generate enterprise security report
mcpcqs security ./your-project --output-dir ./reports --company "Acme Corp"

# Get project information
mcpcqs info ./your-project
```

### MCP Server Integration

#### Claude Code Integration

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "mcp-security-scanner": {
      "command": "mcpcqs",
      "args": ["serve"]
    }
  }
}
```

#### Start MCP Server

```bash
# Start MCP server
mcpcqs serve

# With custom configuration
mcpcqs serve --config strict
```

### Programmatic Usage

```python
from mcp_code_scanner import CodeScanner, ScanConfig

# Basic scanning
scanner = CodeScanner()
results = await scanner.scan_project("./your-project")

# Custom configuration
config = ScanConfig.get_preset("security")
results = await scanner.scan_project("./your-project", config)

# Security-focused scan
security_results = await scanner.security_scan("./your-project")
```

## 📊 Professional Reporting

### Executive Reports
Perfect for C-level stakeholders with business impact analysis:
- Overall risk assessment and compliance scoring
- ROI expectations and investment recommendations
- Strategic security roadmap and timeline
- Regulatory compliance status

### Technical Reports
Detailed analysis for development teams:
- Vulnerability analysis by tool and category
- Code-level security findings with line numbers
- OWASP mappings and remediation guidance
- Priority-based action plans

### SARIF Integration
Industry-standard format for security dashboards:
- GitHub Security tab integration
- Azure DevOps security reports
- GitLab security dashboards
- Third-party SIEM compatibility

## 🛡️ Security Capabilities

### FastAPI Security Analysis
| Vulnerability Type | Detection | OWASP Mapping | Severity |
|-------------------|-----------|---------------|----------|
| SQL Injection | ✅ | A03:2021 | Critical |
| NoSQL Injection | ✅ | A03:2021 | Critical |
| SSTI | ✅ | A03:2021 | High |
| Path Traversal | ✅ | A01:2021 | High |
| Missing Authentication | ✅ | A07:2021 | High |
| Insecure Dependencies | ✅ | A06:2021 | Medium |

### AI/LLM Security Analysis
| Vulnerability Type | Detection | OWASP LLM | Severity |
|-------------------|-----------|-----------|----------|
| Prompt Injection | ✅ | LLM01 | Critical |
| Model Extraction | ✅ | LLM06 | High |
| Training Data Poisoning | ✅ | LLM03 | High |
| Unsafe Plugin Execution | ✅ | LLM07 | High |
| Model Denial of Service | ✅ | LLM04 | Medium |

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: MCP Security Scan
      run: |
        pip install mcp-security-scanner
        mcp-scanner comprehensive-scan . --save-reports
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: security_results.sarif
```

### Pre-commit Hooks
```yaml
repos:
- repo: https://github.com/your-org/mcp-security-scanner
  rev: v2.0.0
  hooks:
  - id: mcp-security-scan
    args: [--config, security, --critical-only]
```

## 🏗️ Architecture

Built with proven architectural patterns from experimental projects:

- **V1 Pattern**: Comprehensive error handling and tool-specific parsers
- **V2 Pattern**: Simple YAML configuration per tool
- **V3 Pattern**: Category-based plugin discovery with priority ordering

### Key Components

```
mcp-security-scanner/
├── src/mcp_code_scanner/
│   ├── scanners/          # FastAPI & AI security scanners
│   ├── compliance/        # OWASP compliance mapping
│   ├── reports/           # Enterprise report generators
│   ├── parsers/           # Enhanced tool result processing
│   ├── plugins/           # Extensible plugin architecture
│   ├── mcp/              # MCP server integration
│   └── cli/              # Command-line interface
├── configs/               # Tool and category configurations
│   ├── categories/        # Plugin category definitions
│   └── tools/            # Individual tool configurations
└── tests/                # Comprehensive test suite
```

## 📈 Performance & Scale

- **Scan Speed**: 2-5 seconds for typical projects
- **Report Generation**: 1-3 seconds per report type
- **File Support**: Handles projects with 15,000+ lines
- **OWASP Analysis**: 40+ compliance mappings across 4 frameworks
- **Memory Efficient**: Minimal resource usage during scanning

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Plugin Development
Create custom security tools with our plugin framework:

```python
from mcp_code_scanner.plugins.base_plugin import BasePlugin

class CustomSecurityPlugin(BasePlugin):
    async def scan(self, project_path: Path) -> PluginResult:
        # Your custom security analysis logic
        pass
```

### Development Setup
```bash
git clone https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools.git
cd mcp_agent--code_quality_security_tools
uv venv .venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 📋 Requirements

- **Python**: 3.12 or higher
- **Dependencies**: pydantic, pyyaml, click, rich, fastmcp
- **Optional**: Docker for containerized scanning

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/) - AI assistant integration standard
- [Claude Code](https://claude.ai/code) - AI-powered development environment
- [OWASP](https://owasp.org/) - Web application security standards

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OWASP** for security frameworks and guidelines
- **Anthropic** for the Model Context Protocol standard
- **FastAPI** community for security best practices
- **AI/LLM Security** researchers for vulnerability classifications

---

**🚀 Ready to secure your Python applications?**

Start with `pip install mcp-security-scanner` and integrate enterprise-grade security analysis into your workflow today!