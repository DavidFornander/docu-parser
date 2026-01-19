import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Central Configuration for Zero-Loss Engine.
    Values can be overridden by environment variables with prefix ZERO_.
    Example: ZERO_DATA_DIR=/tmp/data overrides data_dir.
    """
    
    # Base Data Directory
    # Default: ./data (relative to project root if running from root)
    # We resolve this to absolute path to avoid confusion
    data_dir: Path = Path("data").resolve()
    
    # Model Configuration
    model_name: str = "casperhansen/llama-3-8b-instruct-awq"
    
    # Internal settings (can also be overridden if needed)
    app_name: str = "Zero-Loss Engine"
    debug: bool = False

    class Config:
        env_prefix = "ZERO_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    # --- Derived Paths (Properties) ---
    # These automatically follow data_dir unless overridden manually in logic
    # but usually we want strict structure inside data_dir.

    @property
    def input_dir(self) -> Path:
        path = self.data_dir / "input"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def output_dir(self) -> Path:
        path = self.data_dir / "output"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        # Check if environment variable ZERO_LOG_DIR is set, otherwise default to data/logs
        env_log_dir = os.environ.get("ZERO_LOG_DIR")
        if env_log_dir:
            path = Path(env_log_dir).resolve()
        else:
            path = self.data_dir / "logs"
            
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "zeroloss.db"

    @property
    def assets_dir(self) -> Path:
        path = self.data_dir / "assets"
        path.mkdir(parents=True, exist_ok=True)
        return path

# Singleton Instance
settings = Settings()
