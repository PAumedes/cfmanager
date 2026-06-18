import time

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import ContentSwitcher, Header

from cfmanager.core.client import CloudflareClient
from cfmanager.core.config import Config
from cfmanager.core.errors import format_error
from cfmanager.tui.widgets.dialogs import TokenSetupDialog
from cfmanager.tui.widgets.sidebar import Sidebar
from cfmanager.tui.widgets.status_bar import StatusBar

from cfmanager.tui.commands import CFManagerCommandProvider
from cfmanager.tui.screens.dashboard import DashboardView
from cfmanager.tui.screens.dns import DNSView
from cfmanager.tui.screens.loadbalancers import LoadBalancerView
from cfmanager.tui.screens.pages import PagesView
from cfmanager.tui.screens.r2 import R2View, R2ObjectsView
from cfmanager.tui.screens.ssl import SSLView
from cfmanager.tui.screens.zones import ZonesView


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
        self.query_one("#sidebar-list").focus()
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
            await self.cf_client.get_async_account_id()
            status_bar.update_status(account_name=self.cf_client.account_name, status="Connected")
        except Exception as e:
            status_bar.update_status(account_name="Unknown", status=f"Error: {format_error(e)}")

    _CACHE_TTL = 60.0
    _SCREEN_REFRESH: dict[str, str] = {
        "zones": "refresh_zones",
        "dns": "refresh_records",
        "ssl": "refresh_data",
        "r2": "refresh_data",
        "pages": "refresh_data",
        "lb": "refresh_data",
    }

    def navigate_to(self, screen_name: str) -> None:
        switcher = self.query_one("#content-switcher")
        switcher.current = screen_name

        refresh_method = self._SCREEN_REFRESH.get(screen_name)
        if refresh_method:
            v = self.query_one(f"#{screen_name}")
            if time.monotonic() - v._last_loaded > self._CACHE_TTL:
                v.run_worker(getattr(v, refresh_method)(), exclusive=True)

    def on_key(self, event) -> None:
        if len(self.screen_stack) > 1:
            return
        from textual.widgets import Input
        focused = self.focused
        sidebar_list = self.query_one("#sidebar-list")

        if event.key == "right" and focused is sidebar_list:
            highlighted = sidebar_list.highlighted_child
            if highlighted is not None:
                screen_name = Sidebar.SCREEN_MAP.get(highlighted.id)
                if screen_name:
                    self.navigate_to(screen_name)
                    self.call_after_refresh(self._focus_active_table)
        elif event.key == "left" and focused is not sidebar_list and not isinstance(focused, Input):
            if getattr(focused, "scroll_x", 0) > 0:
                return  # widget is scrolled right; let it scroll back left
            sidebar_list.focus()

    def _focus_active_table(self) -> None:
        from textual.widgets import DataTable
        current = self.query_one("#content-switcher").current
        try:
            self.query_one(f"#{current}").query_one(DataTable).focus()
        except Exception:
            pass

    def on_sidebar_selected(self, message: Sidebar.Selected) -> None:
        self.navigate_to(message.screen_name)

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display

    async def navigate_to_r2_objects(self, bucket_name: str) -> None:
        """Replace the r2 content pane with an object browser for *bucket_name*."""
        switcher = self.query_one("#content-switcher")
        # Remove previous object-browser widget if present
        try:
            old = switcher.query_one("#r2-objects")
            await old.remove()
        except Exception:
            pass
        browser = R2ObjectsView(bucket_name, id="r2-objects")
        await switcher.mount(browser)
        switcher.current = "r2-objects"


def run_tui_app():
    import sys
    from cfmanager.core.logger import setup_logger, get_logger

    config = Config()
    setup_logger(config.log_level, config.log_file, dev_mode=config.dev_mode, console=False)
    logger = get_logger()

    if config.dev_mode:
        print(f"[cfm dev] debug log → {config.log_file}", file=sys.stderr)

    # Route uncaught exceptions to the log file so TUI crashes aren't silent
    _original_excepthook = sys.excepthook

    def _crash_logger(exc_type, exc_value, exc_tb):
        logger.critical("Uncaught exception — app crashed", exc_info=(exc_type, exc_value, exc_tb))
        _original_excepthook(exc_type, exc_value, exc_tb)

    sys.excepthook = _crash_logger

    # Pass client=None if no token — app handles it with setup dialog
    client = CloudflareClient(api_token=config.api_token, account_id=config.account_id) if config.api_token else None
    CFManagerApp(config, client).run()
