# src/zerocap/__init__.py

# Expose the core classes for developers to import directly.
from .core.mcp.server import McpServer, tool
from .core.acp.agent import Agent, capability
from .core.acp.models import Part as Artifact # Give 'Part' a more user-friendly alias

# --- NEW: Expose the client ---
from .client import ZerocapClient