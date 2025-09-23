"""
MCP Code Scanner - Automated code quality and security scanning with MCP integration.

This package provides both standalone code quality scanning capabilities and
a Model Context Protocol (MCP) server for integration with AI development tools.
"""

from .core.scanner import CodeScanner, ScanConfig, ScanReport
from .core.reports import ReportGenerator

__version__ = "0.3.2"
__author__ = "MCP Security Scanner Contributors"
__email__ = "security@mcp-scanner.dev"

__all__ = [
    "CodeScanner",
    "ScanConfig", 
    "ScanReport",
    "ReportGenerator",
]