from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class StatusBar(Widget):
    def __init__(self, account_name: str = "Loading...", status: str = "Connecting", **kwargs) -> None:
        self.account_name = account_name
        self.status = status
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        self.status_label = Label(f"Status: {self.status} | Account: {self.account_name}")
        yield self.status_label

    def update_status(self, account_name: str, status: str) -> None:
        self.account_name = account_name
        self.status = status
        self.status_label.update(f"Status: {self.status} | Account: {self.account_name}")
