"""DevTools plugin implementation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
import yaml
from rich.console import Console
from PyQt6.QtWidgets import QWidget
from textual.app import App

from killer_tools.core.plugin import Plugin


class DevToolsPlugin(Plugin):
    """Plugin for developer tools and utilities."""

    name = "devtools"
    summary = "JSON/YAML/TOML formatters, regex tester, .env parser, and README generators"
    version = "1.0.0"

    def run_cli(self, console: Console, **kwargs: Any) -> None:
        """Run the devtools plugin in CLI mode."""
        console.print("[bold blue]DevTools Plugin[/bold blue]")
        console.print("Available operations:")
        console.print("• format-json <file> - Format JSON file")
        console.print("• format-yaml <file> - Format YAML file")
        console.print("• format-toml <file> - Format TOML file")
        console.print("• validate-json <file> - Validate JSON file")
        console.print("• regex-test <pattern> <text> - Test regex pattern")
        console.print("• parse-env <file> - Parse .env file")
        console.print("• generate-readme - Generate README with badges")

    def tui_view(self) -> Optional[App]:
        """Return a Textual app for TUI mode."""
        return None

    def gui_widget(self) -> Optional[QWidget]:
        """Return a PyQt6 widget for GUI mode."""
        return None

    def format_json(self, file_path: Path, indent: int = 2) -> str:
        """Format JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            return f"Error formatting JSON: {e}"

    def format_yaml(self, file_path: Path) -> str:
        """Format YAML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except Exception as e:
            return f"Error formatting YAML: {e}"

    def format_toml(self, file_path: Path) -> str:
        """Format TOML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            return toml.dumps(data)
        except Exception as e:
            return f"Error formatting TOML: {e}"

    def validate_json(self, file_path: Path) -> Dict[str, Any]:
        """Validate JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return {"valid": True, "error": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def test_regex(self, pattern: str, text: str) -> Dict[str, Any]:
        """Test regex pattern against text."""
        try:
            regex = re.compile(pattern)
            matches = regex.findall(text)
            return {
                "valid": True,
                "matches": matches,
                "match_count": len(matches),
                "error": None
            }
        except Exception as e:
            return {
                "valid": False,
                "matches": [],
                "match_count": 0,
                "error": str(e)
            }

    def parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """Parse .env file."""
        env_vars = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip()
                        else:
                            print(f"Warning: Invalid line {line_num}: {line}")
        except Exception as e:
            print(f"Error parsing .env file: {e}")
        return env_vars

    def generate_readme_badges(self, project_name: str, github_user: str) -> str:
        """Generate README badges for a project."""
        badges = [
            f"[![CI](https://github.com/{github_user}/{project_name}/workflows/CI/badge.svg)](https://github.com/{github_user}/{project_name}/actions)",
            f"[![Coverage](https://codecov.io/gh/{github_user}/{project_name}/branch/main/graph/badge.svg)](https://codecov.io/gh/{github_user}/{project_name})",
            f"[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)",
            f"[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)",
            f"[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)",
        ]
        return "\n".join(badges)


# Create plugin instance
plugin = DevToolsPlugin()
