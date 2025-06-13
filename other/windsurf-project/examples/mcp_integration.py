"""
Example of integrating Model in the Middle with MCP servers.

This example shows how to:
1. Connect to a mock MCP server
2. Discover tools from the server
3. Process a search request from a user-facing LLM
4. Execute tools on the MCP server
"""
import asyncio
import json
import logging
from datetime import datetime
import time
import httpx

from mitm.tool_discovery import ToolDiscovery, MCPServer
from mitm.llm_interface import LLMInterface
from mitm.models import ToolDefinition, ParameterSchema, ToolType, ToolExecutionRequest
from mitm.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MCPConnector:
    """Connector for MCP servers that implements tool discovery and execution."""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
    
    async def discover_tools(self) -> dict:
        """
        Discover available tools from the MCP server.
        
        Returns:
            Dictionary mapping tool names to ToolDefinition objects
        """
        try:
            response = await self.client.get("/tools")
            response.raise_for_status()
            
            server_tools = response.json()
            tools = {}
            
            for tool_data in server_tools:
                # Convert the MCP server's tool schema to our internal format
                parameters = {}
                for param_name, param_data in tool_data.get("parameters", {}).items():
                    parameters[param_name] = ParameterSchema(
                        type=param_data.get("type", "string"),
                        description=param_data.get("description", ""),
                        required=param_data.get("required", True),
                        enum=param_data.get("enum")
                    )
                
                # Create the tool definition
                tool_name = f"{self.name}_{tool_data['name']}"
                tools[tool_name] = ToolDefinition(
                    name=tool_name,
                    description=tool_data.get("description", ""),
                    parameters=parameters,
                    server_name=self.name,
                    tool_type=ToolType.MCP,
                    return_type="Any"
                )
            
            logger.info(f"Discovered {len(tools)} tools from server {self.name}")
            return tools
            
        except Exception as e:
            logger.error(f"Error discovering tools from server {self.name}: {e}")
            return {}
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """
        Execute a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        try:
            # Extract the actual tool name (without server prefix)
            actual_tool_name = tool_name[len(self.name) + 1:]
            
            # Execute the tool on the MCP server
            response = await self.client.post(
                f"/execute/{actual_tool_name}",
                json={"parameters": parameters}
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} on server {self.name}: {e}")
            raise

async def main():
    # Initialize components
    tool_discovery = ToolDiscovery(settings)
    llm_interface = LLMInterface()
    
    # Start the LLM interface
    await llm_interface.initialize()
    
    try:
        # Create an MCP connector for our mock server
        mock_mcp_connector = MCPConnector(
            name="mockserver",
            base_url="http://localhost:8001"
        )
        
        # Register the MCP server
        logger.info("Registering mock MCP server...")
        await tool_discovery.register_server(
            "mockserver",
            "Mock MCP server for testing"
        )
        
        # Discover tools from the server
        logger.info("Discovering tools from mock MCP server...")
        mock_server = tool_discovery.servers["mockserver"]
        mock_server.tools = await mock_mcp_connector.discover_tools()
        mock_server.last_updated = datetime.utcnow()
        
        # Print discovered tools
        logger.info(f"Discovered {len(mock_server.tools)} tools from mock MCP server")
        for tool_name, tool in mock_server.tools.items():
            logger.info(f"  - {tool_name}: {tool.description}")
            
        # Simulate a search request from a user-facing LLM
        user_query = "Find documents tagged as important"
        logger.info(f"Processing user query: \"{user_query}\"")
        
        # Use the LLM to search for relevant tools
        start_time = time.time()
        search_result = await llm_interface.search_tools(
            user_query,
            tool_discovery.get_all_tools(),
            limit=3
        )
        search_time = time.time() - start_time
        
        # Print search results
        logger.info(f"Found {len(search_result.tools)} relevant tools in {search_time:.2f}s:")
        for tool in search_result.tools:
            confidence = search_result.confidence_scores.get(tool.name, 0)
            logger.info(f"  - {tool.name} (confidence: {confidence:.2f}): {tool.description}")
        
        # Execute the most relevant tool
        if search_result.tools:
            most_relevant_tool = search_result.tools[0]
            tool_name = most_relevant_tool.name
            
            # Extract the server name from the tool name
            server_name = most_relevant_tool.server_name
            
            logger.info(f"Executing tool: {tool_name}")
            
            # Prepare parameters based on the tool
            parameters = {}
            if "tag" in most_relevant_tool.parameters:
                parameters["tag"] = "important"
            elif "query" in most_relevant_tool.parameters:
                parameters["query"] = "important"
            
            logger.info(f"Parameters: {parameters}")
            
            # Execute the tool through the appropriate MCP connector
            if server_name == "mockserver":
                result = await mock_mcp_connector.execute_tool(tool_name, parameters)
                logger.info(f"Result: {json.dumps(result, indent=2)}")
            else:
                logger.error(f"Unknown server: {server_name}")
        
    finally:
        # Clean up
        await tool_discovery.stop()
        await llm_interface.close()
        await mock_mcp_connector.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
