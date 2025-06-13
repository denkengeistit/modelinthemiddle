"""Tests for the tool discovery module."""
import pytest
import asyncio
from datetime import datetime, timedelta

from mitm.tool_discovery import ToolDiscovery, MCPServer
from mitm.models import ToolDefinition, ParameterSchema, ToolType

@pytest.fixture
async def tool_discovery():
    """Fixture that provides a ToolDiscovery instance."""
    discovery = ToolDiscovery()
    yield discovery
    await discovery.stop()

@pytest.mark.asyncio
async def test_register_server(tool_discovery):
    """Test registering a new MCP server."""
    server_name = "test_server"
    description = "Test server"
    
    # Register a new server
    result = await tool_discovery.register_server(server_name, description)
    assert result is True
    assert server_name in tool_discovery.servers
    assert tool_discovery.servers[server_name].description == description
    
    # Try to register the same server again
    result = await tool_discovery.register_server(server_name)
    assert result is False  # Should return False for duplicate

@pytest.mark.asyncio
async def test_unregister_server(tool_discovery):
    """Test unregistering an MCP server."""
    server_name = "test_server"
    await tool_discovery.register_server(server_name)
    
    # Unregister the server
    result = await tool_discovery.unregister_server(server_name)
    assert result is True
    assert server_name not in tool_discovery.servers
    
    # Try to unregister a non-existent server
    result = await tool_discovery.unregister_server("non_existent")
    assert result is False

@pytest.mark.asyncio
async def test_discover_server_tools(tool_discovery):
    """Test discovering tools from a server."""
    server_name = "test_server"
    await tool_discovery.register_server(server_name)
    
    # Discover tools
    result = await tool_discovery.discover_server_tools(server_name)
    assert result is True
    
    # Verify tools were discovered
    server = tool_discovery.servers[server_name]
    assert len(server.tools) > 0
    assert server.last_updated is not None
    
    # Check that tool definitions are valid
    for tool in server.tools.values():
        assert isinstance(tool, ToolDefinition)
        assert tool.name
        assert tool.description
        assert tool.server_name == server_name

@pytest.mark.asyncio
async def test_get_tool(tool_discovery):
    """Test getting a specific tool by name."""
    server_name = "test_server"
    await tool_discovery.register_server(server_name)
    await tool_discovery.discover_server_tools(server_name)
    
    # Get a tool that should exist
    server = tool_discovery.servers[server_name]
    tool_name = next(iter(server.tools.keys()))
    tool = tool_discovery.get_tool(tool_name)
    
    assert tool is not None
    assert tool.name == tool_name
    
    # Get a non-existent tool
    assert tool_discovery.get_tool("non_existent_tool") is None

@pytest.mark.asyncio
async def test_search_tools(tool_discovery):
    """Test searching for tools."""
    server_name = "test_server"
    await tool_discovery.register_server(server_name)
    await tool_discovery.discover_server_tools(server_name)
    
    # Search for tools (should match at least one tool)
    results = tool_discovery.search_tools("document")
    assert len(results) > 0
    
    # Search with a non-matching query
    results = tool_discovery.search_tools("nonexistent_query_123")
    assert len(results) == 0

@pytest.mark.asyncio
async def test_periodic_discovery(tool_discovery, monkeypatch):
    """Test periodic tool discovery."""
    # Patch the discovery interval to a small value for testing
    monkeypatch.setattr(tool_discovery.settings, "TOOL_DISCOVERY_INTERVAL", 0.1)
    
    server_name = "test_server"
    await tool_discovery.register_server(server_name)
    
    # Start periodic discovery
    await tool_discovery.start()
    
    # Wait for at least one discovery cycle
    await asyncio.sleep(0.2)
    
    # Verify tools were discovered
    server = tool_discovery.servers[server_name]
    assert len(server.tools) > 0
    assert server.last_updated is not None
    
    # Stop the discovery task
    await tool_discovery.stop()
    
    # Verify the task was stopped
    assert tool_discovery._discovery_task.done()
