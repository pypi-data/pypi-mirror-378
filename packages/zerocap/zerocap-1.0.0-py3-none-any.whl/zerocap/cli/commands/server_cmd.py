# src/zerocap/cli/commands/server_cmd.py
"""
CLI commands for managing and inspecting MCP Servers.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from zerocap.daemon import hub_client

# Create a 'sub-app' for the 'server' command
app = typer.Typer(help="Manage and inspect MCP Servers.")

@app.command("list")
def list_servers():
    """
    List all MCP Servers currently registered with the Zerocap Hub.
    """
    console = Console()
    
    try:
        hub_data = hub_client.get_hub_status()
        servers = hub_data.get("mcp_servers", {})

        if not servers:
            console.print("[yellow]No MCP Servers are currently registered with the hub.[/yellow]")
            return

        table = Table(
            "Server Name",
            "Address",
            "Model ID",
            "Tools",
            title="Registered MCP Servers"
        )

        for name, info in servers.items():
            address = info.get('address', '[i]N/A[/i]')
            manifest = info.get('manifest', {})
            model_id = manifest.get('model_id', '[i]N/A[/i]')
            tools = manifest.get('tools', [])
            
            # Format the list of tools for display
            tool_names = ", ".join([t.get('name', 'N/A') for t in tools])

            table.add_row(
                f"[bold cyan]{name}[/bold cyan]",
                f"[green]{address}[/green]",
                model_id,
                tool_names if tool_names else "[italic]None[/italic]"
            )
        
        console.print(table)

    except ConnectionError as e:
        console.print(f"[bold red]Error:[/bold red] Could not connect to the Zerocap daemon. Is it running?")
        console.print(f"       ({e})")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

@app.command("info")
def server_info(
    server_name: str = typer.Argument(..., help="The unique name of the server to inspect.")
):
    """
    Display detailed information about a specific MCP Server.
    """
    console = Console()
    console.print(f"🔎 Fetching details for server '[bold cyan]{server_name}[/bold cyan]'...")

    try:
        info = hub_client.discover_mcp_server(server_name)
        manifest = info.get("manifest", {})
        
        # --- Build a rich display for the server's details ---
        
        # Live Info
        address = info.get('address', 'N/A')
        
        # Manifest Info
        name = manifest.get('name', 'N/A')
        model_id = manifest.get('model_id', 'N/A')
        tools = manifest.get('tools', [])

        # Create a table for the main details
        details_table = Table.grid(padding=(0, 2))
        details_table.add_column(style="bold magenta")
        details_table.add_column()
        details_table.add_row("Name:", name)
        details_table.add_row("Address:", f"[green]{address}[/green]")
        details_table.add_row("Model ID:", model_id)
        
        # Create a table for the tools
        tools_table = Table("Tool Name", "Description", show_header=True, header_style="bold blue")
        if tools:
            for tool in tools:
                tools_table.add_row(
                    tool.get('name', 'N/A'),
                    tool.get('description', '[italic]No description.[/italic]')
                )
        else:
            tools_table.add_row("[italic]No tools listed.[/italic]", "")

        # Combine them in a Panel
        console.print(Panel(
            details_table,
            title=f"Server Details: [bold cyan]{server_name}[/bold cyan]",
            border_style="blue",
            expand=False
        ))
        console.print(tools_table)

    except ConnectionError as e:
        console.print(f"\n[bold red]Error:[/bold red] Could not find or connect to server '{server_name}'.")
        console.print(f"       ({e})")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")
