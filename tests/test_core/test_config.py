import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cfmanager.core.config import Config


def test_cwd_dotenv_loaded_before_user_dotenv(monkeypatch):
    """cwd .env must be loaded first so project-level values win over user-level."""
    calls = []

    def fake_load_dotenv(dotenv_path=None, **kwargs):
        calls.append(dotenv_path)

    monkeypatch.setattr("cfmanager.core.config.load_dotenv", fake_load_dotenv)

    # Make the user-level dotenv path appear to exist so the second call fires.
    original_exists = Path.exists

    def fake_exists(self):
        if ".cfmanager" in str(self) and str(self).endswith(".env"):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)

    Config(load_env_file=True)

    assert len(calls) == 2
    assert calls[0] is None, "cwd .env (dotenv_path=None) must be loaded first"
    assert calls[1] is not None, "user-level .env must be loaded second"


def test_cwd_token_wins_over_user_token(monkeypatch):
    """When cwd .env sets a key, the user-level .env cannot clobber it."""
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    def fake_load_dotenv(dotenv_path=None, **kwargs):
        if dotenv_path is None:
            # cwd .env — set cwd value; setdefault ensures real env always wins.
            os.environ.setdefault("CLOUDFLARE_API_TOKEN", "cwd_token")
        else:
            # user-level .env — must not win over cwd value.
            os.environ.setdefault("CLOUDFLARE_API_TOKEN", "user_token")

    monkeypatch.setattr("cfmanager.core.config.load_dotenv", fake_load_dotenv)

    original_exists = Path.exists

    def fake_exists(self):
        if ".cfmanager" in str(self) and str(self).endswith(".env"):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)

    config = Config(load_env_file=True)

    assert config.api_token == "cwd_token"


def test_user_token_used_when_no_cwd_env(monkeypatch):
    """User-level .env is the fallback when cwd .env is absent."""
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    def fake_load_dotenv(dotenv_path=None, **kwargs):
        if dotenv_path is not None:
            os.environ.setdefault("CLOUDFLARE_API_TOKEN", "user_token")
        # cwd call sets nothing (simulates missing cwd .env)

    monkeypatch.setattr("cfmanager.core.config.load_dotenv", fake_load_dotenv)

    original_exists = Path.exists

    def fake_exists(self):
        if ".cfmanager" in str(self) and str(self).endswith(".env"):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)

    config = Config(load_env_file=True)

    assert config.api_token == "user_token"


def test_real_env_var_wins_over_dotenv(monkeypatch):
    """Actual environment variable always beats any .env file value."""
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "env_token")

    def fake_load_dotenv(dotenv_path=None, **kwargs):
        # Attempt to set from file — must not override the real env var.
        os.environ.setdefault("CLOUDFLARE_API_TOKEN", "file_token")

    monkeypatch.setattr("cfmanager.core.config.load_dotenv", fake_load_dotenv)

    config = Config(load_env_file=True)

    assert config.api_token == "env_token"


def test_config_account_id_from_env(monkeypatch):
    """CLOUDFLARE_ACCOUNT_ID env var is picked up by Config."""
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc_123")
    config = Config(load_env_file=False)
    assert config.account_id == "acc_123"


def test_config_account_id_absent(monkeypatch):
    """account_id is None when CLOUDFLARE_ACCOUNT_ID is not set."""
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    config = Config(load_env_file=False)
    assert config.account_id is None
