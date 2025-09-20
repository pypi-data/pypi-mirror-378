"""Main CLI application for KillerTools."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from killer_tools import __version__
from killer_tools.core.logging import setup_logging
from killer_tools.core.plugin import registry
from killer_tools.core.settings import Settings

# Initialize console
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="killertools",
    help="A modern, cross-platform Swiss-army toolkit for developers and makers",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Global settings
settings = Settings.load_from_file()


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"KillerTools v{__version__}")


@app.command()
def list_plugins() -> None:
    """List all available plugins."""
    # Discover and register plugins
    registry.discover_plugins()
    plugins = registry.list_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    console.print("\n[bold]Available Plugins:[/bold]\n")
    
    for plugin in plugins:
        panel = Panel(
            f"[bold]{plugin.name}[/bold] v{plugin.version}\n{plugin.summary}",
            title=f"Plugin: {plugin.name}",
            border_style="blue",
        )
        console.print(panel)


@app.command()
def info() -> None:
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


@app.command()
def tui() -> None:
    """Launch the TUI dashboard."""
    console.print("[yellow]TUI dashboard launching...[/yellow]")
    console.print("Note: TUI functionality will be implemented in a future version")


@app.command()
def gui() -> None:
    """Launch the GUI application."""
    console.print("[yellow]GUI application launching...[/yellow]")
    console.print("Note: GUI functionality will be implemented in a future version")


if __name__ == "__main__":
    app()