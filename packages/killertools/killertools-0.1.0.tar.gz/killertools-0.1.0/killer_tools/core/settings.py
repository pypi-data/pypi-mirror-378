"""Settings management for KillerTools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ThemeSettings(BaseModel):
    """Theme-related settings."""

    mode: str = Field(default="system", description="Theme mode: system, light, dark")
    accent_color: str = Field(default="#7C3AED", description="Accent color in hex")
    font_family: str = Field(default="system", description="Font family")


class UIConfig(BaseModel):
    """UI configuration settings."""

    window_width: int = Field(default=1200, description="Default window width")
    window_height: int = Field(default=800, description="Default window height")
    sidebar_width: int = Field(default=250, description="Sidebar width")
    show_tooltips: bool = Field(default=True, description="Show tooltips")
    animations: bool = Field(default=True, description="Enable animations")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    file_logging: bool = Field(default=True, description="Enable file logging")
    max_file_size: int = Field(default=10, description="Max log file size in MB")
    backup_count: int = Field(default=5, description="Number of backup log files")


class TelemetryConfig(BaseModel):
    """Telemetry configuration."""

    enabled: bool = Field(default=False, description="Enable telemetry")
    anonymous_usage: bool = Field(default=True, description="Collect anonymous usage data")
    crash_reports: bool = Field(default=True, description="Send crash reports")


class Settings(BaseSettings):
    """Main settings class for KillerTools."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KILLERTOOLS_",
        case_sensitive=False,
    )

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    imgbb_api_key: Optional[str] = Field(default=None, description="ImgBB API key")
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token")

    # External tools
    ffmpeg_path: Optional[str] = Field(default=None, description="Path to FFmpeg binary")

    # UI Settings
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)

    # Plugin settings
    plugin_settings: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific settings")

    def save_to_file(self, file_path: Optional[Path] = None) -> None:
        """Save settings to a JSON file."""
        if file_path is None:
            config_dir = Path.home() / ".killertools"
            config_dir.mkdir(exist_ok=True)
            file_path = config_dir / "config.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, file_path: Optional[Path] = None) -> Settings:
        """Load settings from a JSON file."""
        if file_path is None:
            config_dir = Path.home() / ".killertools"
            file_path = config_dir / "config.json"

        if not file_path.exists():
            return cls()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return cls()

    def get_plugin_setting(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Get a plugin-specific setting."""
        return self.plugin_settings.get(plugin_name, {}).get(key, default)

    def set_plugin_setting(self, plugin_name: str, key: str, value: Any) -> None:
        """Set a plugin-specific setting."""
        if plugin_name not in self.plugin_settings:
            self.plugin_settings[plugin_name] = {}
        self.plugin_settings[plugin_name][key] = value
