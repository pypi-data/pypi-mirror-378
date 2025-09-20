"""Plugin architecture for KillerTools."""

from __future__ import annotations

import importlib
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Type, runtime_checkable

from rich.console import Console
from textual.app import App
from PyQt6.QtWidgets import QWidget


@runtime_checkable
class Plugin(Protocol):
    """Protocol defining the interface for KillerTools plugins."""

    name: str
    """The plugin name."""

    summary: str
    """A brief description of what the plugin does."""

    version: str
    """The plugin version."""

    @abstractmethod
    def run_cli(self, console: Console, **kwargs: Any) -> None:
        """Run the plugin in CLI mode."""
        ...

    def tui_view(self) -> Optional[App]:
        """Return a Textual app for TUI mode. Optional."""
        return None

    def gui_widget(self) -> Optional[QWidget]:
        """Return a PyQt6 widget for GUI mode. Optional."""
        return None


class PluginRegistry:
    """Registry for managing KillerTools plugins."""

    def __init__(self) -> None:
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Plugin] = {}
        self._console = Console()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        if plugin.name in self._plugins:
            self._console.print(f"[yellow]Warning: Plugin '{plugin.name}' is already registered[/yellow]")
            return

        self._plugins[plugin.name] = plugin
        self._console.print(f"[green]Registered plugin: {plugin.name} v{plugin.version}[/green]")

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> List[Plugin]:
        """List all registered plugins."""
        return list(self._plugins.values())

    def discover_plugins(self) -> None:
        """Auto-discover and register plugins from the plugins package."""
        plugins_package = "killer_tools.plugins"
        
        try:
            package = importlib.import_module(plugins_package)
            package_path = Path(package.__file__).parent  # type: ignore
            
            for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
                if ispkg:
                    module_name = f"{plugins_package}.{name}.plugin"
                    try:
                        module = importlib.import_module(module_name)
                        
                        # Look for plugins in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                isinstance(attr, type)
                                and hasattr(attr, "name")
                                and hasattr(attr, "summary")
                                and hasattr(attr, "version")
                                and hasattr(attr, "run_cli")
                                and not attr_name.startswith("_")
                                and attr_name.endswith("Plugin")
                            ):
                                try:
                                    plugin_instance = attr()
                                    if isinstance(plugin_instance, Plugin):
                                        self.register(plugin_instance)
                                        self._console.print(f"Registered plugin: {plugin_instance.name} v{plugin_instance.version}")
                                except Exception as e:
                                    self._console.print(f"[red]Failed to instantiate plugin {attr_name}: {e}[/red]")
                                    
                    except Exception as e:
                        self._console.print(f"[red]Failed to import plugin module {module_name}: {e}[/red]")
                        
        except Exception as e:
            self._console.print(f"[red]Failed to discover plugins: {e}[/red]")

    def run_plugin_cli(self, name: str, **kwargs: Any) -> bool:
        """Run a plugin in CLI mode."""
        plugin = self.get_plugin(name)
        if not plugin:
            self._console.print(f"[red]Plugin '{name}' not found[/red]")
            return False

        try:
            plugin.run_cli(self._console, **kwargs)
            return True
        except Exception as e:
            self._console.print(f"[red]Error running plugin '{name}': {e}[/red]")
            return False


# Global plugin registry instance
registry = PluginRegistry()
