# src/zerocap/daemon/service.py
"""
The core service logic for the Zerocap background daemon.

This service is a long-running FastAPI application that acts as the central
nervous system for the local Zerocap environment. It maintains a real-time
registry of all running MCP Servers and ACP Agents and provides an internal
API for the CLI, UI, and other components to query this state.
"""
import threading
from typing import Any, Dict, List, Optional
from collections import deque
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class HubEvent(BaseModel):
    source_id: str
    target_id: str
    timestamp: float # Unix timestamp
    tool_name: Optional[str] = None

# --- The Daemon's In-Memory Database ---
# A thread-safe dictionary to store the state of the local ecosystem.
# Using a lock ensures that we don't have race conditions if multiple
# clients try to register at the same time.
class ThreadSafeRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {"mcp_servers": {}, "acp_agents": {}}
        self._events: deque[HubEvent] = deque(maxlen=50)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            # Return a deep copy to prevent external modification
            return self._data.copy()
        
     # --- NEW: Method to add an event ---
    def add_event(self, event: HubEvent):
        with self._lock:
            self._events.append(event)
    
    # --- NEW: Method to get all events ---
    def get_events(self) -> List[HubEvent]:
        with self._lock:
            return list(self._events)

    def register_mcp_server(self, name: str, data: Dict[str, Any]):
        with self._lock:
            print(f"DAEMON: Registering MCP Server '{name}'")
            self._data["mcp_servers"][name] = data

    def get_mcp_server(self, name: str) -> Dict[str, Any]:
        with self._lock:
            server = self._data["mcp_servers"].get(name)
            if not server:
                raise KeyError(f"MCP Server '{name}' not found in registry.")
            return server
    
    def register_acp_agent(self, name: str, data: Dict[str, Any]):
        with self._lock:
            print(f"DAEMON: Registering ACP Agent '{name}'")
            self._data["acp_agents"][name] = data

    
    def get_acp_agent(self, name: str) -> Dict[str, Any]:
        with self._lock:
            agent = self._data["acp_agents"].get(name)
            if not agent: raise KeyError(f"ACP Agent '{name}' not found.")
            return agent

    

# --- Singleton Instance of the Registry ---
# This will be the single source of truth for the entire daemon process.
registry = ThreadSafeRegistry()

# --- The Daemon's Internal API Server ---
app = FastAPI(
    title="Zerocap Daemon",
    description="Internal API for the Zerocap local ecosystem.",
    version="0.0.1",
)

@app.get("/status")
def get_hub_status():
    return registry.get_all()

@app.post("/registry/mcp/{server_name}")
def register_mcp_server_endpoint(server_name: str, manifest_data: Dict[str, Any]):
    """Endpoint for MCP Servers to register themselves."""
    registry.register_mcp_server(server_name, manifest_data)
    return {"status": "ok", "registered": server_name}

@app.get("/registry/mcp/{server_name}")
def discover_mcp_server_endpoint(server_name: str):
    """Endpoint for clients (like Agents) to discover MCP Servers."""
    try:
        server = registry.get_mcp_server(server_name)
        return server
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@app.post("/registry/acp/{agent_id}")
def register_acp_agent_endpoint(agent_id: str, registration_data: Dict[str, Any]):
    """Endpoint for ACP Agents to register themselves."""
    registry.register_acp_agent(agent_id, registration_data)
    return {"status": "ok", "registered": agent_id}

@app.get("/registry/acp/{agent_id}")
def discover_acp_agent_endpoint(agent_id: str):
    """Endpoint for clients to discover ACP Agents."""
    try:
        return registry.get_acp_agent(agent_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---Event API Endpoints ---
@app.post("/events", status_code=202)
def report_event(event: HubEvent):
    """Receives a communication event and adds it to the log."""
    registry.add_event(event)
    return {"status": "event recorded"}

@app.get("/events", response_model=List[HubEvent])
def get_events():
    """Returns the list of most recent communication events."""
    return registry.get_events()