#!/usr/bin/env python3
"""Simple CLI application for KillerTools without Typer."""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from killer_tools import __version__
from killer_tools.core.logging import setup_logging
from killer_tools.core.plugin import registry
from killer_tools.core.settings import Settings

console = Console()

def show_version():
    """Show version information."""
    console.print(f"KillerTools v{__version__}")

def show_info():
    """Show KillerTools information."""
    info_text = Text()
    info_text.append("KillerTools\n", style="bold blue")
    info_text.append(f"Version: {__version__}\n")
    info_text.append("A modern, cross-platform Swiss-army toolkit for developers and makers\n\n")
    
    info_text.append("Features:\n", style="bold")
    info_text.append("• CLI interface with rich output\n")
    info_text.append("• TUI dashboard (killertools tui)\n")
    info_text.append("• GUI application (killertools gui)\n")
    info_text.append("• Plugin architecture for extensibility\n")
    info_text.append("• Cross-platform support\n")
    info_text.append("• Theme support (system/light/dark)\n\n")
    
    info_text.append("Quick Start:\n", style="bold")
    info_text.append("killertools list-plugins    # List available plugins\n")
    info_text.append("killertools tui             # Launch TUI dashboard\n")
    info_text.append("killertools gui             # Launch GUI application\n")
    
    panel = Panel(info_text, title="KillerTools Information", border_style="green")
    console.print(panel)

def list_plugins():
    """List all available plugins."""
    # Discover and register plugins
    registry.discover_plugins()
    plugins = registry.list_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    table = Table(title="Available KillerTools Plugins")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Summary", style="magenta")
    table.add_column("Version", style="green")

    for plugin in plugins:
        table.add_row(plugin.name, plugin.summary, getattr(plugin, 'version', '1.0.0'))
    
    console.print(table)

def run_plugin(plugin_name: str):
    """Run a specific plugin."""
    # Discover plugins first
    registry.discover_plugins()
    
    # Debug: show all available plugin names
    available_plugins = [p.name for p in registry.list_plugins()]
    console.print(f"Available plugins: {available_plugins}")
    
    plugin = registry.get_plugin(plugin_name)
    if not plugin:
        console.print(f"[red]Plugin '{plugin_name}' not found.[/red]")
        console.print("Use 'killertools list-plugins' to see available plugins.")
        return

    try:
        plugin.run_cli(console)
    except Exception as e:
        console.print(f"[red]Error running plugin '{plugin_name}': {e}[/red]")

def launch_tui():
    """Launch the TUI dashboard."""
    console.print("[yellow]TUI dashboard launching...[/yellow]")
    console.print("Note: TUI functionality will be implemented in a future version")

def launch_gui():
    """Launch the GUI application."""
    console.print("[yellow]GUI application launching...[/yellow]")
    console.print("Note: GUI functionality will be implemented in a future version")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="A modern, cross-platform Swiss-army toolkit for developers and makers",
        prog="killertools"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--theme",
        choices=["system", "light", "dark"],
        default="system",
        help="Theme mode (default: system)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    subparsers.add_parser("info", help="Show KillerTools information")
    
    # List plugins command
    subparsers.add_parser("list-plugins", help="List all available plugins")
    
    # Run plugin command
    run_parser = subparsers.add_parser("run", help="Run a specific plugin")
    run_parser.add_argument("plugin_name", help="Name of the plugin to run")
    
    # TUI command
    subparsers.add_parser("tui", help="Launch the TUI dashboard")
    
    # GUI command
    subparsers.add_parser("gui", help="Launch the GUI application")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, console=console)
    
    # Apply theme settings
    if args.theme != "system":
        settings = Settings()
        settings.theme.mode = args.theme
        settings.save_to_file()
    
    # Handle version
    if args.version:
        show_version()
        return
    
    # Handle commands
    if args.command == "info":
        show_info()
    elif args.command == "list-plugins":
        list_plugins()
    elif args.command == "run":
        run_plugin(args.plugin_name)
    elif args.command == "tui":
        launch_tui()
    elif args.command == "gui":
        launch_gui()
    else:
        # No command specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()
