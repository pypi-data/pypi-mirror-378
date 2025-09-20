"""Theme management for KillerTools."""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages themes across CLI, TUI, and GUI interfaces."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize the theme manager."""
        self.config_dir = config_dir or Path.home() / ".killertools"
        self.config_dir.mkdir(exist_ok=True)
        self.theme_file = self.config_dir / "theme.json"
        self._current_theme = "system"

    def detect_system_theme(self) -> str:
        """Detect the system theme preference."""
        system = platform.system().lower()

        if system == "windows":
            try:
                # Check Windows registry for theme preference
                settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", QSettings.Format.NativeFormat)
                apps_use_light_theme = settings.value("AppsUseLightTheme", 1, type=int)
                return "light" if apps_use_light_theme else "dark"
            except Exception:
                return "light"

        elif system == "darwin":  # macOS
            try:
                # Check macOS appearance setting
                result = os.popen("defaults read -g AppleInterfaceStyle 2>/dev/null").read().strip()
                return "dark" if result == "Dark" else "light"
            except Exception:
                return "light"

        elif system == "linux":
            try:
                # Check GTK theme or environment variables
                gtk_theme = os.environ.get("GTK_THEME", "").lower()
                if "dark" in gtk_theme:
                    return "dark"
                
                # Check for dark mode environment variables
                if any(os.environ.get(var, "").lower() in ["1", "true", "yes"] for var in ["DARK_MODE", "DARK_THEME"]):
                    return "dark"
                    
                return "light"
            except Exception:
                return "light"

        return "light"

    def get_theme_colors(self, theme: str) -> Dict[str, str]:
        """Get color palette for a theme."""
        if theme == "system":
            theme = self.detect_system_theme()

        if theme == "dark":
            return {
                "background": "#1e1e1e",
                "surface": "#2d2d2d",
                "primary": "#7C3AED",
                "secondary": "#06B6D4",
                "accent": "#7C3AED",
                "text": "#ffffff",
                "text_secondary": "#b3b3b3",
                "border": "#404040",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "info": "#3b82f6",
            }
        else:  # light theme
            return {
                "background": "#ffffff",
                "surface": "#f8f9fa",
                "primary": "#7C3AED",
                "secondary": "#06B6D4",
                "accent": "#7C3AED",
                "text": "#1f2937",
                "text_secondary": "#6b7280",
                "border": "#e5e7eb",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "info": "#3b82f6",
            }

    def get_qss_stylesheet(self, theme: str) -> str:
        """Get QSS stylesheet for PyQt6."""
        colors = self.get_theme_colors(theme)
        
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        /* Sidebar */
        QTreeView {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}

        QTreeView::item {{
            padding: 8px;
            border: none;
        }}

        QTreeView::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}

        QTreeView::item:hover {{
            background-color: {colors['border']};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}

        QPushButton:pressed {{
            background-color: {colors['accent']};
        }}

        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['text_secondary']};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 8px;
            border-radius: 4px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['primary']};
        }}

        /* Labels */
        QLabel {{
            color: {colors['text']};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {colors['surface']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border-top: 1px solid {colors['border']};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}

        QMenuBar::item {{
            padding: 4px 8px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}

        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QMenu::item {{
            padding: 8px 16px;
        }}

        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}

        /* Tooltips */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px;
        }}
        """

    def save_theme(self, theme: str) -> None:
        """Save the current theme to file."""
        self._current_theme = theme
        theme_data = {"theme": theme}
        
        with open(self.theme_file, "w", encoding="utf-8") as f:
            json.dump(theme_data, f, indent=2)

    def load_theme(self) -> str:
        """Load the saved theme from file."""
        if not self.theme_file.exists():
            return "system"

        try:
            with open(self.theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)
            return theme_data.get("theme", "system")
        except Exception:
            return "system"

    def get_current_theme(self) -> str:
        """Get the current theme."""
        return self._current_theme

    def apply_theme_to_app(self, app: QApplication, theme: str) -> None:
        """Apply theme to a QApplication."""
        if theme == "system":
            theme = self.detect_system_theme()

        stylesheet = self.get_qss_stylesheet(theme)
        app.setStyleSheet(stylesheet)
        
        # Set application palette for better integration
        palette = QPalette()
        colors = self.get_theme_colors(theme)
        
        if theme == "dark":
            palette.setColor(QPalette.ColorRole.Window, colors["background"])
            palette.setColor(QPalette.ColorRole.WindowText, colors["text"])
            palette.setColor(QPalette.ColorRole.Base, colors["surface"])
            palette.setColor(QPalette.ColorRole.AlternateBase, colors["background"])
            palette.setColor(QPalette.ColorRole.ToolTipBase, colors["surface"])
            palette.setColor(QPalette.ColorRole.ToolTipText, colors["text"])
            palette.setColor(QPalette.ColorRole.Text, colors["text"])
            palette.setColor(QPalette.ColorRole.Button, colors["surface"])
            palette.setColor(QPalette.ColorRole.ButtonText, colors["text"])
            palette.setColor(QPalette.ColorRole.BrightText, colors["error"])
            palette.setColor(QPalette.ColorRole.Link, colors["primary"])
            palette.setColor(QPalette.ColorRole.Highlight, colors["primary"])
            palette.setColor(QPalette.ColorRole.HighlightedText, colors["text"])
        else:  # light theme
            palette.setColor(QPalette.ColorRole.Window, colors["background"])
            palette.setColor(QPalette.ColorRole.WindowText, colors["text"])
            palette.setColor(QPalette.ColorRole.Base, colors["surface"])
            palette.setColor(QPalette.ColorRole.AlternateBase, colors["background"])
            palette.setColor(QPalette.ColorRole.ToolTipBase, colors["surface"])
            palette.setColor(QPalette.ColorRole.ToolTipText, colors["text"])
            palette.setColor(QPalette.ColorRole.Text, colors["text"])
            palette.setColor(QPalette.ColorRole.Button, colors["surface"])
            palette.setColor(QPalette.ColorRole.ButtonText, colors["text"])
            palette.setColor(QPalette.ColorRole.BrightText, colors["error"])
            palette.setColor(QPalette.ColorRole.Link, colors["primary"])
            palette.setColor(QPalette.ColorRole.Highlight, colors["primary"])
            palette.setColor(QPalette.ColorRole.HighlightedText, colors["text"])

        app.setPalette(palette)
