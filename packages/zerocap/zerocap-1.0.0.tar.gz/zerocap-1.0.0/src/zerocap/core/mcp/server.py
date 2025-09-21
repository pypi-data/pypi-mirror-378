# src/zerocap/core/mcp/server.py
"""
The McpServer base class and related components.
"""
import abc
import inspect
from typing import Any, Callable, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import (
    Context, ToolDefinition, ToolParameters, JsonSchemaObject,
    McpResponse, ToolCallResult
)
from zerocap.daemon import hub_client


def tool(func: Callable) -> Callable:
    """Decorator to mark a method as a discoverable tool."""
    setattr(func, "_is_zerocap_tool", True)
    return func


class McpServer(abc.ABC):
    """Abstract base class for creating an MCP Server."""
    name: str = "default-mcp-server"
    model_id: str = "default-model"
    host: str = "127.0.0.1"
    port: int = 0

    def __init__(self):
        self.tools: List[ToolDefinition] = self._discover_tools()
        self._tool_map: Dict[str, Callable] = self._create_tool_map()
        self.app = self._create_app()

    def _create_tool_map(self) -> Dict[str, Callable]:
        """Creates a mapping from tool names to their actual methods."""
        tool_map = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_zerocap_tool"):
                tool_map[name] = method
        return tool_map
    
    # ---A new abstract method for the fallback case ---
    @abc.abstractmethod
    async def default_handler(self, context: Context) -> McpResponse:
        """
        The handler for when no specific tool is called.

        This method is called when the incoming context does not contain a
        `tool_call` request. It should be implemented by subclasses that
        need to perform more general tasks, like calling an LLM.

        Args:
            context: A validated MCP Context object.

        Returns:
            A standardized McpResponse object.
        """
        raise NotImplementedError("default_handler must be implemented by a subclass")
    
    async def invoke_model(self, context: Context) -> McpResponse:
        """
        The core logic router for the MCP Server.

        If the context contains a `tool_call`, this method automatically
        executes the corresponding @tool method. Otherwise, it calls the
        `default_handler` for custom processing.
        """
        if context.tool_call:
            tool_name = context.tool_call.name
            tool_args = context.tool_call.arguments

            if tool_name not in self._tool_map:
                raise ValueError(f"Tool '{tool_name}' is not defined on this server.")

            print(f"MCP SERVER: Executing tool '{tool_name}' with args: {tool_args}")
            tool_method = self._tool_map[tool_name]
            
            try:
                result = await tool_method(**tool_args)
                tool_result = ToolCallResult(tool_name=tool_name, result=result)
                return McpResponse(tool_calls=[tool_result])
            except TypeError as e:
                # This happens if the agent sends the wrong arguments
                print(f"MCP SERVER ERROR: TypeError executing tool '{tool_name}': {e}")
                raise ValueError(f"Invalid arguments for tool '{tool_name}'. Details: {e}")
        else:
            # If no specific tool was requested, use the fallback handler
            return await self.default_handler(context)

    def _discover_tools(self) -> List[ToolDefinition]:
        # This logic is correct and remains unchanged.
        discovered_tools = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_zerocap_tool"):
                sig = inspect.signature(method)
                docstring = inspect.getdoc(method) or "No description provided."
                properties, required = {}, []
                for param in sig.parameters.values():
                    if param.name == 'self': continue
                    param_type = "string"
                    if param.annotation in (int, float): param_type = "number"
                    elif param.annotation == bool: param_type = "boolean"
                    elif inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel):
                        properties[param.name] = param.annotation.model_json_schema()
                        if param.default is inspect.Parameter.empty: required.append(param.name)
                        continue
                    properties[param.name] = {"type": param_type, "description": ""}
                    if param.default is inspect.Parameter.empty: required.append(param.name)
                tool_def = ToolDefinition(name=name, description=docstring.strip(),
                                          parameters=ToolParameters(properties=properties, required=required))
                discovered_tools.append(tool_def)
        return discovered_tools
    
    def _create_manifest(self) -> Dict[str, Any]:
        """Creates a JSON-serializable manifest for this server."""
        return {"name": self.name, "model_id": self.model_id,
                "tools": [tool.model_dump() for tool in self.tools]}
        
    def _create_app(self) -> FastAPI:
        app = FastAPI(title=f"Zerocap MCP Server: {self.name}", version="0.0.1")
        # NOTE: The response model is now McpResponse
        @app.post(f"/v1/models/{self.model_id}/context", response_model=McpResponse)
        async def handle_context_request(context: Context) -> McpResponse:
            try:
                server_tool_names = {t.name for t in self.tools}
                client_only_tools = [t for t in context.tools if t.name not in server_tool_names]
                context.tools = self.tools + client_only_tools
                # This now calls our new router method
                return await self.invoke_model(context)
            except Exception as e:
                print(f"Error processing context: {e}")
                # Return a structured error in the McpResponse format
                return McpResponse(message=f"Error processing request: {e}", tool_calls=[])
        @app.get("/.zerocap/health")
        def health_check():
            return {"status": "ok", "server_name": self.name}
        return app

    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Starts the FastAPI web server to serve this MCP instance."""
        run_host = host or self.host
        run_port = port if port is not None else self.port

        config = uvicorn.Config(self.app, host=run_host, port=run_port, log_level="info")
        server = uvicorn.Server(config)

        # --- CORRECTED STARTUP HOOK ---
        original_startup = server.startup
        
        # CORRECTED: The function must accept the same arguments as the original.
        async def custom_startup(*args, **kwargs):
            # CORRECTED: Pass the arguments through to the original function.
            await original_startup(*args, **kwargs)
            
            # Now we can safely run our custom logic after the real startup.
            actual_port = server.servers[0].sockets[0].getsockname()[1]
            address = f"http://{run_host}:{actual_port}"
            
            print(f"✅ Starting MCP Server '{self.name}'...")
            
            try:
                hub_client.register_mcp_server(name=self.name, address=address, manifest=self._create_manifest())
                print(f"   - Registered with Local Hub")
            except Exception as e:
                print(f"❌ Error registering with Zerocap Hub: {e}")
            
            print(f"   - Listening on: {address}")
            print(f"   - Model ID: {self.model_id}")
            print(f"   - Discovered {len(self.tools)} tools: {[t.name for t in self.tools]}")

        server.startup = custom_startup
        
        try:
            server.run()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ Error: Port {run_port} is already in use. Please choose another.")
            else:
                raise e