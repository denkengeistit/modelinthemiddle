"""
Mock MCP Server implementation for testing the Model in the Middle framework.

This simple FastAPI server simulates an MCP server with a few example tools.
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mock MCP Server",
    description="A mock MCP server for testing Model in the Middle",
    version="0.1.0"
)

# Data models
class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ToolParameter]

class ToolExecutionRequest(BaseModel):
    parameters: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    result: Any

# In-memory "database" of documents
documents = {
    "doc1": {"id": "doc1", "title": "Sample Document 1", "content": "This is a sample document with some content.", "tags": ["sample", "test"]},
    "doc2": {"id": "doc2", "title": "Sample Document 2", "content": "This is another sample document with different content.", "tags": ["sample", "important"]},
    "doc3": {"id": "doc3", "title": "Important Document", "content": "This document contains important information.", "tags": ["important"]},
}

# Available tools
tools = {
    "get_document": ToolDefinition(
        name="get_document",
        description="Get a document by ID",
        parameters={
            "document_id": ToolParameter(
                type="string",
                description="ID of the document to retrieve",
                required=True
            )
        }
    ),
    "search_documents": ToolDefinition(
        name="search_documents",
        description="Search for documents matching a query",
        parameters={
            "query": ToolParameter(
                type="string",
                description="Search query",
                required=True
            ),
            "limit": ToolParameter(
                type="integer",
                description="Maximum number of results to return",
                required=False
            )
        }
    ),
    "list_documents_by_tag": ToolDefinition(
        name="list_documents_by_tag",
        description="List all documents with a specific tag",
        parameters={
            "tag": ToolParameter(
                type="string", 
                description="Tag to filter by",
                required=True
            )
        }
    ),
    "create_document": ToolDefinition(
        name="create_document",
        description="Create a new document",
        parameters={
            "title": ToolParameter(
                type="string",
                description="Document title",
                required=True
            ),
            "content": ToolParameter(
                type="string",
                description="Document content",
                required=True
            ),
            "tags": ToolParameter(
                type="array",
                description="List of tags",
                required=False
            )
        }
    )
}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "Mock MCP Server",
        "description": "A mock MCP server for testing Model in the Middle",
        "version": "0.1.0"
    }

@app.get("/tools")
async def list_tools():
    """List all available tools."""
    return list(tools.values())

@app.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get details of a specific tool."""
    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return tools[tool_name]

@app.post("/execute/{tool_name}")
async def execute_tool(tool_name: str, request: ToolExecutionRequest):
    """Execute a specific tool."""
    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    # Validate parameters against the tool's schema
    tool = tools[tool_name]
    for param_name, param_schema in tool.parameters.items():
        if param_schema.required and param_name not in request.parameters:
            raise HTTPException(
                status_code=400,
                detail=f"Required parameter '{param_name}' missing"
            )
    
    # Execute the appropriate tool
    if tool_name == "get_document":
        return await execute_get_document(request.parameters)
    elif tool_name == "search_documents":
        return await execute_search_documents(request.parameters)
    elif tool_name == "list_documents_by_tag":
        return await execute_list_documents_by_tag(request.parameters)
    elif tool_name == "create_document":
        return await execute_create_document(request.parameters)
    else:
        raise HTTPException(
            status_code=501,
            detail=f"Tool '{tool_name}' not implemented"
        )

# Tool implementations
async def execute_get_document(parameters: Dict[str, Any]):
    """Implementation of the get_document tool."""
    document_id = parameters["document_id"]
    if document_id not in documents:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{document_id}' not found"
        )
    
    return {"result": documents[document_id]}

async def execute_search_documents(parameters: Dict[str, Any]):
    """Implementation of the search_documents tool."""
    query = parameters["query"].lower()
    limit = parameters.get("limit", 10)
    
    results = []
    for doc in documents.values():
        if query in doc["title"].lower() or query in doc["content"].lower():
            results.append(doc)
            if len(results) >= limit:
                break
    
    return {"result": results}

async def execute_list_documents_by_tag(parameters: Dict[str, Any]):
    """Implementation of the list_documents_by_tag tool."""
    tag = parameters["tag"].lower()
    
    results = []
    for doc in documents.values():
        if tag in [t.lower() for t in doc.get("tags", [])]:
            results.append(doc)
    
    return {"result": results}

async def execute_create_document(parameters: Dict[str, Any]):
    """Implementation of the create_document tool."""
    title = parameters["title"]
    content = parameters["content"]
    tags = parameters.get("tags", [])
    
    # Generate a new document ID
    doc_id = f"doc{len(documents) + 1}"
    
    # Create the new document
    documents[doc_id] = {
        "id": doc_id,
        "title": title,
        "content": content,
        "tags": tags
    }
    
    return {"result": documents[doc_id]}

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "mock_mcp_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
