# src/zerocap/core/mcp/models.py
"""
Pydantic models for the Model Context Protocol (MCP).

This module defines the core data structures used to communicate with an MCP server.
These models ensure that any context object sent to a model is well-formed,
validated, and easily serializable to and from JSON.
"""
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl

# Using a generic dictionary for JSON Schema properties for flexibility.
JsonSchemaObject = Dict[str, Any]


class Message(BaseModel):
    """
    Represents a single message in a conversation, conforming to a common
    multi-modal chat structure.
    """
    role: str = Field(
        ...,
        description="The role of the entity sending the message (e.g., 'user', 'agent', 'system')."
    )
    content: str = Field(
        ...,
        description="The textual content of the message."
    )

    # CORRECTED: Pydantic V2 configuration syntax.
    model_config = {
        "extra": "allow"  # Allow additional fields for custom metadata.
    }


class ToolParameters(BaseModel):
    """
    Defines the parameters for a tool using a JSON Schema-like structure.
    """
    type: Literal["object"] = "object"
    properties: Dict[str, JsonSchemaObject] = Field(
        ...,
        description="A dictionary mapping parameter names to their JSON schema definitions."
    )
    required: List[str] = Field(
        default=[],
        description="A list of required parameter names."
    )


class ToolDefinition(BaseModel):
    """
    Represents a single tool (function) that the model can be instructed to use.
    """
    name: str = Field(
        ...,
        description="The name of the function to be called."
    )
    description: str = Field(
        ...,
        description="A detailed description of what the function does."
    )
    parameters: ToolParameters = Field(
        ...,
        description="The JSON schema for the parameters the function accepts."
    )


class File(BaseModel):
    """
    Represents a file provided as context, which can be referenced by URL
    or included directly as inline content.
    """
    name: str = Field(
        ...,
        description="The name of the file (e.g., 'document.pdf')."
    )
    content: Optional[str] = Field(
        default=None,
        description="The base64-encoded content of the file. Use for small files."
    )
    url: Optional[HttpUrl] = Field(
        default=None,
        description="A publicly accessible URL where the file can be downloaded."
    )
    media_type: Optional[str] = Field(
        default=None,
        description="The MIME type of the file (e.g., 'text/plain', 'application/pdf')."
    )


class ModelConfiguration(BaseModel):
    """
    Defines configuration options that control the behavior of the AI model's
    generation process.
    """
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0,
        description="Controls randomness. Lower is more deterministic."
    )
    max_tokens: Optional[int] = Field(
        default=None, gt=0,
        description="The maximum number of tokens to generate."
    )
    top_p: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Nucleus sampling parameter."
    )
    extra_config: Dict[str, Any] = Field(default_factory=dict)

class ToolCallRequest(BaseModel):
    """
    A structured request to call a specific tool.
    This is sent from the client (Agent) to the server.
    """
    name: str = Field(..., description="The name of the tool to execute.")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="The arguments for the tool.")

class ToolCallResult(BaseModel):
    """
    A structured result from a tool execution.
    This is sent from the server back to the client.
    """
    tool_name: str = Field(..., description="The name of the tool that was executed.")
    result: Any = Field(..., description="The return value from the tool execution.")

class McpResponse(BaseModel):
    """
    A standardized response envelope for all MCP server interactions.
    This ensures that clients can reliably parse server responses.
    """
    message: Optional[str] = "Request processed."
    tool_calls: List[ToolCallResult] = Field(default_factory=list)

class Context(BaseModel):
    """
    The main MCP Context object.

    This is the top-level container for all information provided to a model
    in a single request. It encapsulates messages, files, available tools,
    and model configuration.
    """
    messages: List[Message] = Field(
        default_factory=list,
        description="The conversational history or prompt."
    )
    files: List[File] = Field(
        default_factory=list,
        description="A list of files provided as context to the model."
    )
    tools: List[ToolDefinition] = Field(
        default_factory=list,
        description="A list of tools the model is allowed to use."
    )
    model_config_field: ModelConfiguration = Field(
        default_factory=ModelConfiguration,
        description="Configuration settings for the model's response generation.",
        # CORRECTED: Renamed the field to avoid conflict with the Pydantic V2 'model_config' attribute.
        alias="model_config"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="An optional top-level system prompt to guide the model's behavior."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="An open-ended dictionary for any additional metadata."
    )
    tool_call: Optional[ToolCallRequest] = Field(
        None,
        description="An optional, direct request to execute a specific tool."
    )
    model_config = {
        "extra": "forbid"  # Disallow any fields not explicitly defined in the context.
    }