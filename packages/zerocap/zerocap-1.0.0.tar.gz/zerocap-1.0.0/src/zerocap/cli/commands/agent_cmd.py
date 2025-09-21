# src/zerocap/cli/commands/agent_cmd.py
"""
CLI commands for managing and inspecting ACP Agents.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from zerocap.daemon import hub_client

# We create a 'sub-app' for the 'agent' command
app = typer.Typer(help="Manage and inspect ACP Agents.")

@app.command("list")
def list_agents():
    """
    List all ACP Agents currently registered with the Zerocap Hub.
    """
    console = Console()
    
    try:
        hub_data = hub_client.get_hub_status()
        agents = hub_data.get("acp_agents", {})

        if not agents:
            console.print("[yellow]No ACP Agents are currently registered with the hub.[/yellow]")
            return

        table = Table(
            "Agent ID",
            "Address",
            "Capabilities",
            title="Registered ACP Agents"
        )

        for agent_id, info in agents.items():
            address = info.get('address', '[i]N/A[/i]')
            manifest = info.get('manifest', {})
            capabilities = manifest.get('capabilities', [])
            
            table.add_row(
                f"[bold cyan]{agent_id}[/bold cyan]",
                f"[green]{address}[/green]",
                ", ".join(capabilities) if capabilities else "[italic]None[/italic]"
            )
        
        console.print(table)

    except ConnectionError as e:
        console.print(f"[bold red]Error:[/bold red] Could not connect to the Zerocap daemon. Is it running?")
        console.print(f"       ({e})")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

@app.command("info")
def agent_info(
    agent_id: str = typer.Argument(..., help="The unique ID of the agent to inspect.")
):
    """
    Display detailed information about a specific ACP Agent.
    """
    console = Console()
    console.print(f"🔎 Fetching details for agent '[bold cyan]{agent_id}[/bold cyan]'...")

    try:
        info = hub_client.discover_acp_agent(agent_id)
        manifest = info.get("manifest", {})
        
        # --- Build a rich display for the agent's details ---
        
        # Live Info
        address = info.get('address', 'N/A')
        
        # Manifest Info
        name = manifest.get('name', 'N/A')
        description = manifest.get('description', 'No description provided.')
        version = manifest.get('version', 'N/A')
        capabilities = manifest.get('capabilities', [])

        # Create a table for the main details
        details_table = Table.grid(padding=(0, 2))
        details_table.add_column(style="bold magenta")
        details_table.add_column()
        details_table.add_row("Name:", name)
        details_table.add_row("Address:", f"[green]{address}[/green]")
        details_table.add_row("Version:", version)
        details_table.add_row("Description:", Text(description, overflow="fold"))
        
        # Create a table for capabilities
        caps_table = Table("Capabilities", show_header=True, header_style="bold blue")
        if capabilities:
            for cap in capabilities:
                caps_table.add_row(cap)
        else:
            caps_table.add_row("[italic]No capabilities listed.[/italic]")

        # Combine them in a Panel
        console.print(Panel(
            details_table,
            title=f"Agent Details: [bold cyan]{agent_id}[/bold cyan]",
            border_style="blue",
            expand=False
        ))
        console.print(caps_table)

    except ConnectionError as e:
        console.print(f"\n[bold red]Error:[/bold red] Could not find or connect to agent '{agent_id}'.")
        console.print(f"       ({e})")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")