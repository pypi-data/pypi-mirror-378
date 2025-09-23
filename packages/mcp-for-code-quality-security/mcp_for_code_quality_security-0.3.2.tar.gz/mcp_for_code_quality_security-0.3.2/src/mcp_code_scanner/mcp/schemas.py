"""
Data schemas and models for MCP Code Scanner.

This module defines Pydantic models for request/response validation
and data serialization in the MCP server.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class ScanRequest(BaseModel):
    """Request model for code scanning operations."""
    
    project_path: str = Field(..., description="Path to the project to scan")
    config: str = Field(default="default", description="Configuration preset to use")
    auto_fix: bool = Field(default=False, description="Whether to automatically fix issues")
    include_tests: bool = Field(default=True, description="Whether to include test files")
    output_format: str = Field(default="json", description="Output format")
    tools: Optional[List[str]] = Field(default=None, description="Specific tools to run")
    
    @validator('output_format')
    def validate_output_format(cls, v):
        valid_formats = {'json', 'text', 'markdown', 'html'}
        if v not in valid_formats:
            raise ValueError(f'output_format must be one of {valid_formats}')
        return v


class FixRequest(BaseModel):
    """Request model for auto-fixing issues."""
    
    project_path: str = Field(..., description="Path to the project")
    tool_filter: Optional[List[str]] = Field(default=None, description="Tools to use for fixing")
    safe_only: bool = Field(default=True, description="Only apply safe fixes")
    dry_run: bool = Field(default=False, description="Show what would be fixed without making changes")


class SecurityScanRequest(BaseModel):
    """Request model for security scanning."""
    
    project_path: str = Field(..., description="Path to the project")
    include_dependencies: bool = Field(default=True, description="Check dependencies for vulnerabilities")
    severity_threshold: str = Field(default="warning", description="Minimum severity to report")
    
    @validator('severity_threshold')
    def validate_severity(cls, v):
        valid_severities = {'info', 'warning', 'error', 'critical'}
        if v not in valid_severities:
            raise ValueError(f'severity_threshold must be one of {valid_severities}')
        return v


class Issue(BaseModel):
    """Model for a single code quality issue."""
    
    file: str = Field(..., description="File path where the issue was found")
    line: int = Field(..., description="Line number")
    column: int = Field(default=0, description="Column number")
    rule: str = Field(..., description="Rule or check that triggered the issue")
    message: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity level")
    source: str = Field(..., description="Tool that found the issue")
    fixable: Optional[bool] = Field(default=None, description="Whether the issue can be auto-fixed")
    
    # Optional additional metadata
    category: Optional[str] = Field(default=None, description="Issue category")
    confidence: Optional[str] = Field(default=None, description="Confidence level")
    cwe: Optional[str] = Field(default=None, description="CWE identifier for security issues")
    cve: Optional[str] = Field(default=None, description="CVE identifier")
    more_info: Optional[str] = Field(default=None, description="URL with more information")


class ToolResult(BaseModel):
    """Model for results from a single tool."""
    
    tool: str = Field(..., description="Name of the tool")
    success: bool = Field(..., description="Whether the tool ran successfully")
    execution_time: float = Field(..., description="Time taken to run the tool")
    issues: List[Issue] = Field(default_factory=list, description="Issues found by the tool")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional tool-specific data")


class ScanSummary(BaseModel):
    """Summary of scan results."""
    
    total_issues: int = Field(..., description="Total number of issues found")
    critical_issues: int = Field(..., description="Number of critical issues")
    error_issues: int = Field(default=0, description="Number of error-level issues")
    warning_issues: int = Field(default=0, description="Number of warning-level issues") 
    info_issues: int = Field(default=0, description="Number of info-level issues")
    tools_run: int = Field(..., description="Number of tools executed")
    successful_tools: int = Field(..., description="Number of tools that ran successfully")
    failed_tools: int = Field(..., description="Number of tools that failed")
    execution_time: float = Field(..., description="Total execution time")
    issues_by_severity: Dict[str, int] = Field(default_factory=dict, description="Issues grouped by severity")
    issues_by_tool: Dict[str, int] = Field(default_factory=dict, description="Issues grouped by tool")


class ScanResponse(BaseModel):
    """Response model for scan operations."""
    
    success: bool = Field(..., description="Whether the scan was successful")
    project_path: str = Field(..., description="Path of the scanned project")
    config_used: str = Field(..., description="Configuration that was used")
    timestamp: datetime = Field(..., description="When the scan was performed")
    
    # Results
    summary: ScanSummary = Field(..., description="Summary of scan results")
    tool_results: List[ToolResult] = Field(default_factory=list, description="Detailed results from each tool")
    fix_suggestions: List[str] = Field(default_factory=list, description="Suggested actions to fix issues")
    
    # Optional quality gate results
    quality_gate_passed: Optional[bool] = Field(default=None, description="Whether quality gates passed")
    quality_gate_failures: List[str] = Field(default_factory=list, description="Failed quality gate conditions")


class FixResponse(BaseModel):
    """Response model for fix operations."""
    
    success: bool = Field(..., description="Whether the fix operation was successful")
    fixes_applied: bool = Field(..., description="Whether fixes were actually applied (not dry run)")
    tools_used: List[str] = Field(default_factory=list, description="Tools used for fixing")
    files_modified: List[str] = Field(default_factory=list, description="Files that were modified")
    issues_fixed: int = Field(default=0, description="Number of issues that were fixed")
    remaining_issues: int = Field(default=0, description="Number of issues that remain")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during fixing")


class SecurityScanResponse(BaseModel):
    """Response model for security scan operations."""
    
    success: bool = Field(..., description="Whether the security scan was successful")
    security_issues: List[Issue] = Field(default_factory=list, description="Security issues found")
    vulnerability_count: int = Field(..., description="Total number of vulnerabilities")
    critical_vulnerabilities: int = Field(default=0, description="Number of critical vulnerabilities")
    high_vulnerabilities: int = Field(default=0, description="Number of high severity vulnerabilities")
    medium_vulnerabilities: int = Field(default=0, description="Number of medium severity vulnerabilities")
    low_vulnerabilities: int = Field(default=0, description="Number of low severity vulnerabilities")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    vulnerable_packages: List[Dict[str, str]] = Field(default_factory=list, description="Vulnerable dependency packages")


class ProjectInfo(BaseModel):
    """Information about a Python project."""
    
    project_path: str = Field(..., description="Path to the project")
    is_python_project: bool = Field(..., description="Whether this appears to be a Python project")
    python_files_count: int = Field(..., description="Number of Python files found")
    test_files_count: int = Field(default=0, description="Number of test files found")
    total_lines: int = Field(default=0, description="Total lines of code")
    
    # Project structure
    has_pyproject_toml: bool = Field(default=False, description="Has pyproject.toml file")
    has_setup_py: bool = Field(default=False, description="Has setup.py file")
    has_requirements_txt: bool = Field(default=False, description="Has requirements.txt file")
    has_tests: bool = Field(default=False, description="Has test files or directories")
    
    # Package information
    package_directories: List[str] = Field(default_factory=list, description="Detected package directories")
    dependencies: List[str] = Field(default_factory=list, description="Project dependencies")
    
    # Recommendations
    recommended_tools: List[str] = Field(default_factory=list, description="Recommended tools for this project")
    setup_suggestions: List[str] = Field(default_factory=list, description="Suggestions for project setup")


class ToolInfo(BaseModel):
    """Information about a code quality tool."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    available: bool = Field(..., description="Whether the tool is available on the system")
    version: Optional[str] = Field(default=None, description="Tool version")
    capabilities: List[str] = Field(default_factory=list, description="Tool capabilities")
    auto_fix_supported: bool = Field(default=False, description="Whether the tool supports auto-fixing")
    config_files: List[str] = Field(default_factory=list, description="Configuration files the tool can use")


class ConfigPreset(BaseModel):
    """Configuration preset information."""
    
    name: str = Field(..., description="Preset name")
    description: str = Field(..., description="Preset description")
    tools: List[str] = Field(..., description="Tools included in this preset")
    use_case: str = Field(..., description="Recommended use case")
    auto_fix: bool = Field(default=False, description="Whether auto-fix is enabled")
    min_severity: str = Field(default="info", description="Minimum severity level")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


# Union types for responses
ScanResult = Union[ScanResponse, ErrorResponse]
FixResult = Union[FixResponse, ErrorResponse]
SecurityResult = Union[SecurityScanResponse, ErrorResponse]
ProjectInfoResult = Union[ProjectInfo, ErrorResponse]


def create_error_response(message: str, error_code: Optional[str] = None, **details) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=message,
        error_code=error_code,
        details=details if details else None
    )


def create_success_response(data: Dict[str, Any], response_type: type = ScanResponse) -> BaseModel:
    """Create a standardized success response."""
    return response_type(success=True, **data)