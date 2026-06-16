from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, ContentSwitcher

from cfmanager.core.config import Config
from cfmanager.core.client import CloudflareClient
from cfmanager.tui.widgets.sidebar import Sidebar
from cfmanager.tui.widgets.status_bar import StatusBar
from cfmanager.tui.widgets.dialogs import TokenSetupDialog

from cfmanager.tui.screens.dashboard import DashboardView
from cfmanager.tui.screens.zones import ZonesView
from cfmanager.tui.screens.dns import DNSView
from cfmanager.tui.screens.ssl import SSLView
from cfmanager.tui.screens.r2 import R2View
from cfmanager.tui.screens.pages import PagesView
from cfmanager.tui.screens.loadbalancers import LoadBalancerView
from cfmanager.tui.commands import CFManagerCommandProvider


class CFManagerApp(App):
    CSS_PATH = "theme.tcss"
    COMMANDS = {CFManagerCommandProvider}
    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+p", "command_palette", "Command Palette"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, config: Config, client: CloudflareClient | None, **kwargs):
        self.cf_config = config
        self.cf_client = client
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            with ContentSwitcher(initial="dashboard", id="content-switcher"):
                yield DashboardView(id="dashboard")
                yield ZonesView(id="zones")
                yield DNSView(id="dns")
                yield SSLView(id="ssl")
                yield R2View(id="r2")
                yield PagesView(id="pages")
                yield LoadBalancerView(id="lb")
        yield StatusBar(id="status-bar")

    async def on_mount(self) -> None:
        if self.cf_client is None:
            # No token configured — show first-run setup dialog
            async def handle_token(token: str | None) -> None:
                if token:
                    Config.save_token(token)
                    self.cf_client = CloudflareClient(api_token=token)
                    self.run_worker(self.load_account_details())
                else:
                    status_bar = self.query_one(StatusBar)
                    status_bar.update_status(account_name="—", status="No token — run: cfm config set-token YOUR_TOKEN")
            self.push_screen(TokenSetupDialog(), handle_token)
        else:
            self.run_worker(self.load_account_details())

    async def load_account_details(self) -> None:
        status_bar = self.query_one(StatusBar)
        try:
            account_id = await self.cf_client.get_async_account_id()
            account_name = self.cf_client._account_name
            status_bar.update_status(account_name=account_name, status="Connected")
        except Exception as e:
            status_bar.update_status(account_name="Unknown", status=f"Error: {e}")

    def on_sidebar_selected(self, message: Sidebar.Selected) -> None:
        switcher = self.query_one("#content-switcher")
        switcher.current = message.screen_name

        if message.screen_name == "zones":
            self.run_worker(self.query_one("#zones").refresh_zones())
        elif message.screen_name == "dns":
            self.run_worker(self.query_one("#dns").refresh_records())
        elif message.screen_name == "ssl":
            self.run_worker(self.query_one("#ssl").refresh_data())
        elif message.screen_name == "r2":
            self.run_worker(self.query_one("#r2").refresh_data())
        elif message.screen_name == "pages":
            self.run_worker(self.query_one("#pages").refresh_data())
        elif message.screen_name == "lb":
            self.run_worker(self.query_one("#lb").refresh_data())

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display


def run_tui_app():
    from cfmanager.core.logger import setup_logger
    config = Config()
    setup_logger(config.log_level, config.log_file)

    # Pass client=None if no token — app handles it with setup dialog
    client = CloudflareClient(api_token=config.api_token) if config.api_token else None
    CFManagerApp(config, client).run()
