from typing import Any, Dict, Optional

from textual.app import ComposeResult
from textual.containers import Center, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static


class TokenSetupDialog(ModalScreen[Optional[str]]):
    """First-run dialog shown when no API token is configured."""

    DEFAULT_CSS = """
    TokenSetupDialog {
        align: center middle;
    }
    #setup-box {
        background: $surface;
        border: tall $primary;
        padding: 2 4;
        width: 60;
        height: auto;
    }
    #setup-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    #setup-hint {
        color: $text-muted;
        margin-bottom: 1;
    }
    #setup-token {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="setup-box"):
                yield Label("Welcome to CFManager", id="setup-title")
                yield Label(
                    "Enter your Cloudflare API token to get started.\n"
                    "Create one at: dash.cloudflare.com/profile/api-tokens",
                    id="setup-hint",
                )
                yield Input(placeholder="cf_xxxxxxxxxx", password=True, id="setup-token")
                with Horizontal():
                    yield Button("Connect", variant="primary", id="setup-save")
                    yield Button("Skip", id="setup-skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "setup-save":
            token = self.query_one("#setup-token", Input).value.strip()
            if token:
                self.dismiss(token)
            else:
                self.query_one("#setup-token", Input).border_title = "Token required"
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            token = self.query_one("#setup-token", Input).value.strip()
            if token:
                self.dismiss(token)


class ConfirmDialog(ModalScreen[bool]):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        with Grid(classes="dialog-container"):
            with Vertical(classes="dialog-box"):
                yield Label("Confirm Action", classes="dialog-title")
                yield Label(self.message, id="dialog-message")
                with Horizontal():
                    yield Button("Yes", variant="primary", id="confirm-yes")
                    yield Button("No", id="confirm-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)


class DNSViewDialog(ModalScreen[None]):
    DEFAULT_CSS = """
    DNSViewDialog .dialog-box {
        max-height: 85%;
    }
    DNSViewDialog .view-field {
        color: $text-muted;
        margin-top: 1;
    }
    DNSViewDialog .view-value {
        background: $surface;
        border: solid $panel;
        padding: 0 1;
        height: 3;
        content-align: left middle;
        width: 100%;
        margin: 0 0 0 0;
        color: $text;
    }
    DNSViewDialog .dialog-buttons {
        margin-top: 1;
        width: 100%;
    }
    DNSViewDialog .dialog-buttons Button {
        width: 1fr;
        margin: 0;
    }
    """

    def __init__(self, record: Dict[str, Any]) -> None:
        self.record = record
        super().__init__()

    def compose(self) -> ComposeResult:
        r = self.record
        ttl_display = "Auto" if r.get("ttl") == 1 else str(r.get("ttl", "—"))

        with Grid(classes="dialog-container"):
            with VerticalScroll(classes="dialog-box"):
                yield Label("DNS Record Details", classes="dialog-title")

                yield Label("Record Type", classes="view-field")
                yield Static(r.get("type", "—"), classes="view-value")

                yield Label("Name", classes="view-field")
                yield Static(r.get("name", "—"), classes="view-value")

                yield Label("Content", classes="view-field")
                yield Static(r.get("content", "—"), classes="view-value")

                yield Label("TTL", classes="view-field")
                yield Static(ttl_display, classes="view-value")

                yield Label("Proxied", classes="view-field")
                yield Static("Yes" if r.get("proxied") else "No", classes="view-value")

                with Horizontal(classes="dialog-buttons"):
                    yield Button("Close", variant="primary", id="dns-view-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key in ("escape", "enter", "q"):
            self.dismiss(None)


class DNSFormDialog(ModalScreen[Optional[Dict[str, Any]]]):
    DEFAULT_CSS = """
    DNSFormDialog .dialog-box {
        max-height: 85%;
    }
    DNSFormDialog Select {
        margin: 1 0;
        height: 3;
    }
    DNSFormDialog #dns-name-label {
        margin-top: 1;
    }
    DNSFormDialog Checkbox {
        padding: 0;
        margin: 1 0;
    }
    DNSFormDialog .dialog-buttons {
        margin-top: 1;
        width: 100%;
    }
    DNSFormDialog .dialog-buttons Button {
        width: 1fr;
        margin: 0;
    }
    """

    def __init__(self, record: Optional[Dict[str, Any]] = None) -> None:
        self.record = record
        super().__init__()

    def compose(self) -> ComposeResult:
        title = "Edit DNS Record" if self.record else "Add DNS Record"

        record_type = self.record.get("type", "A") if self.record else "A"
        proxied = self.record.get("proxied", False) if self.record else False

        types = [("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"), ("TXT", "TXT"), ("MX", "MX"), ("NS", "NS")]

        with Grid(classes="dialog-container"):
            with VerticalScroll(classes="dialog-box"):
                yield Label(title, classes="dialog-title")

                yield Label("Record Type")
                yield Select(types, value=record_type, id="dns-type")

                yield Label("Name (e.g. sub.domain.com)", id="dns-name-label")
                yield Input(placeholder="Name", id="dns-name")

                yield Label("Content (e.g. IP Address)")
                yield Input(placeholder="Content", id="dns-content")

                yield Label("TTL (seconds)")
                yield Input(placeholder="3600", id="dns-ttl")

                yield Checkbox("Proxied", value=proxied, id="dns-proxied")

                with Horizontal(classes="dialog-buttons"):
                    yield Button("Save", variant="primary", id="dns-save")
                    yield Button("Cancel", id="dns-cancel")

    def on_mount(self) -> None:
        if self.record:
            self.query_one("#dns-name", Input).value = self.record.get("name", "")
            self.query_one("#dns-content", Input).value = self.record.get("content", "")
            self.query_one("#dns-ttl", Input).value = str(self.record.get("ttl", 3600))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dns-save":
            dns_type = self.query_one("#dns-type").value
            dns_name = self.query_one("#dns-name").value
            dns_content = self.query_one("#dns-content").value
            dns_ttl_str = self.query_one("#dns-ttl").value
            dns_proxied = self.query_one("#dns-proxied").value

            try:
                dns_ttl = int(dns_ttl_str)
            except ValueError:
                dns_ttl = 3600

            self.dismiss({
                "type": dns_type,
                "name": dns_name,
                "content": dns_content,
                "ttl": dns_ttl,
                "proxied": dns_proxied
            })
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
