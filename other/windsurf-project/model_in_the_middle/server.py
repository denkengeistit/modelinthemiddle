"""FastAPI server implementation for Model in the Middle."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import json
from loguru import logger

class ToolDefinition(BaseModel):
    """Definition of an available tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    server: str

class ToolCall(BaseModel):
    """Request to execute a specific tool."""
    tool_name: str
    parameters: Dict[str, Any]

class MITMServer:
    """Model in the Middle server implementation."""
    
    def __init__(self):
        self.app = FastAPI(
            title="Model in the Middle",
            description="Lightweight framework for LLM-MCP server integration",
            version="0.1.0"
        )
        self.tools: Dict[str, ToolDefinition] = {}
        self.servers: Dict[str, str] = {}  # server_name -> base_url
        
        # Register routes
        self.app.get("/tools")(self.list_tools)
        self.app.post("/call")(self.call_tool)
        self.app.post("/register")(self.register_server)
    
    async def list_tools(self, query: str = "") -> List[ToolDefinition]:
        """List all available tools, optionally filtered by query."""
        if not query:
            return list(self.tools.values())
        
        query = query.lower()
        return [
            tool for tool in self.tools.values()
            if query in tool.name.lower() or query in tool.description.lower()
        ]
    
    async def call_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call by forwarding it to the appropriate MCP server."""
        if tool_call.tool_name not in self.tools:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        tool = self.tools[tool_call.tool_name]
        server_url = self.servers.get(tool.server)
        
        if not server_url:
            raise HTTPException(status_code=500, detail=f"Server {tool.server} not found")
        
        # Forward the request to the appropriate MCP server
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{server_url}/{tool.name}",
                    json=tool_call.parameters,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error calling tool {tool.name}: {str(e)}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error from {tool.server}: {e.response.text}"
                )
    
    async def register_server(self, server_name: str, base_url: str, tools: List[Dict[str, Any]]):
        """Register a new MCP server and its tools."""
        self.servers[server_name] = base_url.rstrip('/')
        
        for tool_def in tools:
            tool = ToolDefinition(
                name=tool_def['name'],
                description=tool_def.get('description', ''),
                parameters=tool_def.get('parameters', {}),
                server=server_name
            )
            self.tools[tool.name] = tool
            
        return {"status": "success", "tools_registered": len(tools)}

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MITM server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
