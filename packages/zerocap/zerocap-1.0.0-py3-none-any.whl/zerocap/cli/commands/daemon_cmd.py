# src/zerocap/cli/commands/daemon_cmd.py
"""
CLI commands for managing the Zerocap daemon.
"""
import typer
import uvicorn
import subprocess
import sys
import os
import json
import socket
import psutil # We need a new dependency for checking PIDs
import time

from zerocap.daemon import service, hub_client

app = typer.Typer(help="Manage the Zerocap local background daemon.")

def _get_daemon_info() -> dict | None:
    """Reads the daemon info file and returns its content, or None."""
    if not os.path.exists(hub_client.DAEMON_INFO_FILE):
        return None
    try:
        with open(hub_client.DAEMON_INFO_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

def _is_pid_running(pid: int) -> bool:
    """Checks if a process with the given PID is currently running."""
    return psutil.pid_exists(pid)

def _write_daemon_info(port: int, pid: int):
    """Creates the daemon info file."""
    os.makedirs(hub_client.ZEROCAP_DIR, exist_ok=True)
    with open(hub_client.DAEMON_INFO_FILE, "w") as f:
        json.dump({
            "address": f"http://127.0.0.1:{port}",
            "port": port,
            "pid": pid,
        }, f)

def _find_free_port(start_port: int) -> int:
    """Finds an available TCP port, starting from a given port."""
    for port in range(start_port, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError("Could not find any free ports.")

@app.command()
def start(
    host: str = "127.0.0.1",
    port: int = typer.Option(hub_client.DEFAULT_DAEMON_PORT, help="The port to start searching from.")
):
    """
    Start the Zerocap daemon, automatically finding a free port.
    """
    daemon_info = _get_daemon_info()
    if daemon_info and _is_pid_running(daemon_info.get("pid")):
        print(f"✅ Zerocap daemon is already running at {daemon_info.get('address')} (PID: {daemon_info.get('pid')}).")
        return

    if daemon_info:
        print("ℹ️  Found a stale daemon info file. Cleaning up and starting a new daemon...")
        os.remove(hub_client.DAEMON_INFO_FILE)

    free_port = _find_free_port(port)
    print(f"🚀 Starting Zerocap daemon on {host}:{free_port}...")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "zerocap.daemon.service:app",
        "--host", host, "--port", str(free_port),
        "--log-level", "warning" # Make the daemon less noisy
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1) # Give the server a moment to start up

    if process.poll() is None: # Check if the process is still running
        _write_daemon_info(port=free_port, pid=process.pid)
        print("✅ Daemon started successfully in the background.")
        print(f"   - PID: {process.pid}")
        print(f"   - Storing connection info in: {hub_client.DAEMON_INFO_FILE}")
    else:
        print("❌ Failed to start the daemon process.")

@app.command()
def status():
    """Check the status of the Zerocap daemon."""
    daemon_info = _get_daemon_info()
    if not daemon_info:
        print("❌ Zerocap daemon is not running (no info file found).")
        return
        
    pid = daemon_info.get("pid")
    if pid and _is_pid_running(pid):
        print(f"✅ Zerocap daemon is running.")
        print(f"   - PID: {pid}")
        print(f"   - Address: {daemon_info.get('address')}")
    else:
        print("❌ Zerocap daemon is not running (stale info file found).")
        
@app.command()
def stop():
    """Stop the running Zerocap daemon."""
    daemon_info = _get_daemon_info()
    if not daemon_info:
        print("ℹ️  Zerocap daemon is already stopped.")
        return
        
    pid = daemon_info.get("pid")
    if pid and _is_pid_running(pid):
        print(f"Stopping Zerocap daemon (PID: {pid})...")
        process = psutil.Process(pid)
        process.terminate()
        print("✅ Daemon stopped.")
    else:
        print("ℹ️  Daemon was not running (stale info file).")
    
    os.remove(hub_client.DAEMON_INFO_FILE)