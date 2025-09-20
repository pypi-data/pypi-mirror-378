"""Files plugin implementation."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from textual.app import App
from PyQt6.QtWidgets import QWidget

from killer_tools.core.plugin import Plugin


class FilesPlugin(Plugin):
    """Plugin for file operations and utilities."""

    name = "files"
    summary = "File operations, hashing, duplicate detection, and bulk operations"
    version = "1.0.0"

    def run_cli(self, console: Console, **kwargs: Any) -> None:
        """Run the files plugin in CLI mode."""
        console.print("[bold blue]Files Plugin[/bold blue]")
        console.print("Available operations:")
        console.print("• hash <file> - Calculate file hash")
        console.print("• find-duplicates <directory> - Find duplicate files")
        console.print("• bulk-rename <pattern> <replacement> - Bulk rename files")
        console.print("• tree-size <directory> - Show directory tree with sizes")

    def tui_view(self) -> Optional[App]:
        """Return a Textual app for TUI mode."""
        return None

    def gui_widget(self) -> Optional[QWidget]:
        """Return a PyQt6 widget for GUI mode."""
        return None

    def hash_file(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate hash of a file."""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def find_duplicates(self, directory: Path) -> Dict[str, List[Path]]:
        """Find duplicate files in a directory."""
        file_hashes: Dict[str, List[Path]] = {}
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    file_hash = self.hash_file(file_path)
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    file_hashes[file_hash].append(file_path)
                except Exception:
                    continue
        
        # Return only duplicates
        return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}

    def bulk_rename(self, directory: Path, pattern: str, replacement: str) -> int:
        """Bulk rename files matching a pattern."""
        renamed_count = 0
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and pattern in file_path.name:
                new_name = file_path.name.replace(pattern, replacement)
                new_path = file_path.parent / new_name
                try:
                    file_path.rename(new_path)
                    renamed_count += 1
                except Exception:
                    continue
        
        return renamed_count

    def get_directory_size(self, directory: Path) -> int:
        """Get total size of a directory in bytes."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    continue
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


# Create plugin instance
plugin = FilesPlugin()
