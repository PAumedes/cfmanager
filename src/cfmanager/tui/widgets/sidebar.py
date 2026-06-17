from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView


class Sidebar(Widget):
    SCREEN_MAP = {
        "item-dashboard": "dashboard",
        "item-zones": "zones",
        "item-ssl": "ssl",
        "item-r2": "r2",
        "item-pages": "pages",
        "item-lb": "lb",
    }

    class Selected(Message):
        def __init__(self, screen_name: str) -> None:
            self.screen_name = screen_name
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("☁️ CFManager", id="sidebar-title")
        yield ListView(
            ListItem(Label("📊 Dashboard"), id="item-dashboard"),
            ListItem(Label("🌐 Zones / Domains"), id="item-zones"),
            ListItem(Label("🔑 SSL/TLS"), id="item-ssl"),
            ListItem(Label("📦 R2 Storage"), id="item-r2"),
            ListItem(Label("📃 Pages Projects"), id="item-pages"),
            ListItem(Label("⚖️ Load Balancers"), id="item-lb"),
            id="sidebar-list"
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        screen_name = self.SCREEN_MAP.get(item_id)
        if screen_name:
            self.post_message(self.Selected(screen_name))
