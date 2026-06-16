from __future__ import annotations

from textual.command import Hit, Hits, Provider


class CFManagerCommandProvider(Provider):
    """Command palette provider for cfmanager navigation and actions."""

    _COMMANDS: list[tuple[str, str]] = [
        ("Go to Dashboard", "dashboard"),
        ("Go to Zones", "zones"),
        ("Go to SSL/TLS", "ssl"),
        ("Go to R2 Storage", "r2"),
        ("Go to Pages", "pages"),
        ("Go to Load Balancers", "lb"),
    ]

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        app = self.app

        # Navigation commands
        for label, screen_name in self._COMMANDS:
            score = matcher.match(label)
            if score > 0:
                def _navigate(name: str = screen_name) -> None:
                    app.navigate_to(name)

                yield Hit(
                    score=score,
                    match_display=matcher.highlight(label),
                    command=_navigate,
                    help=f"Switch to the {label.replace('Go to ', '')} view",
                )

        # Quit command
        quit_label = "Quit"
        score = matcher.match(quit_label)
        if score > 0:
            yield Hit(
                score=score,
                match_display=matcher.highlight(quit_label),
                command=app.exit,
                help="Exit cfmanager",
            )
