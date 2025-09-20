"""KillerTools - A modern, cross-platform Swiss-army toolkit for developers and makers."""

__version__ = "0.1.1"
__author__ = "Silas Renner (VoxHash)"
__email__ = "contact@voxhash.dev"
__license__ = "MIT"

from killer_tools.core.plugin import PluginRegistry
from killer_tools.core.settings import Settings

__all__ = ["__version__", "__author__", "__email__", "__license__", "PluginRegistry", "Settings"]
