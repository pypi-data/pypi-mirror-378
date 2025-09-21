# src/zerocap/core/acp/agent.py
"""
The Agent base class and related components for ACP.

This module provides the `Agent` abstract base class, which developers will
subclass to create their own autonomous agents. The class provides a full
ACP-compliant web server, manages the lifecycle of agent runs, and uses
decorators to expose agent capabilities.
"""
import abc
import asyncio
import inspect
import uuid
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional, Type
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException, Body

from zerocap.daemon import hub_client
from .models import AgentManifest, AgentRun, Message, Part
from zerocap.core.mcp.models import Context as MCPContext, ToolCallRequest
import httpx


# In-memory storage for agent runs. In a production system, this could be
# backed by Redis, a database, or the Zerocap Daemon.
RUN_STORAGE: Dict[uuid.UUID, AgentRun] = {}
# In-memory storage for session states ---
# In a real system, this would be a database or Redis.
STATE_STORAGE: Dict[uuid.UUID, BaseModel] = {}

class _MCPToolProxy:
    """
    An internal, dynamically created callable class that represents a single
    remote tool on an MCP Server. This proxy makes remote tool calls look
    like local function calls.
    """
    def __init__(self, agent_id: str, server_name: str, server_address: str, model_id: str, tool_name: str, tool_params: Dict):
        # --- NEW: Store agent_id and server_name for event reporting ---
        self.agent_id = agent_id
        self.server_name = server_name
        self.url = f"{server_address}/v1/models/{model_id}/context"
        self.tool_name = tool_name
        self.tool_params = tool_params

    async def __call__(self, **kwargs: Any) -> Any:
        print(f"AGENT-MCP-PROXY: Calling tool '{self.tool_name}' on {self.url} with args: {kwargs}")
        hub_client.report_event(source_id=self.agent_id, target_id=self.server_name, tool_name=self.tool_name)
        
        tool_call_request = ToolCallRequest(name=self.tool_name, arguments=kwargs)
        context = MCPContext(tool_call=tool_call_request)

        # --- THIS IS THE FIX ---
        # We explicitly serialize to a JSON string to ensure aliases and all
        # Pydantic settings are correctly applied before sending.
        json_payload = context.model_dump_json(by_alias=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.url, 
                content=json_payload, # Send the raw JSON string
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            response_data = response.json()
        
        if not response_data.get("tool_calls"):
            raise ValueError(f"MCP Server response for tool '{self.tool_name}' contained no tool_calls. Server message: {response_data.get('message')}")
        
        tool_call_result = response_data["tool_calls"][0]
        if tool_call_result.get("tool_name") != self.tool_name:
            raise ValueError("MCP Server returned a result for a different tool than was called.")
        
        return tool_call_result.get("result")


class MCPClientGroup:
    """A container for dynamically created MCP clients."""
    pass

def capability(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    A decorator to mark an async method within an Agent as a discoverable capability.

    The framework will expose this method as a runnable task via the ACP server.
    The method must be a coroutine (defined with `async def`).

    Args:
        func: The async method to be decorated.

    Returns:
        The decorated method with a special attribute for discovery.
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError("A @capability method must be defined with 'async def'")
    
    setattr(func, "_is_zerocap_capability", True)
    return func

class MCPToolClient:
    """A dynamically created client for an MCP Server's tool."""
    def __init__(self, server_address: str, tool_name: str):
        self.url = f"{server_address}/v1/models/default-model/context" # Needs refinement
        self.tool_name = tool_name

    async def __call__(self, **kwargs):
        # This is a simplified call, assuming tool use.
        # A real implementation would be more robust.
        print(f"MCP CLIENT: Calling {self.tool_name} with {kwargs}")
        context_data = { "messages": [{"role": "agent", "content": f"Use tool {self.tool_name}"}] }
        async with httpx.AsyncClient() as client:
            # This is a placeholder for a real tool-calling implementation
            response = await client.post(self.url, json=context_data)
            response.raise_for_status()
            return response.json()

class Agent(abc.ABC):
    """
    An abstract base class for creating an ACP-compliant Agent.

    Developers inherit from this class, define agent metadata as class attributes,
    and implement their core logic in methods decorated with `@capability`.
    """
    # --- Metadata attributes that subclasses MUST override ---
    agent_id: str = "default-agent"
    name: str = "Default Zerocap Agent"
    description: str = "This is a default agent."
    requires_mcp_servers: List[str] = []

    # --- Optional metadata ---
    version: str = "0.0.1"
    host: str = "127.0.0.1"
    port: int = 0  # Default to 0 for automatic port allocation
    state_model: Optional[Type[BaseModel]] = None

    def __init__(self):
        self.state: Optional[BaseModel] = None
        self._capabilities: Dict[str, Callable] = self._discover_capabilities()
        self.manifest = self._create_manifest()
        # The MCP Client object for dependency injection ---
        self.mcp = MCPClientGroup()
        self._initialize_mcp_clients()
        self.app = self._create_app()

    def _initialize_mcp_clients(self):
        """
        Discovers required MCP servers, fetches their manifests, and injects
        dynamically created, smart tool proxies into `self.mcp`.
        """
        print(f"AGENT [{self.name}]: Fulfilling MCP server requirements...")
        for server_name in self.requires_mcp_servers:
            try:
                server_info = hub_client.discover_mcp_server(server_name)
                server_manifest = server_info.get("manifest", {})
                server_client = MCPClientGroup()
                
                for tool_def in server_manifest.get("tools", []):
                    tool_name = tool_def.get("name")
                    if not tool_name: continue
                    
                    # --- UPGRADE ---
                    # We now pass the tool's parameter schema to the proxy
                    tool_proxy = _MCPToolProxy(
                        # --- Pass agent_id and server_name to the proxy ---
                        agent_id=self.agent_id,
                        server_name=server_name,
                        server_address=server_info["address"],
                        model_id=server_manifest.get("model_id", "default-model"),
                        tool_name=tool_name,
                        tool_params=tool_def.get("parameters", {})
                    )
                    
                    attribute_name = tool_name.replace('-', '_')
                    setattr(server_client, attribute_name, tool_proxy)
                
                client_attribute_name = server_name.replace('-', '_')
                setattr(self.mcp, client_attribute_name, server_client)
                
                print(f"  - Successfully connected to '{server_name}' (as self.mcp.{client_attribute_name})")
                print(f"    - Injected tools: {[t.get('name') for t in server_manifest.get('tools', [])]}")
            except Exception as e:
                print(f"  - ❌ FAILED to connect to '{server_name}': {e}")

    def _discover_capabilities(self) -> Dict[str, Callable]:
        """Discovers methods decorated with @capability and maps them by name."""
        discovered = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_zerocap_capability"):
                discovered[name] = method
        return discovered

    def _create_manifest(self) -> AgentManifest:
        """Creates the agent's public manifest from its metadata."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            version=self.version,
            capabilities=list(self._capabilities.keys())
        )

    async def _run_capability_background(self, run_id: uuid.UUID):
        run = RUN_STORAGE.get(run_id)
        if not run: return
        
        # Extract details from the run object
        capability_name = run.input.metadata.get("capability_name", "")
        session_id = run.session_id

        run.status = "in-progress"; run.updated_at = datetime.utcnow()

        try:
            # --- STATE LOADING ---
            if session_id and self.state_model:
                # If in a session, load the existing state or create a new one.
                self.state = STATE_STORAGE.get(session_id)
                if not self.state:
                    self.state = self.state_model() # Create a new default state
                    print(f"AGENT: New session '{session_id}', creating initial state.")
            
            capability_method = self._capabilities[capability_name]
            first_text_part = next((p.content for p in run.input.parts if p.content_type == 'text/plain'), "")
            result = await capability_method(first_text_part)
            
            # --- STATE SAVING ---
            if session_id and self.state:
                # After capability runs, save the (potentially modified) state.
                STATE_STORAGE[session_id] = self.state
                print(f"AGENT: Saved state for session '{session_id}'.")
            
            output_message = Message(role=self.agent_id, parts=[])
            if isinstance(result, Part): output_message.parts.append(result)
            elif isinstance(result, str): output_message.parts.append(Part(content_type="text/plain", content=result))
            else: output_message.parts.append(Part(content_type="application/json", content=result))
            run.output.append(output_message); run.status = "completed"
        except Exception as e:
            run.status = "failed"
            error_part = Part(content_type="text/plain", content=f"Agent failed with error: {e}")
            run.output.append(Message(role="system/error", parts=[error_part]))
            print(f"ERROR executing run {run.id}: {e}")
        finally:
            # --- STATE CLEANUP ---
            # Unset the state so the next run starts fresh.
            self.state = None
            run.updated_at = datetime.utcnow()

    def _create_app(self) -> FastAPI:
        app = FastAPI(title=f"Zerocap Agent: {self.name}", version=self.version)
        @app.get("/agent", response_model=AgentManifest)
        async def get_manifest(): return self.manifest

        # --- UPDATED: The create_run endpoint now accepts a session_id ---
        @app.post("/agent/runs", response_model=AgentRun, status_code=202)
        async def create_run(
            capability_name: str = Body(...),
            input_message: Message = Body(...),
            session_id: Optional[uuid.UUID] = Body(None)
        ):
            if capability_name not in self._capabilities: raise HTTPException(status_code=404, detail=f"Capability not found.")
            
            # Add capability_name to metadata so the background runner knows what to do
            input_message.metadata["capability_name"] = capability_name

            run = AgentRun(
                agent_id=self.agent_id,
                input=input_message,
                session_id=session_id
            )
            RUN_STORAGE[run.id] = run
            asyncio.create_task(self._run_capability_background(run.id))
            return run

        @app.get("/agent/runs/{run_id}", response_model=AgentRun)
        async def get_run(run_id: uuid.UUID):
            run = RUN_STORAGE.get(run_id)
            if not run: raise HTTPException(status_code=404, detail=f"Run not found.")
            return run
        return app

    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Starts the FastAPI web server for this Agent with auto-registration."""
        run_host = host or self.host
        run_port = port if port is not None else self.port

        config = uvicorn.Config(self.app, host=run_host, port=run_port, log_level="info")
        server = uvicorn.Server(config)

        original_startup = server.startup
        async def custom_startup(*args, **kwargs):
            await original_startup(*args, **kwargs)
            actual_port = server.servers[0].sockets[0].getsockname()[1]
            address = f"http://{run_host}:{actual_port}"
            
            print(f"✅ Starting ACP Agent '{self.name}' (ID: {self.agent_id})...")
            
            try:
                hub_client.register_acp_agent(
                    agent_id=self.agent_id,
                    address=address,
                    # Pydantic V2 uses model_dump()
                    manifest=self.manifest.model_dump()
                )
                print(f"   - Registered with Local Hub")
            except Exception as e:
                print(f"❌ Error registering agent with Zerocap Hub: {e}")
            
            print(f"   - Listening on: {address}")
            print(f"   - Discovered {len(self._capabilities)} capabilities: {list(self._capabilities.keys())}")

        server.startup = custom_startup
        
        try:
            server.run()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ Error: Port {run_port} is already in use.")
            else:
                raise e