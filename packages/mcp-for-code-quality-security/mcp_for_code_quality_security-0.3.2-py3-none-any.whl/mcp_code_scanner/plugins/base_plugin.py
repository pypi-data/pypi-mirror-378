"""
Base plugin interface for extensible scanner architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


@dataclass
class PluginResult:
    """Result from plugin execution."""
    plugin_name: str
    success: bool
    data: Any = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePlugin(ABC):
    """Base class for all plugins."""

    # Plugin metadata (override in subclasses)
    PLUGIN_METADATA = {
        'name': 'base_plugin',
        'display_name': 'Base Plugin',
        'category': 'general',
        'version': '1.0.0',
        'description': 'Base plugin class',
        'author': 'MCP Team'
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load plugin configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load plugin config from {config_path}: {e}")
            return {}

    @abstractmethod
    async def scan(self, project_path: Path) -> PluginResult:
        """Perform the plugin's main scanning function."""
        pass

    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file extensions."""
        return self.config.get('supported_files', ['.py'])

    def is_applicable(self, project_path: Path) -> bool:
        """Check if this plugin is applicable to the given project."""
        supported_types = self.get_supported_file_types()

        for file_pattern in supported_types:
            if list(project_path.glob(f"**/*{file_pattern}")):
                return True

        return False

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return self.PLUGIN_METADATA.copy()

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        required_fields = ['name', 'display_name', 'category']

        for field in required_fields:
            if field not in self.config:
                return False

        return True