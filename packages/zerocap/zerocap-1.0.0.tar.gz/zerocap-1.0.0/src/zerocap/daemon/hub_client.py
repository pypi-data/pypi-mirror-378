# src/zerocap/daemon/hub_client.py
"""
A resilient, network client for the Zerocap Local Hub Daemon.
It finds the daemon by reading a port file from a well-known location.
"""
import json
import os
import httpx
from typing import Dict, Any, Optional, List
import psutil
import time

ZEROCAP_DIR = os.path.join(os.path.expanduser("~"), ".zerocap")
DAEMON_INFO_FILE = os.path.join(ZEROCAP_DIR, "daemon.json")
DEFAULT_DAEMON_PORT = 11337

def _is_daemon_running() -> bool:
    """
    Checks if the daemon is truly running by verifying its PID first,
    then checking its network health.
    """
    info = get_daemon_info()
    if not info:
        return False
    
    pid = info.get("pid")
    if not pid or not psutil.pid_exists(pid):
        return False
    
    # If the PID exists, we can now safely try to connect.
    address = info.get("address")
    if not address:
        return False
        
    try:
        with httpx.Client() as client:
            response = client.get(f"{address}/status", timeout=1.0)
            return response.status_code == 200
    except httpx.ConnectError:
        # The PID exists but the server is not responding. It might be starting up or frozen.
        return False
    
def get_daemon_info() -> Optional[Dict[str, Any]]:
    """Reads the daemon info file and returns its content, or None."""
    if not os.path.exists(DAEMON_INFO_FILE):
        return None
    try:
        with open(DAEMON_INFO_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

def get_daemon_address() -> Optional[str]:
    """
    Reads the daemon info file to find the currently running daemon's address.
    """
    if not os.path.exists(DAEMON_INFO_FILE):
        return None
    try:
        with open(DAEMON_INFO_FILE, "r") as f:
            info = json.load(f)
            return info.get("address")
    except (IOError, json.JSONDecodeError):
        return None



def get_hub_status() -> Dict[str, Any]:
    """
    Connects to the daemon and retrieves the full status of the registry.
    """
    daemon_address = get_daemon_address()
    if not daemon_address:
        raise ConnectionError("Could not find Zerocap daemon info file. Is the daemon running?")
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{daemon_address}/status")
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise ConnectionError(f"Could not connect to the Zerocap daemon at {daemon_address}.")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Daemon returned an error while fetching status: {e.response.text}")

def register_mcp_server(name: str, address: str, manifest: Dict[str, Any]):
    """Registers an MCP Server with the running daemon."""
    daemon_address = get_daemon_address()
    if not daemon_address:
        raise ConnectionError("Could not find Zerocap daemon info file. Is the daemon running? Try `zerocap daemon start`.")
        
    print(f"[HUB CLIENT] Registering MCP Server '{name}' with daemon at {daemon_address}")
    registration_data = {"address": address, "manifest": manifest}
    try:
        with httpx.Client() as client:
            response = client.post(f"{daemon_address}/registry/mcp/{name}", json=registration_data)
            response.raise_for_status()
        print(f"[HUB CLIENT] Successfully registered '{name}'.")
    except httpx.ConnectError:
        raise ConnectionError(f"Could not connect to the Zerocap daemon at {daemon_address}. Is it running?")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Daemon returned an error during registration: {e.response.text}")

def discover_mcp_server(name: str) -> Dict[str, Any]:
    """Discovers an MCP Server from the running daemon."""
    daemon_address = get_daemon_address()
    if not daemon_address:
        raise ConnectionError("Could not find Zerocap daemon info file. Is the daemon running? Try `zerocap daemon start`.")

    print(f"[HUB CLIENT] Discovering MCP Server '{name}' from daemon at {daemon_address}...")
    try:
        with httpx.Client() as client:
            response = client.get(f"{daemon_address}/registry/mcp/{name}")
            response.raise_for_status()
            server_info = response.json()
        print(f"[HUB CLIENT] Discovered '{name}' at {server_info.get('address')}")
        return server_info
    except httpx.ConnectError:
        raise ConnectionError(f"Could not connect to the Zerocap daemon at {daemon_address}. Is it running?")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ConnectionError(f"MCP Server '{name}' not found in the Zerocap Hub. Is the server running?")
        raise RuntimeError(f"Daemon returned an error during discovery: {e.response.text}")
    
def register_acp_agent(agent_id: str, address: str, manifest: Dict[str, Any]):
    """Registers a running ACP Agent with the local hub via the network."""
    daemon_address = get_daemon_address()
    if not daemon_address:
        raise ConnectionError("Could not find Zerocap daemon info file. Is the daemon running?")
    
    print(f"[HUB CLIENT] Registering ACP Agent '{agent_id}' with daemon at {daemon_address}")
    registration_data = {"address": address, "manifest": manifest}
    
    try:
        with httpx.Client() as client:
            response = client.post(f"{daemon_address}/registry/acp/{agent_id}", json=registration_data)
            response.raise_for_status()
        print(f"[HUB CLIENT] Successfully registered '{agent_id}'.")
    except (httpx.ConnectError, httpx.HTTPStatusError) as e:
        raise RuntimeError(f"Agent registration with daemon failed: {e}")

def discover_acp_agent(agent_id: str) -> Dict[str, Any]:
    """Discovers a registered ACP Agent by its ID."""
    daemon_address = get_daemon_address()
    if not daemon_address:
        raise ConnectionError("Could not find Zerocap daemon info file. Is the daemon running?")

    print(f"[HUB CLIENT] Discovering ACP Agent '{agent_id}' from daemon...")
    try:
        with httpx.Client() as client:
            response = client.get(f"{daemon_address}/registry/acp/{agent_id}")
            response.raise_for_status()
            agent_info = response.json()
        
        print(f"[HUB CLIENT] Discovered '{agent_id}' at {agent_info.get('address')}")
        return agent_info
    except (httpx.ConnectError, httpx.HTTPStatusError) as e:
        raise ConnectionError(f"Agent discovery from daemon failed: {e}")
    
def report_event(source_id: str, target_id: str, tool_name: Optional[str] = None):
    """
    Reports a communication event to the daemon.
    This is a 'fire-and-forget' call; failures are logged but don't crash the caller.
    """
    daemon_address = get_daemon_address()
    if not daemon_address:
        return # Silently fail if daemon isn't running

    event_data = {
        "source_id": f"agent-{source_id}", # Construct the full node ID
        "target_id": f"server-{target_id}",
        "timestamp": time.time(),
        "tool_name": tool_name
    }
    
    try:
        # Use a short timeout as this shouldn't block the agent
        with httpx.Client(timeout=0.5) as client:
            client.post(f"{daemon_address}/events", json=event_data)
    except Exception as e:
        # Log the error but don't interrupt the agent's operation
        print(f"[HUB CLIENT WARNING] Failed to report event to daemon: {e}")

def get_events() -> List[Dict[str, Any]]:
    """Fetches the latest events from the daemon."""
    daemon_address = get_daemon_address()
    if not daemon_address:
        return [] # Return empty list if daemon is down
    try:
        with httpx.Client(timeout=1.0) as client:
            response = client.get(f"{daemon_address}/events")
            response.raise_for_status()
            return response.json()
    except (httpx.ConnectError, httpx.HTTPStatusError):
        return []