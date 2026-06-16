from typing import Dict, Any, Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Checkbox, Select
from textual.containers import Grid, Horizontal, Vertical

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


class DNSFormDialog(ModalScreen[Optional[Dict[str, Any]]]):
    def __init__(self, record: Optional[Dict[str, Any]] = None) -> None:
        self.record = record
        super().__init__()

    def compose(self) -> ComposeResult:
        title = "Edit DNS Record" if self.record else "Add DNS Record"
        
        record_type = self.record.get("type", "A") if self.record else "A"
        name = self.record.get("name", "") if self.record else ""
        content = self.record.get("content", "") if self.record else ""
        ttl = str(self.record.get("ttl", 3600)) if self.record else "3600"
        proxied = self.record.get("proxied", False) if self.record else False

        types = [("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"), ("TXT", "TXT"), ("MX", "MX"), ("NS", "NS")]

        with Grid(classes="dialog-container"):
            with Vertical(classes="dialog-box"):
                yield Label(title, classes="dialog-title")
                
                yield Label("Record Type")
                yield Select(types, value=record_type, id="dns-type")
                
                yield Label("Name (e.g. sub.domain.com)")
                yield Input(value=name, placeholder="Name", id="dns-name")
                
                yield Label("Content (e.g. IP Address)")
                yield Input(value=content, placeholder="Content", id="dns-content")
                
                yield Label("TTL (seconds)")
                yield Input(value=ttl, placeholder="3600", id="dns-ttl")
                
                yield Checkbox("Proxied", value=proxied, id="dns-proxied")
                
                with Horizontal():
                    yield Button("Save", variant="primary", id="dns-save")
                    yield Button("Cancel", id="dns-cancel")

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
