"""
Configuration management for MCP Code Scanner.

This module handles loading, validating, and managing scan configurations
from various sources (files, presets, command-line arguments).
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, validator


class ToolConfig(BaseModel):
    """Configuration for individual tools."""
    
    model_config = ConfigDict(extra='allow')
    
    enabled: bool = True
    timeout: int = 300
    auto_fix: bool = False
    config_file: Optional[str] = None
    extra_args: List[str] = Field(default_factory=list)
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class QualityGates(BaseModel):
    """Quality gate thresholds for failing builds."""
    
    max_critical_issues: Optional[int] = None
    max_error_issues: Optional[int] = None
    max_warning_issues: Optional[int] = None
    max_info_issues: Optional[int] = None
    min_coverage_percentage: Optional[float] = None
    max_complexity: Optional[int] = None
    max_duplicate_lines: Optional[int] = None


class ReportingConfig(BaseModel):
    """Configuration for report generation."""
    
    output_format: str = 'json'
    include_metrics: bool = True
    include_trends: bool = False
    include_suggestions: bool = True
    generate_badge: bool = False
    save_results: bool = False
    results_dir: str = '.mcp-scanner-results'


class ProjectStructure(BaseModel):
    """Project structure configuration."""
    
    source_dirs: List[str] = Field(default_factory=lambda: ['src', 'lib'])
    test_dirs: List[str] = Field(default_factory=lambda: ['tests', 'test'])
    exclude_dirs: List[str] = Field(default_factory=lambda: [
        '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        '.venv', 'venv', 'env', '.env', '.git', '.tox', 'node_modules',
        'build', 'dist'
    ])
    include_patterns: List[str] = Field(default_factory=lambda: ['*.py'])
    exclude_patterns: List[str] = Field(default_factory=lambda: [])


class ScanConfiguration(BaseModel):
    """Complete scan configuration."""
    
    model_config = ConfigDict(extra='allow')
    
    # Basic settings
    name: str = 'default'
    description: str = 'Default configuration'
    
    # Tool selection
    enabled_tools: Set[str] = Field(default_factory=lambda: {
        'ruff', 'mypy', 'bandit', 'safety', 'pylint'
    })
    
    # Scan options  
    include_tests: bool = True
    auto_fix: bool = False
    safe_fixes_only: bool = True
    max_line_length: int = 88
    
    # Output options
    output_format: str = 'json'
    show_source: bool = True
    group_by_file: bool = True
    
    # Severity filtering
    min_severity: str = 'info'
    exclude_rules: Set[str] = Field(default_factory=set)
    
    # Performance settings
    parallel_execution: bool = True
    timeout_seconds: int = 300
    max_workers: Optional[int] = None
    
    # Tool-specific configurations
    tool_configs: Dict[str, ToolConfig] = Field(default_factory=dict)
    
    # Project structure
    project_structure: ProjectStructure = Field(default_factory=ProjectStructure)
    
    # Quality gates
    quality_gates: Optional[QualityGates] = None
    
    # Reporting
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    
    @validator('min_severity')
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = {'info', 'warning', 'error', 'critical'}
        if v not in valid_severities:
            raise ValueError(f'min_severity must be one of {valid_severities}')
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format."""
        valid_formats = {'json', 'yaml', 'text', 'markdown', 'html', 'junit'}
        if v not in valid_formats:
            raise ValueError(f'output_format must be one of {valid_formats}')
        return v
    
    def get_tool_config(self, tool_name: str) -> ToolConfig:
        """Get configuration for a specific tool."""
        if tool_name not in self.tool_configs:
            self.tool_configs[tool_name] = ToolConfig()
        return self.tool_configs[tool_name]
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled."""
        return (tool_name in self.enabled_tools and 
                self.get_tool_config(tool_name).enabled)


class ConfigurationManager:
    """Manages loading and validation of scan configurations."""
    
    def __init__(self):
        self._presets: Dict[str, ScanConfiguration] = {}
        self._load_builtin_presets()
    
    def _load_builtin_presets(self):
        """Load built-in configuration presets."""
        
        # Default preset
        self._presets['default'] = ScanConfiguration(
            name='default',
            description='Balanced scanning for general development',
            enabled_tools={'ruff', 'mypy', 'bandit', 'safety', 'pylint'},
            min_severity='info',
            auto_fix=False,
            parallel_execution=True
        )
        
        # Strict preset
        self._presets['strict'] = ScanConfiguration(
            name='strict',
            description='Comprehensive scanning with all tools and strict quality gates',
            enabled_tools={'ruff', 'mypy', 'bandit', 'safety', 'pylint', 'black', 'isort'},
            min_severity='warning',
            auto_fix=False,
            quality_gates=QualityGates(
                max_critical_issues=0,
                max_error_issues=5,
                max_warning_issues=20,
                min_coverage_percentage=80.0,
                max_complexity=10
            ),
            tool_configs={
                'ruff': ToolConfig(
                    custom_config={
                        'select': ['ALL'],
                        'ignore': ['E501', 'D', 'ANN', 'COM812', 'ISC001']
                    }
                ),
                'mypy': ToolConfig(
                    custom_config={'strict': True}
                ),
                'bandit': ToolConfig(
                    custom_config={
                        'confidence': 'low',
                        'severity': 'low'
                    }
                )
            }
        )
        
        # Security-focused preset
        self._presets['security'] = ScanConfiguration(
            name='security',
            description='Security-focused scanning with vulnerability detection',
            enabled_tools={'bandit', 'safety', 'ruff'},
            include_tests=False,
            min_severity='warning',
            auto_fix=False,
            tool_configs={
                'bandit': ToolConfig(
                    custom_config={
                        'confidence': 'low',
                        'severity': 'low',
                        'exclude_dirs': ['tests', 'test', 'testing']
                    }
                ),
                'ruff': ToolConfig(
                    custom_config={
                        'select': ['S', 'B', 'E9', 'F', 'UP'],
                        'ignore': ['E501']
                    }
                )
            },
            quality_gates=QualityGates(
                max_critical_issues=0,
                max_error_issues=0
            )
        )
        
        # Fast preset
        self._presets['fast'] = ScanConfiguration(
            name='fast',
            description='Quick scanning with essential tools for development workflow',
            enabled_tools={'ruff', 'mypy'},
            min_severity='warning',
            auto_fix=False,
            parallel_execution=True,
            timeout_seconds=60,
            tool_configs={
                'ruff': ToolConfig(
                    custom_config={
                        'select': ['E', 'W', 'F', 'I', 'B'],
                        'ignore': ['E501']
                    }
                )
            }
        )
    
    def get_preset(self, name: str) -> ScanConfiguration:
        """Get a configuration preset by name."""
        if name not in self._presets:
            raise ValueError(f"Unknown preset: {name}. Available: {list(self._presets.keys())}")
        
        # Return a copy to avoid modifying the original
        return self._presets[name].model_copy(deep=True)
    
    def list_presets(self) -> Dict[str, str]:
        """List available presets with their descriptions."""
        return {
            name: config.description 
            for name, config in self._presets.keys()
        }
    
    def load_from_file(self, config_path: Union[str, Path]) -> ScanConfiguration:
        """Load configuration from a file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    import json
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            # Handle tool_configs conversion
            if 'tool_configs' in data:
                tool_configs = {}
                for tool_name, tool_data in data['tool_configs'].items():
                    if isinstance(tool_data, dict):
                        tool_configs[tool_name] = ToolConfig(**tool_data)
                    else:
                        tool_configs[tool_name] = tool_data
                data['tool_configs'] = tool_configs
            
            # Handle quality_gates conversion
            if 'quality_gates' in data and data['quality_gates']:
                data['quality_gates'] = QualityGates(**data['quality_gates'])
            
            # Handle project_structure conversion
            if 'project_structure' in data:
                data['project_structure'] = ProjectStructure(**data['project_structure'])
            
            # Handle reporting conversion
            if 'reporting' in data:
                data['reporting'] = ReportingConfig(**data['reporting'])
            
            return ScanConfiguration(**data)
        
        except Exception as e:
            raise ValueError(f"Failed to parse configuration file {config_path}: {e}")
    
    def save_to_file(self, config: ScanConfiguration, config_path: Union[str, Path]):
        """Save configuration to a file."""
        config_path = Path(config_path)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Convert to dict for serialization
            data = config.model_dump()
            
            # Convert sets to lists for YAML serialization
            if 'enabled_tools' in data:
                data['enabled_tools'] = list(data['enabled_tools'])
            if 'exclude_rules' in data:
                data['exclude_rules'] = list(data['exclude_rules'])
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                elif config_path.suffix.lower() == '.json':
                    import json
                    json.dump(data, f, indent=2, sort_keys=False)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_path}: {e}")
    
    def find_config_file(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """Find configuration file in project hierarchy."""
        if start_path is None:
            start_path = Path.cwd()
        
        config_names = [
            '.mcp-scanner.yaml',
            '.mcp-scanner.yml',
            'mcp-scanner.yaml',
            'mcp-scanner.yml',
            'pyproject.toml'  # Check for [tool.mcp-scanner] section
        ]
        
        current_path = Path(start_path).resolve()
        
        while current_path != current_path.parent:
            for config_name in config_names:
                config_file = current_path / config_name
                if config_file.exists():
                    if config_name == 'pyproject.toml':
                        # Check if it contains mcp-scanner configuration
                        if self._has_mcp_scanner_config(config_file):
                            return config_file
                    else:
                        return config_file
            
            current_path = current_path.parent
        
        return None
    
    def _has_mcp_scanner_config(self, pyproject_path: Path) -> bool:
        """Check if pyproject.toml contains mcp-scanner configuration."""
        try:
            import tomli
            with open(pyproject_path, 'rb') as f:
                data = tomli.load(f)
            return 'tool' in data and 'mcp-scanner' in data['tool']
        except Exception:
            return False
    
    def load_from_pyproject(self, pyproject_path: Path) -> ScanConfiguration:
        """Load configuration from pyproject.toml [tool.mcp-scanner] section."""
        try:
            import tomli
            with open(pyproject_path, 'rb') as f:
                data = tomli.load(f)
            
            if 'tool' not in data or 'mcp-scanner' not in data['tool']:
                raise ValueError("No [tool.mcp-scanner] section found in pyproject.toml")
            
            scanner_config = data['tool']['mcp-scanner']
            
            # Convert similar to load_from_file
            if 'tool_configs' in scanner_config:
                tool_configs = {}
                for tool_name, tool_data in scanner_config['tool_configs'].items():
                    tool_configs[tool_name] = ToolConfig(**tool_data)
                scanner_config['tool_configs'] = tool_configs
            
            if 'quality_gates' in scanner_config and scanner_config['quality_gates']:
                scanner_config['quality_gates'] = QualityGates(**scanner_config['quality_gates'])
            
            if 'project_structure' in scanner_config:
                scanner_config['project_structure'] = ProjectStructure(**scanner_config['project_structure'])
            
            if 'reporting' in scanner_config:
                scanner_config['reporting'] = ReportingConfig(**scanner_config['reporting'])
            
            return ScanConfiguration(**scanner_config)
        
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {pyproject_path}: {e}")
    
    def merge_configs(
        self, 
        base_config: ScanConfiguration,
        override_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ScanConfiguration:
        """Merge configurations with override precedence."""
        
        # Start with base config
        merged_data = base_config.model_dump()
        
        # Apply override config
        if override_config:
            merged_data.update(override_config)
        
        # Apply keyword arguments
        merged_data.update(kwargs)
        
        # Handle special merging for tool_configs
        if 'tool_configs' in merged_data:
            base_tool_configs = base_config.tool_configs.copy()
            override_tool_configs = merged_data.get('tool_configs', {})
            
            for tool_name, tool_config in override_tool_configs.items():
                if tool_name in base_tool_configs:
                    # Merge tool configs
                    base_tool_data = base_tool_configs[tool_name].model_dump()
                    if isinstance(tool_config, dict):
                        base_tool_data.update(tool_config)
                        base_tool_configs[tool_name] = ToolConfig(**base_tool_data)
                else:
                    base_tool_configs[tool_name] = ToolConfig(**tool_config) if isinstance(tool_config, dict) else tool_config
            
            merged_data['tool_configs'] = base_tool_configs
        
        return ScanConfiguration(**merged_data)
    
    def validate_config(self, config: ScanConfiguration) -> List[str]:
        """Validate configuration and return list of warnings/errors."""
        warnings = []
        
        # Check if any tools are enabled
        if not config.enabled_tools:
            warnings.append("No tools are enabled for scanning")
        
        # Check for conflicting settings
        if config.auto_fix and not config.safe_fixes_only:
            warnings.append("Auto-fix is enabled without safe_fixes_only - this may modify code behavior")
        
        # Check timeout settings
        if config.timeout_seconds < 30:
            warnings.append("Timeout is very short - tools may not complete")
        
        # Check quality gates
        if config.quality_gates:
            if (config.quality_gates.max_critical_issues is not None and 
                config.quality_gates.max_critical_issues < 0):
                warnings.append("max_critical_issues cannot be negative")
        
        # Check tool compatibility
        if 'black' in config.enabled_tools and 'ruff' in config.enabled_tools:
            ruff_config = config.get_tool_config('ruff')
            if 'format' in ruff_config.custom_config.get('select', []):
                warnings.append("Both black and ruff formatting are enabled - this may cause conflicts")
        
        return warnings
    
    def create_minimal_config(
        self, 
        tools: Optional[List[str]] = None,
        output_format: str = 'json',
        min_severity: str = 'info'
    ) -> ScanConfiguration:
        """Create a minimal configuration for quick setup."""
        return ScanConfiguration(
            name='minimal',
            description='Minimal configuration for quick scanning',
            enabled_tools=set(tools) if tools else {'ruff', 'mypy'},
            output_format=output_format,
            min_severity=min_severity,
            parallel_execution=True,
            timeout_seconds=120
        )


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return config_manager