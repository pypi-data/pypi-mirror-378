"""Government Scheme MCP Server.

A Model Context Protocol (MCP) server for accessing Indian Government Schemes database.
Provides tools for searching, creating, and managing government benefit schemes.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import mcp

__all__ = ["mcp"]