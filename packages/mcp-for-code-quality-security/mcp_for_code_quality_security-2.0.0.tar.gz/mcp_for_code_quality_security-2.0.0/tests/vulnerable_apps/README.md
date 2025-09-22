# Vulnerable Test Applications

This directory contains intentionally vulnerable applications used for testing the MCP Security Scanner's security analysis capabilities.

## ⚠️ **SECURITY WARNING**

**These applications contain intentional security vulnerabilities and should NEVER be deployed to production or exposed to untrusted networks.**

## 📁 Test Applications

### `vfapi/` - Vulnerable FastAPI Application
- **Purpose**: Tests FastAPI-specific security scanning
- **Vulnerabilities**: SQL injection, NoSQL injection, SSTI, path traversal, authentication bypass
- **Technology**: FastAPI, SQLAlchemy, Jinja2, MongoDB
- **Usage**: Demonstrates custom FastAPI security scanner capabilities

### `damn-vulnerable-MCP-server/` - Vulnerable MCP Server
- **Purpose**: Tests MCP protocol security issues
- **Vulnerabilities**: Command injection, unsafe plugin execution, model extraction
- **Technology**: MCP protocol, Python
- **Usage**: Tests AI/LLM security scanner functionality

### `damn-vulnerable-llm-agent/` - Vulnerable LLM Agent
- **Purpose**: Tests AI/LLM security vulnerabilities
- **Vulnerabilities**: Prompt injection, training data poisoning, model DoS
- **Technology**: LLM integration, various AI frameworks
- **Usage**: Comprehensive AI security analysis testing

## 🧪 Usage in Testing

These applications are scanned by the MCP Security Scanner to verify:

1. **Security scanners detect real vulnerabilities**
2. **OWASP compliance mapping works correctly**
3. **Risk scoring algorithms function properly**
4. **Report generation includes actual findings**

## 🔒 Safety Measures

- Applications are isolated in test environment
- No network exposure during scanning
- Git repositories converted to regular directories
- Intentionally non-functional for deployment

## 📊 Expected Scan Results

When scanning these applications, the MCP Security Scanner should detect:
- **100+ security issues** across all OWASP categories
- **Critical vulnerabilities** in each application
- **Compliance violations** mapped to OWASP frameworks
- **Detailed remediation guidance** for each issue type

These results validate that the scanner's security analysis is working with real, actionable vulnerability detection rather than mock data.