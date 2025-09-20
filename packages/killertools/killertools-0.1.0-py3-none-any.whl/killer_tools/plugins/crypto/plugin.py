"""Crypto plugin implementation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid
from typing import Any, Optional

import jwt
from rich.console import Console
from PyQt6.QtWidgets import QWidget
from textual.app import App

from killer_tools.core.plugin import Plugin


class CryptoPlugin(Plugin):
    """Plugin for cryptographic operations and utilities."""

    name = "crypto"
    summary = "Hash functions, HMAC, JWT operations, UUID generation, and encoding"
    version = "1.0.0"

    def run_cli(self, console: Console, **kwargs: Any) -> None:
        """Run the crypto plugin in CLI mode."""
        console.print("[bold blue]Crypto Plugin[/bold blue]")
        console.print("Available operations:")
        console.print("• hash <text> <algorithm> - Hash text with specified algorithm")
        console.print("• hmac <text> <key> <algorithm> - Generate HMAC")
        console.print("• jwt-decode <token> - Decode JWT token (no verification)")
        console.print("• uuid - Generate UUID")
        console.print("• ulid - Generate ULID")
        console.print("• base64-encode <text> - Base64 encode text")
        console.print("• base64-decode <text> - Base64 decode text")

    def tui_view(self) -> Optional[App]:
        """Return a Textual app for TUI mode."""
        return None

    def gui_widget(self) -> Optional[QWidget]:
        """Return a PyQt6 widget for GUI mode."""
        return None

    def hash_text(self, text: str, algorithm: str = "sha256") -> str:
        """Hash text with specified algorithm."""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()

    def generate_hmac(self, text: str, key: str, algorithm: str = "sha256") -> str:
        """Generate HMAC for text with key."""
        return hmac.new(
            key.encode("utf-8"),
            text.encode("utf-8"),
            algorithm
        ).hexdigest()

    def decode_jwt(self, token: str) -> dict:
        """Decode JWT token without verification."""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            return {"error": str(e)}

    def generate_uuid(self) -> str:
        """Generate a UUID4."""
        return str(uuid.uuid4())

    def generate_ulid(self) -> str:
        """Generate a ULID."""
        try:
            import ulid
            return str(ulid.new())
        except ImportError:
            return "ULID generation requires ulid-py package"

    def base64_encode(self, text: str) -> str:
        """Base64 encode text."""
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    def base64_decode(self, text: str) -> str:
        """Base64 decode text."""
        try:
            return base64.b64decode(text.encode("utf-8")).decode("utf-8")
        except Exception as e:
            return f"Error: {e}"

    def generate_random_string(self, length: int = 32) -> str:
        """Generate a random string."""
        return secrets.token_urlsafe(length)


# Create plugin instance
plugin = CryptoPlugin()
