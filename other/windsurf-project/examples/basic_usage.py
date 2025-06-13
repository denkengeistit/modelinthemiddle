"""
Basic usage example for Model in the Middle (MitM) framework.

This script demonstrates how to:
1. Initialize the MitM server
2. Register MCP servers
3. Search for tools
4. Execute tools
"""
import asyncio
import json
from datetime import datetime

from mitm import ToolDiscovery, LLMInterface
from mitm.models import ToolDefinition, ParameterSchema, ToolType

async def main():
    # Initialize components
    tool_discovery = ToolDiscovery()
    llm_interface = LLMInterface()
    
    # Start the LLM interface
    await llm_interface.initialize()
    
    try:
        # Register some example MCP servers
        print("Registering MCP servers...")
        await tool_discovery.register_server(
            "paperless-ngx",
            "Document management system with OCR and tagging"
        )
        
        # Wait for tool discovery to complete
        print("Discovering tools...")
        await asyncio.sleep(2)  # Simulate discovery time
        
        # List all available tools
        print("\nAvailable tools:")
        for tool in tool_discovery.get_all_tools():
            print(f"- {tool.name}: {tool.description}")
        
        # Search for tools using natural language
        print("\nSearching for document-related tools...")
        search_result = await llm_interface.search_tools(
            "find documents by tag",
            tool_discovery.get_all_tools(),
            limit=3
        )
        
        print("\nSearch results:")
        for tool in search_result.tools:
            confidence = search_result.confidence_scores.get(tool.name, 0)
            print(f"- {tool.name} (confidence: {confidence:.2f}): {tool.description}")
        
        # Execute a tool (simulated)
        if search_result.tools:
            tool_to_execute = search_result.tools[0]
            print(f"\nExecuting tool: {tool_to_execute.name}")
            
            # Simulate execution with some parameters
            params = {"tag": "important", "limit": 5}
            print(f"Parameters: {params}")
            
            # In a real implementation, this would call the actual MCP server
            print("Tool executed successfully!")
        
    finally:
        # Clean up
        await tool_discovery.stop()
        await llm_interface.close()

if __name__ == "__main__":
    asyncio.run(main())
