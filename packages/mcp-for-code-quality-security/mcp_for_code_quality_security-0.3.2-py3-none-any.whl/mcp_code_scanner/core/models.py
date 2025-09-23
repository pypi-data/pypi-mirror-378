"""
Core data models for the MCP code scanner.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, ConfigDict


class ScanResult(BaseModel):
    """Result from a single tool scan."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tool: str
    success: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScanReport(BaseModel):
    """Complete scan report containing results from all tools."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_path: str
    scan_config: str
    timestamp: str
    results: List[ScanResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    total_issues: int = 0
    critical_issues: int = 0
    fix_suggestions: List[str] = field(default_factory=list)