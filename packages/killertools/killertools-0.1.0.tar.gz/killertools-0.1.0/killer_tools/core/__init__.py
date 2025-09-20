"""Core functionality for KillerTools."""

from killer_tools.core.plugin import Plugin, PluginRegistry
from killer_tools.core.settings import Settings
from killer_tools.core.theme import ThemeManager
from killer_tools.core.logging import setup_logging

__all__ = ["Plugin", "PluginRegistry", "Settings", "ThemeManager", "setup_logging"]
