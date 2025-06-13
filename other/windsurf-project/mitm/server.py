import logging
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .models import (
    ToolDefinition,
    ToolSearchResult,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ServerInfo
)
from .tool_discovery import ToolDiscovery
from .llm_interface import LLMInterface
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Model in the Middle (MitM)",
    description="A minimalist framework for MCP server interfaces using local LLMs",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
tool_discovery = ToolDiscovery(settings)
llm_interface = LLMInterface()

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    logger.info("Starting Model in the Middle (MitM) server...")
    
    # Initialize LLM interface
    await llm_interface.initialize()
    
    # Start tool discovery
    await tool_discovery.start()
    
    # Register some example MCP servers
    await tool_discovery.register_server(
        "paperless-ngx",
        "Document management system with OCR and tagging"
    )
    
    logger.info("MitM server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down MitM server...")
    
    # Stop tool discovery
    await tool_discovery.stop()
    
    # Close LLM interface
    await llm_interface.close()
    
    logger.info("MitM server shutdown complete")

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information about the service."""
    return {
        "name": "Model in the Middle (MitM)",
        "description": "A minimalist framework for MCP server interfaces using local LLMs",
        "version": "0.1.0",
        "documentation": "/docs"
    }

@app.get("/servers", response_model=List[ServerInfo])
async def list_servers():
    """List all registered MCP servers."""
    return [
        {
            "name": server.name,
            "description": server.description,
            "version": "1.0.0",  # TODO: Get actual version from server
            "tools_count": len(server.tools)
        }
        for server in tool_discovery.servers.values()
    ]

@app.get("/tools", response_model=List[ToolDefinition])
async def list_tools(limit: int = 100, offset: int = 0):
    """List all available tools."""
    all_tools = tool_discovery.get_all_tools()
    return all_tools[offset:offset + limit]

@app.get("/tools/search", response_model=ToolSearchResult)
async def search_tools(
    q: str,
    limit: int = 5,
    min_confidence: float = 0.1
):
    """
    Search for tools using natural language.
    
    Args:
        q: Search query
        limit: Maximum number of results to return
        min_confidence: Minimum confidence score (0-1) for including results
    """
    if not q:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )
    
    all_tools = tool_discovery.get_all_tools()
    
    # Use the LLM to find the most relevant tools
    search_result = await llm_interface.search_tools(q, all_tools, limit)
    
    # Filter by minimum confidence
    filtered_tools = []
    filtered_scores = {}
    
    for tool in search_result.tools:
        confidence = search_result.confidence_scores.get(tool.name, 0)
        if confidence >= min_confidence:
            filtered_tools.append(tool)
            filtered_scores[tool.name] = confidence
    
    return ToolSearchResult(
        tools=filtered_tools,
        confidence_scores=filtered_scores
    )

@app.get("/tools/{tool_name}", response_model=ToolDefinition)
async def get_tool(tool_name: str):
    """Get details about a specific tool."""
    tool = tool_discovery.get_tool(tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )
    return tool

@app.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """
    Execute a tool with the given parameters.
    
    This is a placeholder implementation. In a real implementation, this would
    forward the request to the appropriate MCP server.
    """
    tool = tool_discovery.get_tool(request.tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{request.tool_name}' not found"
        )
    
    # TODO: Validate parameters against the tool's schema
    # For now, just log the execution
    logger.info(
        f"Executing tool: {tool.name} with parameters: {request.parameters}"
    )
    
    # In a real implementation, this would forward the request to the MCP server
    # and return the result
    return ToolExecutionResponse(
        success=True,
        result={
            "message": f"Successfully executed {tool.name}",
            "parameters": request.parameters,
            "server": tool.server_name
        },
        execution_time=0.1  # Simulated execution time
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "mitm.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
