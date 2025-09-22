"""FastMCP - A more ergonomic interface for MCP servers."""

from importlib.metadata import version

from .server import Context, FastMCP
from .utilities.types import Image

__version__ = version("mcp-aipy")
__all__ = ["FastMCP", "Context", "Image"]
