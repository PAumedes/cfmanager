import os
from pathlib import Path

from dotenv import load_dotenv

from cfmanager.core.exceptions import ConfigError

class Config:
    def __init__(self, load_env_file: bool = True):
        if load_env_file:
            # Priority order (lowest → highest):
            # 1. ~/.cfmanager/.env  (user-level, written by `cfm config set-token`)
            # 2. .env in cwd        (project-level override)
            # 3. environment variable (always wins — load_dotenv never overrides real env vars)
            # Load cwd first so it is set, then user-level with override=False can't clobber it.
            load_dotenv()  # cwd .env
            cfmanager_dotenv = Path.home() / ".cfmanager" / ".env"
            if cfmanager_dotenv.exists():
                load_dotenv(dotenv_path=cfmanager_dotenv)  # fills missing keys only

        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
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

        self.dev_mode = os.getenv("CFM_ENV", "").lower() in ("dev", "development")

    @staticmethod
    def config_dir() -> Path:
        return Path.home() / ".cfmanager"

    @staticmethod
    def config_file() -> Path:
        return Config.config_dir() / ".env"

    @staticmethod
    def save_token(token: str) -> Path:
        config_file = Config.config_file()
        config_dir = config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        config_dir.chmod(0o700)
        lines = []
        if config_file.exists():
            lines = [l for l in config_file.read_text().splitlines() if not l.startswith("CLOUDFLARE_API_TOKEN=")]
        lines.append(f"CLOUDFLARE_API_TOKEN={token}")
        config_file.write_text("\n".join(lines) + "\n")
        config_file.chmod(0o600)
        return config_file

    def validate(self):
        if not self.api_token:
            raise ConfigError(
                "No API token found. Run:\n"
                "  cfm config set-token YOUR_TOKEN\n"
                "Or set the CLOUDFLARE_API_TOKEN environment variable."
            )
