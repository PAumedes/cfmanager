import os
from pathlib import Path
from dotenv import load_dotenv
from cfmanager.core.exceptions import ConfigError

class Config:
    def __init__(self, load_env_file: bool = True):
        if load_env_file:
            # Load from current working directory
            load_dotenv()
            # Also load from home directory if exists
            home_dotenv = Path.home() / ".env"
            if home_dotenv.exists():
                load_dotenv(dotenv_path=home_dotenv)

        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.log_level = os.getenv("CFM_LOG_LEVEL", "INFO").upper()
        self.r2_access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
        self.r2_secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
        
        # Default log file to ~/.cfmanager/cfmanager.log
        default_log_dir = Path.home() / ".cfmanager"
        default_log_file = default_log_dir / "cfmanager.log"
        
        self.log_file = os.getenv("CFM_LOG_FILE")
        if self.log_file:
            self.log_file = Path(self.log_file)
        else:
            self.log_file = default_log_file

    def validate(self):
        if not self.api_token:
            raise ConfigError(
                "CLOUDFLARE_API_TOKEN environment variable or .env file entry is missing.\n"
                "Please configure CLOUDFLARE_API_TOKEN in your environment or a .env file."
            )
