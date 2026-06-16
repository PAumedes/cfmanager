from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import DataTable, Label

from cfmanager.core.logger import get_logger
from cfmanager.services.pages import PagesService
logger = get_logger()


class PagesView(Widget):
    def __init__(self, **kwargs) -> None:
        self.selected_project: Optional[str] = None
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            self.title_label = Label("📃 Pages Projects", id="screen-title")
            yield self.title_label
            self.hint_label = Label(
                "Press [bold]Enter[/bold] to view deployments, [bold]r[/bold] to refresh."
            )
            yield self.hint_label
            yield DataTable(id="pages-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        # Start in projects mode
        self._setup_projects_columns(table)
        self.run_worker(self.refresh_data())

    def _setup_projects_columns(self, table: DataTable) -> None:
        table.clear(columns=True)
        table.add_columns("Name", "Subdomain", "Latest Status", "Created On")

    def _setup_deployments_columns(self, table: DataTable) -> None:
        table.clear(columns=True)
        table.add_columns("ID", "Environment", "Status", "URL", "Created On")

    async def refresh_data(self) -> None:
        if self.selected_project is None:
            await self._load_projects()
        else:
            await self._load_deployments(self.selected_project)

    async def _load_projects(self) -> None:
        table = self.query_one(DataTable)
        self._setup_projects_columns(table)
        self.title_label.update("📃 Pages Projects")
        self.hint_label.update(
            "Press [bold]Enter[/bold] to view deployments, [bold]r[/bold] to refresh."
        )

        pages_service = PagesService(self.app.cf_client)
        try:
            projects = await pages_service.list_projects_async()
            for project in projects:
                table.add_row(
                    project.get("name", ""),
                    project.get("subdomain", ""),
                    project.get("latest_deployment_status", ""),
                    str(project.get("created_on", "")),
                    key=project.get("name", ""),
                )
        except Exception as e:
            logger.exception("Failed to load Pages projects in TUI")
            self.app.notify(f"Error loading Pages projects: {e}", severity="error")

    async def _load_deployments(self, project_name: str) -> None:
        table = self.query_one(DataTable)
        self._setup_deployments_columns(table)
        self.title_label.update(f"📃 Deployments — {project_name}")
        self.hint_label.update(
            "Press [bold]b[/bold] or [bold]Escape[/bold] to go back, [bold]r[/bold] to refresh."
        )

        pages_service = PagesService(self.app.cf_client)
        try:
            deployments = await pages_service.list_deployments_async(project_name)
            for dep in deployments:
                table.add_row(
                    dep.get("id", ""),
                    dep.get("environment", ""),
                    dep.get("status", ""),
                    dep.get("url", ""),
                    str(dep.get("created_on", "")),
                    key=dep.get("id", ""),
                )
        except Exception as e:
            logger.exception("Failed to load Pages deployments in TUI")
            self.app.notify(f"Error loading deployments: {e}", severity="error")

    def _go_back_to_projects(self) -> None:
        self.selected_project = None
        self.run_worker(self.refresh_data())

    async def on_key(self, event) -> None:
        if event.key == "r":
            await self.refresh_data()
            return

        if event.key in ("b", "escape") and self.selected_project is not None:
            self._go_back_to_projects()
            return

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self.selected_project is None:
            # Drill into project deployments
            project_name = event.row_key.value
            self.selected_project = project_name
            self.run_worker(self.refresh_data())
