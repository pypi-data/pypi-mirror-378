"""Main GUI application for KillerTools."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from killer_tools import __version__
from killer_tools.core.logging import setup_logging
from killer_tools.core.plugin import registry
from killer_tools.core.settings import Settings
from killer_tools.core.theme import ThemeManager


class AboutDialog(QMessageBox):
    """About dialog for KillerTools."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the about dialog."""
        super().__init__(parent)
        self.setWindowTitle("About KillerTools")
        self.setIcon(QMessageBox.Icon.Information)
        
        about_text = f"""
        <h2>KillerTools v{__version__}</h2>
        <p>A modern, cross-platform Swiss-army toolkit for developers and makers</p>
        
        <h3>Features:</h3>
        <ul>
        <li>CLI interface with rich output</li>
        <li>TUI dashboard</li>
        <li>GUI application</li>
        <li>Plugin architecture for extensibility</li>
        <li>Cross-platform support</li>
        <li>Theme support (system/light/dark)</li>
        </ul>
        
        <h3>Links:</h3>
        <p>
        <a href="https://github.com/VoxHash/KillerTools">GitHub</a> |
        <a href="https://voxhash.github.io/KillerTools">Documentation</a> |
        <a href="https://twitter.com/VoxHash">Twitter</a> |
        <a href="https://linkedin.com/in/voxhash">LinkedIn</a> |
        <a href="https://t.me/VoxHash">Telegram</a>
        </p>
        
        <p><b>Author:</b> Silas Renner (VoxHash)<br>
        <b>Email:</b> contact@voxhash.dev<br>
        <b>License:</b> MIT</p>
        """
        
        self.setText(about_text)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)


class PluginWidget(QWidget):
    """Base widget for plugin content."""

    def __init__(self, plugin_name: str, parent: Optional[QWidget] = None) -> None:
        """Initialize the plugin widget."""
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the plugin UI."""
        layout = QVBoxLayout()
        
        # Plugin header
        header = QLabel(f"Plugin: {self.plugin_name}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Plugin content placeholder
        content = QLabel("Plugin content will be displayed here")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(content)
        
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main window for KillerTools GUI."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.settings = Settings.load_from_file()
        self.theme_manager = ThemeManager()
        self.plugins = []
        self.current_plugin = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.load_plugins()
        self.apply_theme()

    def setup_ui(self) -> None:
        """Set up the main UI."""
        self.setWindowTitle(f"KillerTools v{__version__}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Splitter for sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar with plugin tree
        self.setup_sidebar(splitter)
        
        # Content area
        self.setup_content_area(splitter)
        
        # Set splitter proportions
        splitter.setSizes([250, 950])

    def setup_sidebar(self, parent: QSplitter) -> None:
        """Set up the sidebar with plugin tree."""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        
        # Plugin tree
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabel("Plugins")
        self.plugin_tree.itemClicked.connect(self.on_plugin_selected)
        sidebar_layout.addWidget(self.plugin_tree)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Plugins")
        refresh_btn.clicked.connect(self.load_plugins)
        sidebar_layout.addWidget(refresh_btn)
        
        parent.addWidget(sidebar_widget)

    def setup_content_area(self, parent: QSplitter) -> None:
        """Set up the content area."""
        self.content_stack = QStackedWidget()
        parent.addWidget(self.content_stack)
        
        # Welcome widget
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_widget.setLayout(welcome_layout)
        
        welcome_label = QLabel("Welcome to KillerTools!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        welcome_layout.addWidget(welcome_label)
        
        info_label = QLabel(
            "Select a plugin from the sidebar to get started.\n\n"
            "KillerTools provides a comprehensive set of utilities for developers and makers, "
            "including file management, media processing, network tools, cryptography, and more."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 14px; margin: 20px; color: gray;")
        welcome_layout.addWidget(info_label)
        
        self.content_stack.addWidget(welcome_widget)

    def setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QAction("&Refresh Plugins", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.load_plugins)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")
        
        system_theme_action = QAction("&System", self)
        system_theme_action.setCheckable(True)
        system_theme_action.triggered.connect(lambda: self.set_theme("system"))
        theme_menu.addAction(system_theme_action)
        
        light_theme_action = QAction("&Light", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        # Store theme actions for updating check state
        self.theme_actions = {
            "system": system_theme_action,
            "light": light_theme_action,
            "dark": dark_theme_action,
        }
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self) -> None:
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def load_plugins(self) -> None:
        """Load and register all plugins."""
        # Discover and register plugins
        registry.discover_plugins()
        self.plugins = registry.list_plugins()
        
        # Clear existing tree items
        self.plugin_tree.clear()
        
        # Add plugins to tree
        for plugin in self.plugins:
            item = QTreeWidgetItem([plugin.name])
            item.setData(0, Qt.ItemDataRole.UserRole, plugin)
            self.plugin_tree.addTopLevelItem(item)
        
        self.status_bar.showMessage(f"Loaded {len(self.plugins)} plugins")

    def on_plugin_selected(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle plugin selection."""
        plugin = item.data(0, Qt.ItemDataRole.UserRole)
        if plugin:
            self.show_plugin(plugin)

    def show_plugin(self, plugin) -> None:
        """Show a plugin widget."""
        # Check if widget already exists
        for i in range(self.content_stack.count()):
            widget = self.content_stack.widget(i)
            if isinstance(widget, PluginWidget) and widget.plugin_name == plugin.name:
                self.content_stack.setCurrentWidget(widget)
                return
        
        # Create new plugin widget
        plugin_widget = PluginWidget(plugin.name)
        self.content_stack.addWidget(plugin_widget)
        self.content_stack.setCurrentWidget(plugin_widget)
        
        self.current_plugin = plugin
        self.status_bar.showMessage(f"Selected plugin: {plugin.name}")

    def set_theme(self, theme: str) -> None:
        """Set the application theme."""
        self.settings.theme.mode = theme
        self.settings.save_to_file()
        self.apply_theme()
        
        # Update theme action check states
        for theme_name, action in self.theme_actions.items():
            action.setChecked(theme_name == theme)

    def apply_theme(self) -> None:
        """Apply the current theme to the application."""
        theme = self.settings.theme.mode
        self.theme_manager.apply_theme_to_app(QApplication.instance(), theme)

    def show_about(self) -> None:
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def closeEvent(self, event) -> None:
        """Handle application close event."""
        # Save settings
        self.settings.save_to_file()
        event.accept()


def main() -> None:
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("KillerTools")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("VoxHash")
    
    # Set up logging
    setup_logging(level="INFO")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
