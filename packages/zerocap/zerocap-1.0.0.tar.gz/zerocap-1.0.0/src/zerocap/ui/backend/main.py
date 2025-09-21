# src/zerocap/ui/backend/main.py
"""
The FastAPI backend server for the Zerocap Visual Orchestrator UI.

This server is responsible for two things:
1. Serving the static files of the compiled React frontend application.
2. Providing a real-time API that the frontend can query to get the status
   of the Zerocap ecosystem from the running daemon.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from zerocap.client import ZerocapClient
import os
from pydantic import BaseModel, Field
from zerocap.daemon import hub_client
import httpx
from typing import Optional
app = FastAPI(
    title="Zerocap UI Backend",
    version="0.1.0"
)

# --- CORS Middleware ---
# This is crucial for local development, allowing the React development server
# (on a different port) to talk to this FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/api/v1/topology")
def get_system_topology():
    try:
        hub_data = hub_client.get_hub_status()
        nodes = []
        edges = []
        
        # --- NEW: Add dynamic positioning logic ---
        server_y_pos = 100
        agent_y_pos = 100

        # Process MCP Servers as nodes
        for name, info in hub_data.get("mcp_servers", {}).items():
            nodes.append({
                "id": f"server-{name}",
                "type": "serverNode",
                # Position servers in a column on the left
                "position": {"x": 150, "y": server_y_pos},
                "data": { "label": name, "info": info }
            })
            server_y_pos += 120 # Increment Y position for the next server

        # Process ACP Agents as nodes
        for agent_id, info in hub_data.get("acp_agents", {}).items():
            agent_node_id = f"agent-{agent_id}"
            nodes.append({
                "id": agent_node_id,
                "type": "agentNode",
                # Position agents in a column on the right
                "position": {"x": 550, "y": agent_y_pos},
                "data": { "label": agent_id, "info": info }
            })
            agent_y_pos += 120 # Increment Y position for the next agent

            # Create edges for declared dependencies
            manifest = info.get("manifest", {})
            dependencies = manifest.get("requires_mcp_servers", []) # This key doesn't exist yet, we'll add it
            for dep_name in dependencies:
                edges.append({
                    "id": f"edge-{agent_id}-to-{dep_name}",
                    "source": agent_node_id,
                    "target": f"server-{dep_name}",
                    "animated": True # Make the connection line pulse
                })

        return {"nodes": nodes, "edges": edges}

    except ConnectionError as e:
        # If the daemon isn't running, return an empty state so the UI doesn't crash.
        return {"nodes": [], "edges": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RunRequest(BaseModel):
    agent_id: str
    capability_name: str
    prompt: str
    session_id: Optional[str] = None

@app.get("/api/v1/events")
def get_events_from_daemon():
    """
    Fetches the latest events from the daemon and proxies them to the frontend.
    """
    try:
        return hub_client.get_events()
    except ConnectionError:
        return []
    
@app.post("/api/v1/run-capability")
async def run_capability(request: RunRequest):
    """
    Acts as a client to run a capability, now with session support.
    """
    print(f"UI BACKEND: Received run request for {request.agent_id} (Session: {request.session_id})")
    try:
        client = ZerocapClient()
        
        if request.session_id:
            # If a session ID is provided, we can't use the simple client.
            # We need to act like a session object.
            # This is a more direct implementation for now.
            agent_info = hub_client.discover_acp_agent(request.agent_id)
            agent_address = agent_info.get("address")
            
            async with httpx.AsyncClient() as http_client:
                run_input = {
                    "capability_name": request.capability_name,
                    "input_message": {"role": "user/ui", "parts": [{"content_type": "text/plain", "content": request.prompt}]},
                    "session_id": request.session_id
                }
                response = await http_client.post(f"{agent_address}/agent/runs", json=run_input)
                response.raise_for_status()
                # We just need the run data, polling is handled by the client lib
                final_run_data = response.json()
                # For simplicity, we assume the run completes quickly for the UI
                # In a real app, you might poll here too.
                # Let's use the client to poll for completion
                run_id = final_run_data.get("id")
                final_run = await client._poll_for_completion(f"{agent_address}/agent/runs/{run_id}")

        else:
            # If no session, use the simple stateless run
            final_run = await client.run(
                agent_id=request.agent_id,
                capability_name=request.capability_name,
                prompt=request.prompt
            )
        
        return final_run.model_dump()

    except Exception as e:
        print(f"UI BACKEND: Error during run: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Construct the path to the 'dist' directory relative to this file
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.exists(static_dir):
    print(f"✅ Found static UI files. Serving from: {static_dir}")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    print("🟡 Warning: Static UI directory not found. The UI will not be served.")
    print(f"   (Searched for: {static_dir})")
    print("   (Did you run `npm run build` in the frontend directory?)")

