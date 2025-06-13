import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .models import ToolDefinition, ParameterSchema, ToolType

logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    name: str
    description: str = ""
    tools: Dict[str, ToolDefinition] = field(default_factory=dict)
    last_updated: Optional[datetime] = None

class ToolDiscovery:
    def __init__(self, settings):
        self.settings = settings
        self.servers: Dict[str, MCPServer] = {}
        self._discovery_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    async def start(self):
        """Start the periodic tool discovery task."""
        self._stop_event.clear()
        self._discovery_task = asyncio.create_task(self._periodic_discovery())
    
    async def stop(self):
        """Stop the periodic tool discovery."""
        if self._discovery_task:
            self._stop_event.set()
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass
    
    async def _periodic_discovery(self):
        """Periodically discover tools from all registered MCP servers."""
        while not self._stop_event.is_set():
            try:
                await self.discover_all_servers()
            except Exception as e:
                logger.error(f"Error during tool discovery: {e}")
            
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.settings.TOOL_DISCOVERY_INTERVAL
                )
            except asyncio.TimeoutError:
                pass
    
    async def register_server(self, server_name: str, description: str = "") -> bool:
        """Register a new MCP server."""
        if server_name in self.servers:
            logger.warning(f"Server {server_name} is already registered")
            return False
        
        self.servers[server_name] = MCPServer(name=server_name, description=description)
        await self.discover_server_tools(server_name)
        return True
    
    async def unregister_server(self, server_name: str) -> bool:
        """Unregister an MCP server."""
        if server_name not in self.servers:
            return False
        
        del self.servers[server_name]
        return True
    
    async def discover_all_servers(self) -> Dict[str, bool]:
        """Discover tools from all registered servers."""
        results = {}
        for server_name in list(self.servers.keys()):
            try:
                success = await self.discover_server_tools(server_name)
                results[server_name] = success
            except Exception as e:
                logger.error(f"Error discovering tools for server {server_name}: {e}")
                results[server_name] = False
        return results
    
    async def discover_server_tools(self, server_name: str) -> bool:
        """Discover tools from a specific MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} is not registered")
        
        # TODO: Implement actual MCP server tool discovery
        # This is a placeholder that simulates discovering tools
        # In a real implementation, this would query the MCP server's API
        
        # Simulate discovering some tools
        tools = {}
        
        # Example tool 1
        tool1_name = f"{server_name}_get_document"
        tools[tool1_name] = ToolDefinition(
            name=tool1_name,
            description=f"Get a document from {server_name}",
            parameters={
                "document_id": ParameterSchema(
                    type="string",
                    description="ID of the document to retrieve",
                    required=True
                )
            },
            server_name=server_name,
            tool_type=ToolType.MCP,
            return_type="Document"
        )
        
        # Example tool 2
        tool2_name = f"{server_name}_search_documents"
        tools[tool2_name] = ToolDefinition(
            name=tool2_name,
            description=f"Search documents in {server_name}",
            parameters={
                "query": ParameterSchema(
                    type="string",
                    description="Search query",
                    required=True
                ),
                "limit": ParameterSchema(
                    type="integer",
                    description="Maximum number of results to return",
                    required=False,
                    default=10
                )
            },
            server_name=server_name,
            tool_type=ToolType.MCP,
            return_type="List[Document]"
        )
        
        # Update the server with discovered tools
        self.servers[server_name].tools = tools
        self.servers[server_name].last_updated = datetime.utcnow()
        
        logger.info(f"Discovered {len(tools)} tools from server {server_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a specific tool by name."""
        for server in self.servers.values():
            if tool_name in server.tools:
                return server.tools[tool_name]
        return None
    
    def search_tools(self, query: str, limit: int = 10) -> List[ToolDefinition]:
        """Search for tools matching the query."""
        # TODO: Implement semantic search using the local LLM
        # For now, just do a simple case-insensitive substring match
        query = query.lower()
        results = []
        
        for server in self.servers.values():
            for tool in server.tools.values():
                if (query in tool.name.lower() or 
                    query in tool.description.lower() or
                    any(query in param.description.lower() 
                        for param in tool.parameters.values())):
                    results.append(tool)
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all available tools from all servers."""
        return [
            tool
            for server in self.servers.values()
            for tool in server.tools.values()
        ]
