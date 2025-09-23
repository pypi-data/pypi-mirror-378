# MCP Security Scanner 🛡️

[![PyPI version](https://badge.fury.io/py/mcp-for-code-quality-security.svg)](https://badge.fury.io/py/mcp-for-code-quality-security)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.3.1-green.svg)](https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools)

A powerful **Model Context Protocol (MCP)** agent for automated Python code quality and security scanning. Integrates seamlessly with AI assistants like Claude Code while providing comprehensive security analysis and professional reporting.

> **🤖 For Claude Code Sessions**: This project has automatic startup protocol. When starting a new session, Claude will automatically read project context, activate virtual environment, and present development options. See `CLAUDE.md` for details.

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

### Quick Start (End Users)

```bash
# Install from PyPI
pip install mcp-for-code-quality-security

# Verify installation
mcpcqs --version

# Start scanning
mcpcqs scan ./your-project
```

### Development Setup

```bash
# Clone and setup virtual environment
git clone https://github.com/lgtkgtv/mcp_agent--code_quality_security_tools.git
cd mcp_agent--code_quality_security_tools
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
```

📚 **Documentation**:
- **[Setup Guide](docs/current/SETUP_GUIDE.md)** - Complete installation for all user types
- **[User Guide](docs/current/USER_GUIDE.md)** - How to use the scanner effectively
- **[AI Integration](docs/current/AI_INTEGRATION.md)** - Claude Code & other AI assistants
- **[Docker Examples](docs/examples/docker/)** - Container usage patterns

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
    "mcp-for-code-quality-security": {
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
        pip install mcp-for-code-quality-security
        mcp-scanner comprehensive-scan . --save-reports
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: security_results.sarif
```

### Pre-commit Hooks
```yaml
repos:
- repo: https://github.com/your-org/mcp-for-code-quality-security
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
mcp-for-code-quality-security/
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

## ✅ Current Features vs 🚧 Planned Features

### What Works Today (v0.3.1)
- ✅ **10+ Security Tools** - Integrated Ruff, MyPy, Bandit, Safety, Pylint, and more
- ✅ **MCP Server** - Full integration with Claude Code and AI assistants
- ✅ **Multiple Report Formats** - JSON, Markdown, YAML, SARIF
- ✅ **CLI Interface** - Comprehensive command-line tools
- ✅ **Configuration Presets** - default, strict, security, fast modes
- ✅ **Auto-fixing** - Safe automatic issue resolution
- ✅ **FastAPI Security Scanner** - Custom security analysis
- ✅ **AI/LLM Security Scanner** - Prompt injection detection

### On the Roadmap
- 🚧 **OWASP Compliance Dashboard** - Track security scores (Q1 2025)
- 🚧 **Multi-Project Tracking** - Monitor multiple projects (Q1 2025)
- 🚧 **Threat Model Profiles** - Context-aware scanning (Q2 2025)
- 🚧 **Web Dashboard** - Visual security status (Q2 2025)
- 🚧 **Educational Mode** - Learn security as you code (Future)
- 🚧 **AI Transparency Layer** - Explain security decisions (Future)

See [ROADMAP.md](ROADMAP.md) for detailed development plans.

## 📈 Performance & Scale

- **Scan Speed**: 2-5 seconds for typical projects
- **Report Generation**: 1-3 seconds per report type
- **File Support**: Handles projects with 15,000+ lines
- **Tool Integration**: 10+ security and quality tools
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

Start with `pip install mcp-for-code-quality-security` and integrate enterprise-grade security analysis into your workflow today!