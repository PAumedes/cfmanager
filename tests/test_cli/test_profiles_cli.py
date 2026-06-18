"""Tests for cfm config profiles commands and --profile global flag."""
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from cfmanager.cli.app import app

runner = CliRunner()

_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")


def _profiles_patch(tmp_path):
    return patch("cfmanager.core.profiles.ProfileManager._DEFAULT_FILE", tmp_path / "profiles.json")


# ── profiles list ─────────────────────────────────────────────────────────────

def test_profiles_list_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    with (
        _PATCH_VALIDATE,
        patch("cfmanager.cli.config.ProfileManager") as MockPM,
    ):
        MockPM.return_value.list_profiles.return_value = {}
        result = runner.invoke(app, ["config", "profiles", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_profiles_list_shows_profiles(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    with (
        _PATCH_VALIDATE,
        patch("cfmanager.cli.config.ProfileManager") as MockPM,
    ):
        MockPM.return_value.list_profiles.return_value = {
            "prod": {"api_token": "cf_prod_token_1234", "account_id": "acc1"},
        }
        result = runner.invoke(app, ["config", "profiles", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "prod" in result.output


# ── profiles add ─────────────────────────────────────────────────────────────

def test_profiles_add(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    with (
        _PATCH_VALIDATE,
        patch("cfmanager.cli.config.ProfileManager") as MockPM,
    ):
        result = runner.invoke(
            app,
            ["config", "profiles", "add", "staging", "tok_staging"],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
    assert "staging" in result.output
    MockPM.return_value.add.assert_called_once_with(
        "staging", api_token="tok_staging", account_id=None
    )


def test_profiles_add_with_account_id(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    with (
        _PATCH_VALIDATE,
        patch("cfmanager.cli.config.ProfileManager") as MockPM,
    ):
        result = runner.invoke(
            app,
            ["config", "profiles", "add", "prod", "tok_prod", "--account-id", "acc123"],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
    MockPM.return_value.add.assert_called_once_with(
        "prod", api_token="tok_prod", account_id="acc123"
    )


# ── profiles delete ───────────────────────────────────────────────────────────

def test_profiles_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    with (
        _PATCH_VALIDATE,
        patch("cfmanager.cli.config.ProfileManager") as MockPM,
    ):
        result = runner.invoke(
            app, ["config", "profiles", "delete", "staging"], catch_exceptions=False
        )
    assert result.exit_code == 0
    MockPM.return_value.delete.assert_called_once_with("staging")


# ── --profile global flag ─────────────────────────────────────────────────────

def test_global_profile_flag_loads_profile_token(monkeypatch, tmp_path):
    pf = tmp_path / "profiles.json"
    pf.write_text(json.dumps({"myprofile": {"api_token": "profile_tok"}}))
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    mock_client = MagicMock()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.core.profiles.ProfileManager._DEFAULT_FILE", pf),
        patch("cfmanager.services.zones.ZoneService.list_zones", return_value=[]),
    ):
        result = runner.invoke(
            app,
            ["--profile", "myprofile", "zones", "list"],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
