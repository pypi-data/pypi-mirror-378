# src/zerocap/cli/commands/ui_cmd.py
"""
CLI command for launching the Zerocap Visual Orchestrator UI.
"""
import typer
import uvicorn
import webbrowser
import socket # Import the socket library

from zerocap.daemon import hub_client

app = typer.Typer(help="Launch and manage the Zerocap UI.")

# This is now the *default* port to try first.
DEFAULT_UI_PORT = 8501

# --- NEW HELPER FUNCTION (can be moved to a shared utils file later) ---
def _find_free_port(start_port: int) -> int:
    """Finds an available TCP port, starting from a given port."""
    for port in range(start_port, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError(f"Could not find any free ports starting from {start_port}.")

@app.command()
def launch(
    port: int = typer.Option(DEFAULT_UI_PORT, "--port", "-p", help="The port to try starting the UI on.")
):
    """
    Launch the Zerocap Visual Orchestrator, finding a free port if needed.
    """
    print("🚀 Launching Zerocap UI...")
    
    if not hub_client._is_daemon_running():
        print("🟡 Zerocap daemon is not running. Live data will be unavailable.")
        print("   Run `zerocap daemon start` in another terminal for full functionality.")

    # --- UPDATED LOGIC ---
    # Find a free port, starting with the default or user-provided one.
    try:
        actual_port = _find_free_port(port)
        if actual_port != port:
            print(f"🟡 Port {port} was busy. Using next available port: {actual_port}")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)

    from zerocap.ui.backend.main import app as ui_app
    
    final_url = f"http://127.0.0.1:{actual_port}"
    
    print(f"✅ UI Server is running at: {final_url}")
    print("   Opening this in your default web browser...")

    webbrowser.open(final_url)
    
    # Run the server on the port we actually found to be free.
    uvicorn.run(ui_app, host="127.0.0.1", port=actual_port)