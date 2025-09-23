"""Output formatting utilities."""

import json
from typing import Any, Optional

from rich.console import Console
from rich.table import Table


class OutputFormatter:
    """Handles output formatting for CLI."""

    def __init__(self) -> None:
        """Initialize output formatter."""
        self.console = Console()
        self.json_mode = False

    def set_json_mode(self, enabled: bool) -> None:
        """Set JSON output mode.

        Args:
            enabled: Whether to output in JSON format
        """
        self.json_mode = enabled

    def info(self, message: str) -> None:
        """Display info message.

        Args:
            message: Message to display
        """
        if not self.json_mode:
            self.console.print(message)

    def success(self, message: str) -> None:
        """Display success message.

        Args:
            message: Success message
        """
        if not self.json_mode:
            self.console.print(f"[green]✅[/green] {message}")

    def warning(self, message: str) -> None:
        """Display warning message.

        Args:
            message: Warning message
        """
        if not self.json_mode:
            self.console.print(f"[yellow]⚠️[/yellow]  {message}")

    def error(self, message: str) -> None:
        """Display error message.

        Args:
            message: Error message
        """
        if not self.json_mode:
            # Rich Console doesn't support file parameter in all versions
            # Use stderr console instead
            error_console = Console(stderr=True)
            error_console.print(f"[red]❌[/red] {message}")

    def progress(self, message: str) -> None:
        """Display progress message.

        Args:
            message: Progress message
        """
        if not self.json_mode:
            self.console.print(f"[cyan]⏳[/cyan] {message}")

    def text(self, message: str) -> None:
        """Display plain text.

        Args:
            message: Text to display
        """
        if not self.json_mode:
            self.console.print(message)

    def json_output(self, data: Any) -> None:
        """Output data as JSON.

        Args:
            data: Data to output
        """
        if self.json_mode:
            print(json.dumps(data, indent=2, default=str))

    def table(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
        title: Optional[str] = None,
    ) -> None:
        """Display data in a table.

        Args:
            data: List of dictionaries
            columns: Column names to display
            title: Optional table title
        """
        if self.json_mode:
            self.json_output(data)
            return

        if not data:
            self.info("No data to display")
            return

        table = Table(title=title)

        # Add columns
        for column in columns:
            table.add_column(column)

        # Add rows
        for item in data:
            row = []
            for column in columns:
                value = item.get(column, "")
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                elif value is None:
                    value = "-"
                else:
                    value = str(value)
                row.append(value)
            table.add_row(*row)

        self.console.print(table)

    def dict_display(self, data: dict[str, Any], title: Optional[str] = None) -> None:
        """Display dictionary data.

        Args:
            data: Dictionary to display
            title: Optional title
        """
        if self.json_mode:
            self.json_output(data)
            return

        if title:
            self.console.print(f"\n[bold]{title}[/bold]")

        for key, value in data.items():
            if isinstance(value, dict):
                self.console.print(f"\n[cyan]{key}:[/cyan]")
                for sub_key, sub_value in value.items():
                    self.console.print(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                self.console.print(f"[cyan]{key}:[/cyan]")
                for item in value:
                    self.console.print(f"  • {item}")
            else:
                self.console.print(f"[cyan]{key}:[/cyan] {value}")
