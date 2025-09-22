"""
Online Boutique AI Assistant MCP Server

Model Context Protocol server for Online Boutique AI Assistant,
exposing microservices via standardized MCP protocol.
"""

__version__ = "1.0.0"
__author__ = "Arjun Prabhulal"
__email__ = "code.aicloudlab@gmail.com"

from . import mcp_server

__all__ = ["mcp_server"]
