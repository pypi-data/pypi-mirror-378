"""
Enhanced Plugin Manager with V3 architectural patterns and v1/v2 learnings.

Incorporates:
- V3: Category-based discovery with priority ordering
- V2: Simple per-plugin configuration loading
- V1: Comprehensive error handling and validation
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Type
import importlib.util
import sys

from .base_plugin import BasePlugin
from ..config.enhanced_config import EnhancedConfigManager, ToolCategory
from ..parsers.enhanced_parsers import EnhancedToolProcessor


@dataclass
class PluginInfo:
    """Information about a discovered plugin."""
    name: str
    display_name: str
    category: str
    version: str
    description: str
    author: str
    priority: int
    enabled: bool = True
    config_path: Optional[Path] = None
    plugin_class: Optional[Type[BasePlugin]] = None


@dataclass
class PluginCategory:
    """Plugin category information."""
    name: str
    display_name: str
    description: str
    icon: str
    priority: int
    tools: List[PluginInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedPluginManager:
    """
    Enhanced Plugin Manager with V1/V2/V3 architectural patterns.

    V3: Category-based discovery with priority ordering
    V2: Simple per-plugin configuration loading
    V1: Comprehensive error handling and validation

    Discovers plugins from:
    1. configs/categories/*.yaml (category definitions)
    2. configs/tools/*/*.yaml (tool configurations)
    3. plugins/ directory (external plugins)
    """

    def __init__(self, config_root: Path):
        self.config_root = Path(config_root)
        self.categories: Dict[str, PluginCategory] = {}
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}

        # V2+V3: Enhanced configuration management
        self.config_manager = EnhancedConfigManager(config_root)

        # V1: Enhanced tool processing
        self.tool_processor = EnhancedToolProcessor()

        # Discover categories and plugins
        self._discover_categories()
        self._discover_tools()
        self._discover_external_plugins()

        # V1: Validate discovered plugins
        self._validate_plugins()

    def _discover_categories(self):
        """Discover plugin categories from YAML files (V3 pattern)."""
        categories_dir = self.config_root / "categories"
        if not categories_dir.exists():
            return

        for category_file in categories_dir.glob("*.yaml"):
            try:
                with open(category_file, 'r', encoding='utf-8') as f:
                    category_data = yaml.safe_load(f)

                category = PluginCategory(
                    name=category_data['name'],
                    display_name=category_data['display_name'],
                    description=category_data['description'],
                    icon=category_data.get('icon', '🔧'),
                    priority=category_data.get('priority', 99),
                    metadata=category_data.get('metadata', {})
                )

                self.categories[category.name] = category

            except Exception as e:
                print(f"Warning: Failed to load category {category_file}: {e}")

    def _discover_tools(self):
        """Discover tools from configs/tools/*/*.yaml (V2 pattern)."""
        tools_dir = self.config_root / "tools"
        if not tools_dir.exists():
            return

        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue

            config_file = tool_dir / "config.yaml"
            if not config_file.exists():
                continue

            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    tool_config = yaml.safe_load(f)

                plugin_info = PluginInfo(
                    name=tool_config['name'],
                    display_name=tool_config['display_name'],
                    category=tool_config['category'],
                    version=tool_config.get('version', '1.0.0'),
                    description=tool_config['description'],
                    author=tool_config.get('author', 'Unknown'),
                    priority=tool_config.get('priority', 99),
                    enabled=tool_config.get('enabled', True),
                    config_path=config_file
                )

                self.plugins[plugin_info.name] = plugin_info

                # Add to category
                if plugin_info.category in self.categories:
                    self.categories[plugin_info.category].tools.append(plugin_info)

            except Exception as e:
                print(f"Warning: Failed to load tool config {config_file}: {e}")

    def _discover_external_plugins(self):
        """Discover external plugins from plugins/ directory."""
        plugins_dir = self.config_root.parent / "plugins"
        if not plugins_dir.exists():
            return

        for plugin_file in plugins_dir.glob("*_plugin.py"):
            try:
                plugin_info = self._load_external_plugin(plugin_file)
                if plugin_info:
                    self.plugins[plugin_info.name] = plugin_info

                    # Add to category
                    if plugin_info.category in self.categories:
                        self.categories[plugin_info.category].tools.append(plugin_info)

            except Exception as e:
                print(f"Warning: Failed to load external plugin {plugin_file}: {e}")

    def _load_external_plugin(self, plugin_file: Path) -> Optional[PluginInfo]:
        """Load external plugin from Python file."""
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr != BasePlugin):
                    plugin_class = attr
                    break

            if not plugin_class:
                return None

            # Get plugin metadata
            metadata = getattr(plugin_class, 'PLUGIN_METADATA', {})

            return PluginInfo(
                name=metadata.get('name', plugin_file.stem),
                display_name=metadata.get('display_name', plugin_file.stem),
                category=metadata.get('category', 'custom'),
                version=metadata.get('version', '1.0.0'),
                description=metadata.get('description', 'External plugin'),
                author=metadata.get('author', 'Community'),
                priority=metadata.get('priority', 99),
                plugin_class=plugin_class
            )

        except Exception as e:
            print(f"Error loading external plugin {plugin_file}: {e}")
            return None

    def get_categories(self, sort_by_priority: bool = True) -> List[PluginCategory]:
        """Get all categories, optionally sorted by priority."""
        categories = list(self.categories.values())
        if sort_by_priority:
            categories.sort(key=lambda x: x.priority)
        return categories

    def get_tools_by_category(self, category: str) -> List[PluginInfo]:
        """Get all tools in a specific category."""
        if category not in self.categories:
            return []
        return self.categories[category].tools

    def get_enabled_tools(self, category: Optional[str] = None) -> List[PluginInfo]:
        """Get all enabled tools, optionally filtered by category."""
        tools = []
        for plugin_info in self.plugins.values():
            if not plugin_info.enabled:
                continue
            if category and plugin_info.category != category:
                continue
            tools.append(plugin_info)
        return tools

    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Load a plugin instance."""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]

        plugin_info = self.plugins.get(plugin_name)
        if not plugin_info:
            return None

        try:
            # Load plugin class
            if plugin_info.plugin_class:
                # External plugin
                plugin_instance = plugin_info.plugin_class(plugin_info.config_path)
            else:
                # Built-in plugin - import from scanners
                plugin_instance = self._load_builtin_plugin(plugin_info)

            if plugin_instance:
                self.loaded_plugins[plugin_name] = plugin_instance
                return plugin_instance

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")

        return None

    def _load_builtin_plugin(self, plugin_info: PluginInfo) -> Optional[BasePlugin]:
        """Load built-in plugin from scanners module."""
        try:
            # Map plugin names to scanner classes
            scanner_map = {
                'fastapi_security': ('scanners.fastapi_scanner', 'FastAPISecurityScanner'),
                'ai_security': ('scanners.ai_security_scanner', 'AISecurityScanner'),
            }

            if plugin_info.name not in scanner_map:
                return None

            module_path, class_name = scanner_map[plugin_info.name]

            # Import the scanner class
            from importlib import import_module
            module = import_module(f"mcp_code_scanner.{module_path}")
            scanner_class = getattr(module, class_name)

            # Wrap scanner in plugin adapter
            return BuiltinPluginAdapter(scanner_class(), plugin_info)

        except Exception as e:
            print(f"Error loading builtin plugin {plugin_info.name}: {e}")
            return None

    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin configuration."""
        plugin_info = self.plugins.get(plugin_name)
        if not plugin_info or not plugin_info.config_path:
            return {}

        try:
            with open(plugin_info.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def enable_plugin(self, plugin_name: str):
        """Enable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True

    def disable_plugin(self, plugin_name: str):
        """Disable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin."""
        return self.plugins.get(plugin_name)

    def list_plugins(self, category: Optional[str] = None,
                    enabled_only: bool = False) -> List[PluginInfo]:
        """List all plugins with optional filtering."""
        plugins = []
        for plugin_info in self.plugins.values():
            if category and plugin_info.category != category:
                continue
            if enabled_only and not plugin_info.enabled:
                continue
            plugins.append(plugin_info)

        # Sort by priority then name
        plugins.sort(key=lambda x: (x.priority, x.name))
        return plugins


    def _validate_plugins(self):
        """V1-pattern: Comprehensive plugin validation."""
        validation_errors = []

        for plugin_name, plugin_info in self.plugins.items():
            # Validate plugin metadata
            if not plugin_info.name:
                validation_errors.append(f"Plugin {plugin_name}: Missing name")

            if not plugin_info.display_name:
                validation_errors.append(f"Plugin {plugin_name}: Missing display_name")

            if not plugin_info.category:
                validation_errors.append(f"Plugin {plugin_name}: Missing category")

            # Validate category exists
            if plugin_info.category not in self.categories:
                validation_errors.append(f"Plugin {plugin_name}: Unknown category '{plugin_info.category}'")

            # Validate priority range
            if not (1 <= plugin_info.priority <= 100):
                validation_errors.append(f"Plugin {plugin_name}: Priority {plugin_info.priority} out of range (1-100)")

        if validation_errors:
            print("Plugin validation warnings:")
            for error in validation_errors:
                print(f"  - {error}")

    def get_plugins_by_confidence(self, min_confidence: float = 0.8) -> List[PluginInfo]:
        """V1-pattern: Get plugins with high confidence scores."""
        high_confidence_plugins = []

        for plugin_info in self.plugins.values():
            # Load plugin to check confidence if available
            plugin = self.load_plugin(plugin_info.name)
            if plugin and hasattr(plugin, 'get_confidence_score'):
                confidence = plugin.get_confidence_score()
                if confidence >= min_confidence:
                    high_confidence_plugins.append(plugin_info)
            else:
                # Default confidence for plugins without scoring
                high_confidence_plugins.append(plugin_info)

        return high_confidence_plugins

    def get_enhanced_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """V1-pattern: Get comprehensive plugin information with metadata."""
        plugin_info = self.plugins.get(plugin_name)
        if not plugin_info:
            return None

        # Get tool configuration if available
        tool_config = self.config_manager.get_tool_config(plugin_name)

        enhanced_info = {
            "basic_info": {
                "name": plugin_info.name,
                "display_name": plugin_info.display_name,
                "category": plugin_info.category,
                "version": plugin_info.version,
                "description": plugin_info.description,
                "author": plugin_info.author,
                "priority": plugin_info.priority,
                "enabled": plugin_info.enabled
            },
            "configuration": tool_config.to_dict() if tool_config else None,
            "capabilities": {
                "fix_capable": tool_config.fix_capable if tool_config else False,
                "supported_files": tool_config.supported_files if tool_config else [".py"],
                "output_format": tool_config.output_format if tool_config else "text"
            },
            "status": {
                "loaded": plugin_name in self.loaded_plugins,
                "validated": True,  # All plugins go through validation
                "has_parser": self.tool_processor and plugin_name in self.tool_processor.get_supported_tools()
            }
        }

        return enhanced_info

    def create_plugin_from_template(self, plugin_name: str, category: str,
                                  template_type: str = "basic") -> Dict[str, Any]:
        """V2-pattern: Create new plugin from template."""
        try:
            tool_category = ToolCategory(category)
        except ValueError:
            tool_category = ToolCategory.CUSTOM

        # Create tool configuration template
        config_template = self.config_manager.create_tool_config_template(plugin_name, tool_category)

        # Create plugin info template
        plugin_template = {
            "plugin_info": {
                "name": plugin_name,
                "display_name": plugin_name.replace('_', ' ').title(),
                "category": category,
                "version": "1.0.0",
                "description": f"Custom {plugin_name} plugin",
                "author": "MCP Community",
                "priority": 50,
                "enabled": True
            },
            "tool_config": config_template,
            "template_files": {
                f"{plugin_name}_plugin.py": self._generate_plugin_code_template(plugin_name),
                "config.yaml": config_template,
                "README.md": self._generate_plugin_readme_template(plugin_name)
            }
        }

        return plugin_template

    def _generate_plugin_code_template(self, plugin_name: str) -> str:
        """Generate Python code template for new plugin."""
        return f'''"""
{plugin_name.replace('_', ' ').title()} Plugin for MCP Security Scanner.

This plugin was generated from a template and should be customized for your specific tool.
"""

from pathlib import Path
from typing import Dict, List, Any

from mcp_code_scanner.plugins.base_plugin import BasePlugin, PluginResult


class {plugin_name.replace('_', ' ').title().replace(' ', '')}Plugin(BasePlugin):
    """Custom plugin for {plugin_name} tool."""

    PLUGIN_METADATA = {{
        'name': '{plugin_name}',
        'display_name': '{plugin_name.replace('_', ' ').title()}',
        'category': 'custom',
        'version': '1.0.0',
        'description': 'Custom {plugin_name} plugin',
        'author': 'MCP Community'
    }}

    async def scan(self, project_path: Path) -> PluginResult:
        """Perform the plugin's main scanning function."""
        try:
            # TODO: Implement your tool's scanning logic here

            # Example: Run external command
            # result = subprocess.run(['{plugin_name}', str(project_path)],
            #                        capture_output=True, text=True)

            # TODO: Parse tool output and extract issues
            issues = []  # Parse your tool's output here

            return PluginResult(
                plugin_name=self.PLUGIN_METADATA['name'],
                success=True,
                data={{"issues": issues}},
                metadata={{"files_scanned": 0, "execution_time": 0.0}}
            )

        except Exception as e:
            return PluginResult(
                plugin_name=self.PLUGIN_METADATA['name'],
                success=False,
                errors=[str(e)]
            )

    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file extensions."""
        # TODO: Customize for your tool
        return ['.py']

    def is_applicable(self, project_path: Path) -> bool:
        """Check if this plugin is applicable to the given project."""
        # TODO: Add your tool's applicability logic
        return super().is_applicable(project_path)
'''

    def _generate_plugin_readme_template(self, plugin_name: str) -> str:
        """Generate README template for new plugin."""
        return f'''# {plugin_name.replace('_', ' ').title()} Plugin

## Description

This plugin integrates {plugin_name} with the MCP Security Scanner.

## Installation

1. Place this plugin in the `plugins/` directory
2. Configure the tool in `configs/tools/{plugin_name}/config.yaml`
3. Restart the MCP Security Scanner

## Configuration

Edit `config.yaml` to customize:

- `command`: The command to run {plugin_name}
- `args`: Command line arguments
- `supported_files`: File types this tool analyzes
- `timeout`: Maximum execution time

## Usage

The plugin will be automatically discovered and can be used via:

- MCP server tools
- CLI commands
- Direct API calls

## Customization

Edit `{plugin_name}_plugin.py` to:

- Parse tool output
- Extract security issues
- Add tool-specific metadata
- Implement custom validation logic

## Support

For questions or issues, please refer to the MCP Security Scanner documentation.
'''


class BuiltinPluginAdapter(BasePlugin):
    """Adapter to wrap existing scanners as plugins."""

    def __init__(self, scanner, plugin_info: PluginInfo):
        super().__init__(plugin_info.config_path)
        self.scanner = scanner
        self.plugin_info = plugin_info

    async def scan(self, project_path: Path) -> Any:
        """Delegate to the wrapped scanner."""
        if hasattr(self.scanner, 'scan_fastapi_project'):
            return await self.scanner.scan_fastapi_project(project_path)
        elif hasattr(self.scanner, 'scan_ai_project'):
            return await self.scanner.scan_ai_project(project_path)
        else:
            raise NotImplementedError(f"Scanner {type(self.scanner)} doesn't have a scan method")