from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widget import Widget
from textual.widgets import Label, Static


class DashboardView(Widget):
    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            yield Label("📊 Dashboard Overview", id="screen-title")
            with Vertical():
                yield Static(
                    "Welcome to CFManager!\n\n"
                    "This terminal interface provides keyboard-driven access to your Cloudflare infrastructure.\n\n"
                    "Available Navigation:\n"
                    " - 🌐 Zones / Domains: Manage your zones, status, cache purging\n"
                    " - 🔑 SSL/TLS: View/edit SSL configurations (Phase 2)\n"
                    " - 📦 R2 Storage: Browse buckets and objects (Phase 2)\n"
                    " - 📃 Pages: Manage pages deployments (Phase 2)\n"
                    " - ⚖️ Load Balancers: Manage load balancers & pools (Phase 3)\n\n"
                    "Global Shortcuts:\n"
                    " - Ctrl+B: Toggle sidebar\n"
                    " - q: Exit application",
                    classes="card"
                )
