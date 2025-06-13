"""Tests for the FastAPI server."""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from mitm.server import app
from mitm.models import ToolDefinition, ParameterSchema, ToolType

@pytest.fixture
def client():
    """Fixture that provides a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_tool_discovery():
    """Fixture that mocks the tool discovery service."""
    with patch('mitm.server.tool_discovery') as mock:
        # Create a mock server with some tools
        mock_server = MagicMock()
        mock_server.name = "test_server"
        mock_server.description = "Test server"
        mock_server.tools = {
            "get_document": ToolDefinition(
                name="get_document",
                description="Get a document by ID",
                parameters={
                    "document_id": ParameterSchema(
                        type="string",
                        description="ID of the document to retrieve",
                        required=True
                    )
                },
                server_name="test_server",
                tool_type=ToolType.MCP,
                return_type="Document"
            )
        }
        mock.servers = {"test_server": mock_server}
        
        # Mock the get_all_tools method
        mock.get_all_tools.return_value = list(mock_server.tools.values())
        
        # Mock the get_tool method
        def get_tool(tool_name):
            return mock_server.tools.get(tool_name)
        mock.get_tool.side_effect = get_tool
        
        # Mock the search_tools method
        mock.search_tools.return_value = [mock_server.tools["get_document"]]
        
        yield mock

@pytest.fixture
def mock_llm_interface():
    """Fixture that mocks the LLM interface."""
    with patch('mitm.server.llm_interface') as mock:
        # Mock the search_tools method
        mock.search_tools.return_value = MagicMock(
            tools=[],
            confidence_scores={}
        )
        yield mock

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

def test_list_servers(client, mock_tool_discovery):
    """Test the list servers endpoint."""
    response = client.get("/servers")
    assert response.status_code == 200
    servers = response.json()
    assert len(servers) == 1
    assert servers[0]["name"] == "test_server"

def test_list_tools(client, mock_tool_discovery):
    """Test the list tools endpoint."""
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) == 1
    assert tools[0]["name"] == "get_document"

def test_search_tools(client, mock_tool_discovery, mock_llm_interface):
    """Test the search tools endpoint."""
    response = client.get("/tools/search?q=document")
    assert response.status_code == 200
    result = response.json()
    assert "tools" in result
    assert "confidence_scores" in result
    assert len(result["tools"]) == 1
    assert result["tools"][0]["name"] == "get_document"

def test_get_tool(client, mock_tool_discovery):
    """Test getting a specific tool."""
    response = client.get("/tools/get_document")
    assert response.status_code == 200
    tool = response.json()
    assert tool["name"] == "get_document"
    assert "parameters" in tool

def test_get_nonexistent_tool(client, mock_tool_discovery):
    """Test getting a tool that doesn't exist."""
    response = client.get("/tools/nonexistent_tool")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_execute_tool(client, mock_tool_discovery):
    """Test executing a tool."""
    # Mock the tool execution
    mock_tool = mock_tool_discovery.servers["test_server"].tools["get_document"]
    
    # Make the request
    response = client.post(
        "/execute",
        json={
            "tool_name": "get_document",
            "parameters": {"document_id": "123"}
        }
    )
    
    # Verify the response
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "message" in result["result"]
    assert result["result"]["parameters"]["document_id"] == "123"

def test_execute_nonexistent_tool(client, mock_tool_discovery):
    """Test executing a tool that doesn't exist."""
    response = client.post(
        "/execute",
        json={
            "tool_name": "nonexistent_tool",
            "parameters": {}
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
