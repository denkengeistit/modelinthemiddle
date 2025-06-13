"""Command-line interface for Model in the Middle."""

import typer
import asyncio
from typing import Optional, List
from .client import MITMClient
import json

app = typer.Typer()

@app.command()
def serve(
    host: str = "0.0.0.0",
    port: int = 8000,
    debug: bool = False
):
    """Start the MITM server."""
    from .server import MITMServer
    
    server = MITMServer()
    print(f"Starting Model in the Middle server on {host}:{port}")
    server.run(host=host, port=port)

@app.command()
async def list_tools(
    server_url: str = "http://localhost:8000",
    query: Optional[str] = None
):
    """List available tools from an MITM server."""
    async with MITMClient(server_url) as client:
        tools = await client.list_tools(query or "")
        print(json.dumps(tools, indent=2))

@app.command()
async def call_tool(
    server_url: str,
    tool_name: str,
    params_json: str = "{}",
):
    """Call a tool on an MITM server.
    
    Example:
        mitm call-tool http://localhost:8000 my_tool '{"param1": "value1"}'
    """
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters: {e}")
        return
    
    async with MITMClient(server_url) as client:
        try:
            result = await client.call_tool(tool_name, **params)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error calling tool: {e}")

@app.command()
async def register_server(
    mitm_url: str,
    server_name: str,
    server_url: str,
    tools_file: str
):
    """Register a new MCP server with an MITM server.
    
    tools_file should be a JSON file containing a list of tool definitions.
    """
    try:
        with open(tools_file) as f:
            tools = json.load(f)
    except Exception as e:
        print(f"Error loading tools file: {e}")
        return
    
    async with MITMClient(mitm_url) as client:
        try:
            result = await client.register_server(server_name, server_url, tools)
            print(f"Successfully registered {result['tools_registered']} tools from {server_name}")
        except Exception as e:
            print(f"Error registering server: {e}")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()
