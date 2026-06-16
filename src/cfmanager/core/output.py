import csv
import io
import json
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table

class OutputFormatter:
    def __init__(self, format_type: str = "table"):
        self.format_type = format_type.lower()
        self.console = Console()

    def format(self, data: List[Dict[str, Any]], headers: List[str], keys: List[str]):
        """Format and print the data according to the format_type.
        
        Args:
            data: List of dictionaries containing the records.
            headers: List of user-friendly headers for display.
            keys: List of dictionary keys corresponding to the headers.
        """
        if self.format_type == "json":
            # Just print the json dump
            self.console.print_json(data=data)
        elif self.format_type == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            for row in data:
                # Format boolean values nicely for CSV as well, or keep raw
                formatted_row = {}
                for k in keys:
                    v = row.get(k)
                    if isinstance(v, bool):
                        formatted_row[k] = "true" if v else "false"
                    elif v is None:
                        formatted_row[k] = ""
                    else:
                        formatted_row[k] = str(v)
                writer.writerow(formatted_row)
            self.console.print(output.getvalue().strip())
        else:
            # Default is rich table
            table = Table(show_header=True, header_style="bold #F6821F")
            for header in headers:
                table.add_column(header)
            
            for row in data:
                row_values = []
                for key in keys:
                    val = row.get(key)
                    if isinstance(val, bool):
                        val = "[green]Yes[/green]" if val else "[red]No[/red]"
                    elif val is None:
                        val = ""
                    else:
                        val = str(val)
                    row_values.append(val)
                table.add_row(*row_values)
            
            self.console.print(table)
