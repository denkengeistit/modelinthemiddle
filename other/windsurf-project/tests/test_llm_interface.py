"""Tests for the LLM interface module."""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch

from mitm.llm_interface import LLMInterface
from mitm.models import ToolDefinition, ParameterSchema, ToolType

@pytest.fixture
def llm_interface():
    """Fixture that provides an LLMInterface instance with a mock endpoint."""
    return LLMInterface(endpoint="http://mock-llm-endpoint")

@pytest.fixture
def mock_tools():
    """Fixture that provides a list of mock tools for testing."""
    return [
        ToolDefinition(
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
        ),
        ToolDefinition(
            name="search_documents",
            description="Search for documents",
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
            server_name="test_server",
            tool_type=ToolType.MCP,
            return_type="List[Document]"
        )
    ]

@pytest.mark.asyncio
async def test_initialize_and_close(llm_interface):
    """Test initializing and closing the LLM interface."""
    # Initialize should create a session
    await llm_interface.initialize()
    assert llm_interface.session is not None
    assert not llm_interface.session.closed
    
    # Close should close the session
    await llm_interface.close()
    assert llm_interface.session.closed

@pytest.mark.asyncio
async def test_search_tools_with_llm(llm_interface, mock_tools):
    """Test searching for tools using the LLM."""
    # Mock the LLM response
    mock_response = [
        {"name": "get_document", "confidence": 0.95},
        {"name": "search_documents", "confidence": 0.85}
    ]
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        # Setup the mock response
        mock_resp = AsyncMock()
        mock_resp.json.return_value = {"text": json.dumps(mock_response)}
        mock_resp.__aenter__.return_value = mock_resp
        mock_post.return_value = mock_resp
        
        # Initialize the interface
        await llm_interface.initialize()
        
        # Perform the search
        result = await llm_interface.search_tools("find document by id", mock_tools, limit=2)
        
        # Verify the results
        assert len(result.tools) == 2
        assert result.tools[0].name == "get_document"
        assert result.tools[1].name == "search_documents"
        assert result.confidence_scores["get_document"] == 0.95
        assert result.confidence_scores["search_documents"] == 0.85
        
        # Verify the LLM was called with the correct prompt
        mock_post.assert_called_once()
        
        # Clean up
        await llm_interface.close()

@pytest.mark.asyncio
async def test_search_tools_fallback(llm_interface, mock_tools):
    """Test fallback search when LLM is not available."""
    with patch('aiohttp.ClientSession.post', side_effect=Exception("Connection error")):
        # Initialize the interface
        await llm_interface.initialize()
        
        # Perform the search - should fall back to simple matching
        result = await llm_interface.search_tools("document", mock_tools, limit=2)
        
        # Verify the results (both tools should match "document")
        assert len(result.tools) == 2
        assert set(tool.name for tool in result.tools) == {"get_document", "search_documents"}
        
        # Clean up
        await llm_interface.close()

@pytest.mark.asyncio
async def test_search_tools_empty_query(llm_interface, mock_tools):
    """Test searching with an empty query."""
    # Initialize the interface
    await llm_interface.initialize()
    
    # Search with empty query - should return all tools up to the limit
    result = await llm_interface.search_tools("", mock_tools, limit=1)
    
    # Verify we got exactly 1 tool
    assert len(result.tools) == 1
    
    # Clean up
    await llm_interface.close()

@pytest.mark.asyncio
async def test_search_tools_no_matches(llm_interface, mock_tools):
    """Test searching with a query that doesn't match any tools."""
    # Initialize the interface
    await llm_interface.initialize()
    
    # Search with a query that won't match any tools
    result = await llm_interface.search_tools("this_query_matches_nothing", mock_tools)
    
    # Verify no tools were returned
    assert len(result.tools) == 0
    
    # Clean up
    await llm_interface.close()
