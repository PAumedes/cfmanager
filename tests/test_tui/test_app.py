from unittest.mock import MagicMock, AsyncMock, patch
from cfmanager.tui.app import CFManagerApp
from cfmanager.core.client import CloudflareClient
from cfmanager.core.config import Config


def _make_mock_client():
    client = MagicMock(spec=CloudflareClient)
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    client.get_async_account_id = AsyncMock(return_value="mock_account_id")
    client._account_name = "Mock Account"
    return client


def _make_mock_config():
    config = MagicMock(spec=Config)
    config.api_token = "test_token"
    config.log_level = "WARNING"
    config.log_file = None
    return config


async def test_app_mounts():
    """App composes and mounts without raising."""
    client = _make_mock_client()
    config = _make_mock_config()
    app = CFManagerApp(config=config, client=client)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert pilot.app.query_one("#content-switcher") is not None
        assert pilot.app.query_one("#sidebar") is not None


async def test_initial_view_is_dashboard():
    """ContentSwitcher starts on the dashboard view."""
    client = _make_mock_client()
    config = _make_mock_config()
    app = CFManagerApp(config=config, client=client)
    async with app.run_test() as pilot:
        await pilot.pause()
        switcher = pilot.app.query_one("#content-switcher")
        assert switcher.current == "dashboard"


async def test_navigate_to_switches_view():
    """navigate_to sets the active content pane immediately."""
    client = _make_mock_client()
    config = _make_mock_config()
    app = CFManagerApp(config=config, client=client)
    async with app.run_test() as pilot:
        await pilot.pause()
        pilot.app.navigate_to("ssl")
        switcher = pilot.app.query_one("#content-switcher")
        assert switcher.current == "ssl"


async def test_navigate_to_all_views():
    """navigate_to works for every named view without raising."""
    client = _make_mock_client()
    config = _make_mock_config()
    app = CFManagerApp(config=config, client=client)
    views = ["dashboard", "zones", "dns", "ssl", "r2", "pages", "lb"]
    async with app.run_test() as pilot:
        await pilot.pause()
        for view in views:
            pilot.app.navigate_to(view)
            switcher = pilot.app.query_one("#content-switcher")
            assert switcher.current == view


async def test_no_client_does_not_crash():
    """App with no token pushes the setup dialog gracefully (no crash)."""
    config = _make_mock_config()
    config.api_token = None
    app = CFManagerApp(config=config, client=None)
    with patch("cfmanager.tui.app.CFManagerApp.push_screen"):
        async with app.run_test() as pilot:
            await pilot.pause()
            assert pilot.app.query_one("#content-switcher") is not None
