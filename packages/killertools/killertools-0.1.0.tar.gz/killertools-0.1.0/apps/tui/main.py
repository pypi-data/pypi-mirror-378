"""Main TUI application for KillerTools."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static, Tree
from textual.widgets.tree import TreeNode

from killer_tools.core.plugin import registry
from killer_tools.core.settings import Settings
from killer_tools.core.theme import ThemeManager


class PluginTile(Static):
    """A tile widget for displaying plugin information."""

    def __init__(self, plugin_name: str, plugin_summary: str, plugin_version: str) -> None:
        """Initialize the plugin tile."""
        super().__init__()
        self.plugin_name = plugin_name
        self.plugin_summary = plugin_summary
        self.plugin_version = plugin_version

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static(f"[bold blue]{self.plugin_name}[/bold blue] v{self.plugin_version}")
        yield Static(f"[dim]{self.plugin_summary}[/dim]")
        yield Button("Run", id=f"run-{self.plugin_name}")


class KillerToolsTUI(App):
    """Main TUI application for KillerTools."""

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }

    .main-container {
        layout: horizontal;
        height: 1fr;
    }

    .sidebar {
        width: 25%;
        border: solid $primary;
        margin: 1;
    }

    .content {
        width: 75%;
        margin: 1;
    }

    .plugin-grid {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
    }

    PluginTile {
        height: 8;
        border: solid $secondary;
        margin: 1;
        padding: 1;
    }

    .welcome {
        text-align: center;
        margin: 2;
    }

    .status {
        dock: bottom;
        height: 3;
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "home", "Home"),
        ("l", "list_plugins", "List Plugins"),
        ("t", "toggle_theme", "Toggle Theme"),
        ("/", "search", "Search"),
        ("f1", "help", "Help"),
    ]

    def __init__(self) -> None:
        """Initialize the TUI app."""
        super().__init__()
        self.settings = Settings.load_from_file()
        self.theme_manager = ThemeManager()
        self.current_theme = "dark"
        self.plugins = []

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        
        with Container(classes="main-container"):
            with Container(classes="sidebar"):
                yield Tree("Plugins", id="plugin-tree")
            
            with Container(classes="content"):
                yield Static("Welcome to KillerTools TUI!", classes="welcome")
                yield Container(id="plugin-grid", classes="plugin-grid")
        
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Discover and register plugins
        registry.discover_plugins()
        self.plugins = registry.list_plugins()
        
        # Populate plugin tree
        plugin_tree = self.query_one("#plugin-tree", Tree)
        for plugin in self.plugins:
            plugin_tree.root.add(plugin.name, data=plugin)
        
        # Create plugin tiles
        self.create_plugin_tiles()

    def create_plugin_tiles(self) -> None:
        """Create tiles for all plugins."""
        plugin_grid = self.query_one("#plugin-grid", Container)
        plugin_grid.remove_children()
        
        for plugin in self.plugins:
            tile = PluginTile(
                plugin_name=plugin.name,
                plugin_summary=plugin.summary,
                plugin_version=plugin.version,
            )
            plugin_grid.mount(tile)

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_home(self) -> None:
        """Go to home screen."""
        self.create_plugin_tiles()

    def action_list_plugins(self) -> None:
        """List all plugins."""
        self.create_plugin_tiles()

    def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.dark = self.current_theme == "dark"

    def action_search(self) -> None:
        """Open search dialog."""
        # TODO: Implement search functionality
        self.notify("Search functionality coming soon!", severity="information")

    def action_help(self) -> None:
        """Show help dialog."""
        help_text = """
KillerTools TUI Help

Key Bindings:
• q - Quit application
• h - Go to home screen
• l - List plugins
• t - Toggle theme
• / - Search plugins
• F1 - Show this help

Navigation:
• Use Tab to navigate between widgets
• Use Enter to activate buttons
• Use arrow keys to navigate the plugin tree
        """
        self.notify(help_text, severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id and button_id.startswith("run-"):
            plugin_name = button_id[4:]  # Remove "run-" prefix
            self.run_plugin(plugin_name)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle plugin tree selection."""
        if event.node.data:
            plugin = event.node.data
            self.notify(f"Selected plugin: {plugin.name}", severity="information")

    def run_plugin(self, plugin_name: str) -> None:
        """Run a specific plugin."""
        plugin = registry.get_plugin(plugin_name)
        if plugin:
            self.notify(f"Running plugin: {plugin_name}", severity="information")
            # TODO: Implement plugin execution in TUI
        else:
            self.notify(f"Plugin not found: {plugin_name}", severity="error")


def main() -> None:
    """Main entry point for TUI application."""
    app = KillerToolsTUI()
    app.run()


if __name__ == "__main__":
    main()
