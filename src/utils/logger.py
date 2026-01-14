import logging
import os
import sys
import threading
import time
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

# Define a custom theme for our application
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "timestamp": "dim white",
    "heartbeat": "dim blue"
})

# Force terminal output (for when running in non-interactive shells)
# and write to stderr (standard for logs)
console = Console(theme=custom_theme, force_terminal=True, stderr=True)

def setup_logger(name: str = "StudyEngine", level: int = logging.INFO):
    """
    Configures a 'best practice' logger for 2026.
    Uses RichHandler for beautiful, structured console output.
    Captures third-party logs (like vLLM) and formats them consistently.
    """
    
    # Configure root logger if not already configured
    # We force re-configuration to ensure our handlers take precedence
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicates/conflicts
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    # Create the RichHandler
    # markup=True allows us to use [bold red]text[/] style syntax in logs
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_time=True,
        show_path=False, # cleaner output
        enable_link_path=True,
        markup=True
    )
    
    # Set the format (RichHandler ignores standard formatters for the message part usually, 
    # but we set a basic one for compatibility)
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)
    
    root_logger.addHandler(rich_handler)
    root_logger.setLevel(level)
    
    # Silence overly verbose libraries if necessary
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(name)

class Heartbeat:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Heartbeat, cls).__new__(cls)
                    cls._instance.status = "Initializing..."
                    cls._instance.running = False
                    cls._instance.thread = None
        return cls._instance

    def set_status(self, status: str):
        """Update the current operation status."""
        self.status = status

    def start(self):
        """Start the background heartbeat thread."""
        if self.running:
            return
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the heartbeat thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _loop(self):
        """Main loop that logs status every 5 seconds."""
        import json
        from datetime import datetime
        
        last_print = 0
        log_file = "logs/system_state.jsonl"
        
        while self.running:
            current_time = time.time()
            if current_time - last_print >= 5.0:
                # ts = datetime.now().strftime("%H:%M:%S")
                # console.print(f"[heartbeat]♥ [{ts}] {self.status}[/]", highlight=False)
                
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "status": self.status,
                }
                
                try:
                    with open(log_file, "a") as f:
                        f.write(json.dumps(log_entry) + "\n")
                except Exception as e:
                    console.print(f"[error]Failed to write heartbeat log: {e}[/]")
                
                last_print = current_time
            time.sleep(0.5)

# Global instance
heartbeat = Heartbeat()