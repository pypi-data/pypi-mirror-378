"""Logging configuration for KillerTools."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: Optional[Console] = None,
    enable_file_logging: bool = True,
    max_file_size: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """Set up logging for KillerTools."""
    
    # Create logger
    logger = logging.getLogger("killertools")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with Rich
    if console is None:
        console = Console()
    
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter for console
    console_formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="[%X]",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if enable_file_logging:
        if log_file is None:
            log_dir = Path.home() / ".killertools" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "killertools.log"
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter for file
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger
