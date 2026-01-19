import logging
import os
import sys
import threading
import time
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Define a custom theme for our application
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "timestamp": "dim white"
})

# Force terminal output and write to stderr
console = Console(theme=custom_theme, force_terminal=True, stderr=True)

def setup_logger(name: str = "StudyEngine", level: int = logging.INFO, log_file: str = None):
    """
    Configures a 'best practice' logger for 2026.
    Uses RichHandler for console and FileHandler for persistent logs.
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
            
    # 1. Console Handler (Rich)
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_time=True,
        show_path=False,
        enable_link_path=False,
        markup=True
    )
    logger.addHandler(rich_handler)
    
    # 2. File Handler (Plain Text - No Rich formatting)
    if log_file:
        # Ensure directory exists (though config usually handles this)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        # Clean, predictable format for Web UI readability
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(name)-12s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Silence overly verbose libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger

