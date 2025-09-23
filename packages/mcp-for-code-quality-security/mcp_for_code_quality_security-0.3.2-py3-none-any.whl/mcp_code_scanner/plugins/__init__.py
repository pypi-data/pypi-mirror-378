"""
Plugin discovery and management system (V3 architectural pattern).
"""

from .plugin_manager import PluginManager, PluginCategory, PluginInfo
from .base_plugin import BasePlugin, PluginResult

__all__ = [
    'PluginManager',
    'PluginCategory',
    'PluginInfo',
    'BasePlugin',
    'PluginResult'
]