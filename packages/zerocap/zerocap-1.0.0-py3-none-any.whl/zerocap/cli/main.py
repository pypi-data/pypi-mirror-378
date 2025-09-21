# src/zerocap/cli/main.py
import typer

from .commands import daemon_cmd, hub_cmd, agent_cmd, server_cmd
from .commands import ui_cmd

app = typer.Typer(
    name="zerocap",
    help="Zerocap - The Universal Framework for AI Capabilities",
    rich_markup_mode="markdown"
)

app.add_typer(daemon_cmd.app, name="daemon")
app.add_typer(hub_cmd.app, name="hub")
app.add_typer(agent_cmd.app, name="agent")
app.add_typer(server_cmd.app, name="server")
app.add_typer(ui_cmd.app, name="ui")

@app.command()
def version():
    """Displays the version of the Zerocap framework."""
    print("Zerocap version: 0.1.0 (Alpha)")

if __name__ == "__main__":
    app()