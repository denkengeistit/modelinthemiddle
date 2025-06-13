# Model in the Middle (MITM)

A lightweight framework that acts as an intermediary between LLMs and MCP servers, enabling efficient tool discovery and usage without requiring fine-tuning or massive system prompts.

## Features

- Dynamic tool discovery and registration from multiple MCP servers
- Automatic 1:1 API mapping for MCP server tools
- Simple RESTful interface for tool search and execution
- Support for multiple MCP servers with automatic routing
- Minimal system prompt requirements
- Command-line interface for easy interaction

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd model-in-the-middle
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

1. Start the MITM server:
```bash
mitm serve
```

2. Register an MCP server (example with a test server):
```bash
# Create a tools.json file with your MCP server's tool definitions
cat > tools.json << 'EOL'
[
  {
    "name": "example_tool",
    "description": "An example tool that does something useful",
    "parameters": {
      "param1": {"type": "string", "description": "First parameter"},
      "param2": {"type": "integer", "description": "Second parameter"}
    }
  }
]
EOL

# Register the server
mitm register-server http://localhost:8000 example_server http://example-mcp-server:8000 tools.json
```

3. List available tools:
```bash
mitm list-tools
```

4. Call a tool:
```bash
mitm call-tool http://localhost:8000 example_tool '{"param1": "value", "param2": 42}'
```

## Architecture

- `model_in_the_middle/`
  - `__init__.py` - Package initialization
  - `server.py` - FastAPI server implementation
  - `client.py` - Client library for interacting with MITM servers
  - `cli.py` - Command-line interface
- `requirements.txt` - Python dependencies
- `README.md` - This file

## API Reference

### Server Endpoints

- `GET /tools` - List all available tools
  - Query parameters:
    - `query` (optional): Filter tools by name or description

- `POST /call` - Execute a tool
  - Request body:
    ```json
    {
      "tool_name": "tool_name",
      "parameters": {}
    }
    ```

- `POST /register` - Register a new MCP server
  - Request body:
    ```json
    {
      "server_name": "server1",
      "base_url": "http://mcp-server:8000",
      "tools": [
        {
          "name": "tool1",
          "description": "Tool description",
          "parameters": {}
        }
      ]
    }
    ```

## License

MIT
