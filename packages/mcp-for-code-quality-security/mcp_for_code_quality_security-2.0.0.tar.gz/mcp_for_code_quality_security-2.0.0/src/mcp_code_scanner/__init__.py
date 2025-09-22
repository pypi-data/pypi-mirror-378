"""
MCP Code Scanner - Automated code quality and security scanning with MCP integration.

This package provides both standalone code quality scanning capabilities and
a Model Context Protocol (MCP) server for integration with AI development tools.
"""

from .core.scanner import CodeScanner, ScanConfig, ScanReport
from .core.reports import ReportGenerator

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "CodeScanner",
    "ScanConfig", 
    "ScanReport",
    "ReportGenerator",
]