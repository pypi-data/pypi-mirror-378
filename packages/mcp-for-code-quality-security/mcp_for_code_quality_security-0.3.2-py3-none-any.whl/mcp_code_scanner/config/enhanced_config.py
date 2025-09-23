"""
V2-pattern simple configuration loading with V3-style category grouping.

Incorporates learnings from experimental v2/v3 projects for clean configuration management.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class ToolCategory(Enum):
    """Tool categories for organization."""
    SECURITY = "security"
    QUALITY = "quality"
    FORMATTING = "formatting"
    TESTING = "testing"
    TYPING = "typing"
    DOCUMENTATION = "documentation"
    CUSTOM = "custom"


@dataclass
class ToolConfig:
    """V2-pattern: Simple individual tool configuration."""
    name: str
    display_name: str
    category: ToolCategory
    enabled: bool = True
    command: str = ""
    args: List[str] = field(default_factory=list)
    config_file: Optional[str] = None
    supported_files: List[str] = field(default_factory=lambda: [".py"])
    output_format: str = "text"
    priority: int = 50
    timeout: int = 300
    fix_capable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, config_path: Path) -> 'ToolConfig':
        """V2-pattern: Load simple YAML configuration."""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            name=data['name'],
            display_name=data['display_name'],
            category=ToolCategory(data['category']),
            enabled=data.get('enabled', True),
            command=data.get('command', ''),
            args=data.get('args', []),
            config_file=data.get('config_file'),
            supported_files=data.get('supported_files', ['.py']),
            output_format=data.get('output_format', 'text'),
            priority=data.get('priority', 50),
            timeout=data.get('timeout', 300),
            fix_capable=data.get('fix_capable', False),
            metadata=data.get('metadata', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'category': self.category.value,
            'enabled': self.enabled,
            'command': self.command,
            'args': self.args,
            'config_file': self.config_file,
            'supported_files': self.supported_files,
            'output_format': self.output_format,
            'priority': self.priority,
            'timeout': self.timeout,
            'fix_capable': self.fix_capable,
            'metadata': self.metadata
        }

    def is_applicable(self, file_path: Path) -> bool:
        """Check if tool is applicable to given file."""
        file_suffix = file_path.suffix
        return file_suffix in self.supported_files


@dataclass
class CategoryConfig:
    """V3-pattern: Category-based organization configuration."""
    name: str
    display_name: str
    description: str
    icon: str
    priority: int
    enabled: bool = True
    tools: List[ToolConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, config_path: Path) -> 'CategoryConfig':
        """Load category configuration from YAML."""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            name=data['name'],
            display_name=data['display_name'],
            description=data['description'],
            icon=data.get('icon', '🔧'),
            priority=data.get('priority', 50),
            enabled=data.get('enabled', True),
            metadata=data.get('metadata', {})
        )


class EnhancedConfigManager:
    """
    V2+V3-pattern: Simple per-tool configs with category-based organization.

    Features from v2:
    - Simple YAML per tool
    - Clean configuration loading
    - Individual tool focus

    Features from v3:
    - Category-based organization
    - Priority-based ordering
    - Dynamic discovery
    """

    def __init__(self, config_root: Path):
        self.config_root = Path(config_root)
        self.categories: Dict[str, CategoryConfig] = {}
        self.tools: Dict[str, ToolConfig] = {}
        self._discover_configurations()

    def _discover_configurations(self):
        """V2+V3 pattern: Discover configurations from directory structure."""
        # Step 1: Discover categories (V3 pattern)
        self._discover_categories()

        # Step 2: Discover individual tool configs (V2 pattern)
        self._discover_tools()

        # Step 3: Organize tools by category
        self._organize_tools_by_category()

    def _discover_categories(self):
        """V3-pattern: Discover category configurations."""
        categories_dir = self.config_root / "categories"
        if not categories_dir.exists():
            # Create default categories if none exist
            self._create_default_categories()
            return

        for category_file in categories_dir.glob("*.yaml"):
            try:
                category_config = CategoryConfig.from_yaml(category_file)
                self.categories[category_config.name] = category_config
            except Exception as e:
                print(f"Warning: Failed to load category {category_file}: {e}")

    def _discover_tools(self):
        """V2-pattern: Discover individual tool configurations."""
        tools_dir = self.config_root / "tools"
        if not tools_dir.exists():
            return

        # V2 pattern: Each tool has its own directory with config.yaml
        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue

            config_file = tool_dir / "config.yaml"
            if config_file.exists():
                try:
                    tool_config = ToolConfig.from_yaml(config_file)
                    self.tools[tool_config.name] = tool_config
                except Exception as e:
                    print(f"Warning: Failed to load tool config {config_file}: {e}")

    def _organize_tools_by_category(self):
        """V3-pattern: Organize tools by category with priority ordering."""
        for tool_config in self.tools.values():
            category_name = tool_config.category.value
            if category_name in self.categories:
                self.categories[category_name].tools.append(tool_config)

        # Sort tools within each category by priority
        for category in self.categories.values():
            category.tools.sort(key=lambda t: (t.priority, t.name))

    def _create_default_categories(self):
        """Create default categories if none exist."""
        default_categories = [
            CategoryConfig(
                name="security",
                display_name="Security Analysis",
                description="Security vulnerability detection and analysis",
                icon="🛡️",
                priority=10
            ),
            CategoryConfig(
                name="quality",
                display_name="Code Quality",
                description="Code quality analysis and linting",
                icon="📊",
                priority=20
            ),
            CategoryConfig(
                name="formatting",
                display_name="Code Formatting",
                description="Code formatting and style checking",
                icon="✨",
                priority=30
            ),
            CategoryConfig(
                name="typing",
                display_name="Type Checking",
                description="Static type analysis and validation",
                icon="🔍",
                priority=40
            ),
            CategoryConfig(
                name="testing",
                display_name="Testing",
                description="Test execution and coverage analysis",
                icon="🧪",
                priority=50
            )
        ]

        for category in default_categories:
            self.categories[category.name] = category

    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """V2-pattern: Get simple tool configuration."""
        return self.tools.get(tool_name)

    def get_category_config(self, category_name: str) -> Optional[CategoryConfig]:
        """V3-pattern: Get category configuration."""
        return self.categories.get(category_name)

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolConfig]:
        """V3-pattern: Get tools organized by category."""
        category_name = category.value
        if category_name in self.categories:
            return self.categories[category_name].tools
        return []

    def get_enabled_tools(self, category: Optional[ToolCategory] = None) -> List[ToolConfig]:
        """Get enabled tools, optionally filtered by category."""
        tools = []
        for tool in self.tools.values():
            if not tool.enabled:
                continue
            if category and tool.category != category:
                continue
            tools.append(tool)

        # Sort by priority
        tools.sort(key=lambda t: (t.priority, t.name))
        return tools

    def get_tools_for_file(self, file_path: Path) -> List[ToolConfig]:
        """Get applicable tools for a specific file."""
        applicable_tools = []
        for tool in self.get_enabled_tools():
            if tool.is_applicable(file_path):
                applicable_tools.append(tool)
        return applicable_tools

    def get_categories_by_priority(self) -> List[CategoryConfig]:
        """V3-pattern: Get categories sorted by priority."""
        categories = list(self.categories.values())
        categories.sort(key=lambda c: (c.priority, c.name))
        return categories

    def enable_tool(self, tool_name: str):
        """Enable a specific tool."""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = True

    def disable_tool(self, tool_name: str):
        """Disable a specific tool."""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = False

    def enable_category(self, category_name: str):
        """Enable all tools in a category."""
        if category_name in self.categories:
            self.categories[category_name].enabled = True
            for tool in self.categories[category_name].tools:
                tool.enabled = True

    def disable_category(self, category_name: str):
        """Disable all tools in a category."""
        if category_name in self.categories:
            self.categories[category_name].enabled = False
            for tool in self.categories[category_name].tools:
                tool.enabled = False

    def create_tool_config_template(self, tool_name: str, category: ToolCategory) -> Dict[str, Any]:
        """V2-pattern: Create template for new tool configuration."""
        return {
            'name': tool_name,
            'display_name': tool_name.replace('_', ' ').title(),
            'category': category.value,
            'enabled': True,
            'command': tool_name,
            'args': [],
            'config_file': None,
            'supported_files': ['.py'],
            'output_format': 'text',
            'priority': 50,
            'timeout': 300,
            'fix_capable': False,
            'metadata': {
                'description': f'{tool_name} tool configuration',
                'version': '1.0.0',
                'author': 'MCP Security Scanner'
            }
        }

    def save_tool_config(self, tool_config: ToolConfig):
        """V2-pattern: Save individual tool configuration."""
        tool_dir = self.config_root / "tools" / tool_config.name
        tool_dir.mkdir(parents=True, exist_ok=True)

        config_file = tool_dir / "config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(tool_config.to_dict(), f, default_flow_style=False, sort_keys=False)

        # Update in-memory configuration
        self.tools[tool_config.name] = tool_config

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            'total_categories': len(self.categories),
            'total_tools': len(self.tools),
            'enabled_tools': len(self.get_enabled_tools()),
            'categories': {
                name: {
                    'enabled': config.enabled,
                    'tool_count': len(config.tools),
                    'priority': config.priority
                }
                for name, config in self.categories.items()
            },
            'tools_by_category': {
                category.value: len(self.get_tools_by_category(category))
                for category in ToolCategory
            }
        }