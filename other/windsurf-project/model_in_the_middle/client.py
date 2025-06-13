"""Client library for interacting with Model in the Middle."""

import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class MITMClient:
    """Client for interacting with a Model in the Middle server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the MITM client.
        
        Args:
            base_url: Base URL of the MITM server
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()
    
    async def list_tools(self, query: str = "") -> List[Dict[str, Any]]:
        """List all available tools, optionally filtered by query.
        
        Args:
            query: Optional search query to filter tools
            
        Returns:
            List of tool definitions
        """
        params = {"query": query} if query else {}
        response = await self.client.get(
            f"{self.base_url}/tools",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool response
        """
        response = await self.client.post(
            f"{self.base_url}/call",
            json={"tool_name": tool_name, "parameters": kwargs}
        )
        response.raise_for_status()
        return response.json()
    
    async def register_server(self, server_name: str, base_url: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Register a new MCP server with the MITM server.
        
        Args:
            server_name: Name of the server
            base_url: Base URL of the MCP server
            tools: List of tool definitions
            
        Returns:
            Registration status
        """
        response = await self.client.post(
            f"{self.base_url}/register",
            json={
                "server_name": server_name,
                "base_url": base_url,
                "tools": tools
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
