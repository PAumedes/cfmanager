"""Tests for multi-account profile support."""
import json
import pytest
from pathlib import Path
from cfmanager.core.config import Config
from cfmanager.core.profiles import ProfileManager, ProfileError


# ── ProfileManager ─────────────────────────────────────────────────────────────

def test_add_and_list_profile(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    pm.add("prod", api_token="tok_prod", account_id="acc1")

    profiles = pm.list_profiles()
    assert "prod" in profiles
    assert profiles["prod"]["api_token"] == "tok_prod"
    assert profiles["prod"]["account_id"] == "acc1"


def test_add_profile_without_account_id(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    pm.add("dev", api_token="tok_dev")

    profiles = pm.list_profiles()
    assert profiles["dev"].get("account_id") is None


def test_delete_profile(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    pm.add("prod", api_token="tok_prod")
    pm.delete("prod")

    assert "prod" not in pm.list_profiles()


def test_delete_nonexistent_profile_raises(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    with pytest.raises(ProfileError, match="not found"):
        pm.delete("ghost")


def test_get_profile_returns_correct_data(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    pm.add("staging", api_token="tok_staging", account_id="acc2")

    p = pm.get("staging")
    assert p["api_token"] == "tok_staging"
    assert p["account_id"] == "acc2"


def test_get_nonexistent_profile_raises(tmp_path):
    pm = ProfileManager(profiles_file=tmp_path / "profiles.json")
    with pytest.raises(ProfileError, match="not found"):
        pm.get("nobody")


def test_profiles_persisted_to_disk(tmp_path):
    pf = tmp_path / "profiles.json"
    pm = ProfileManager(profiles_file=pf)
    pm.add("prod", api_token="tok_prod")

    pm2 = ProfileManager(profiles_file=pf)
    assert "prod" in pm2.list_profiles()


# ── Config profile loading ─────────────────────────────────────────────────────

def test_config_loads_profile_token(tmp_path, monkeypatch):
    pf = tmp_path / "profiles.json"
    pf.write_text(json.dumps({"myprofile": {"api_token": "tok_from_profile", "account_id": "acc_profile"}}))
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    cfg = Config(load_env_file=False, profile="myprofile", profiles_file=pf)
    assert cfg.api_token == "tok_from_profile"
    assert cfg.account_id == "acc_profile"


def test_config_profile_overrides_env_token(tmp_path, monkeypatch):
    pf = tmp_path / "profiles.json"
    pf.write_text(json.dumps({"myprofile": {"api_token": "profile_token"}}))
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "env_token")

    cfg = Config(load_env_file=False, profile="myprofile", profiles_file=pf)
    assert cfg.api_token == "profile_token"


def test_config_no_profile_uses_env(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "env_only")
    cfg = Config(load_env_file=False)
    assert cfg.api_token == "env_only"
