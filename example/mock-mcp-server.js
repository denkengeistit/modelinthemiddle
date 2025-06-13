#!/usr/bin/env node

// Simple mock MCP server for testing the framework
// This simulates a complex MCP server with multiple tools

const tools = [
  {
    name: "echo",
    description: "Echoes back the input message",
    inputSchema: {
      type: "object",
      properties: {
        message: {
          type: "string",
          description: "Message to echo back"
        }
      },
      required: ["message"]
    }
  },
  {
    name: "add_numbers", 
    description: "Adds two numbers together",
    inputSchema: {
      type: "object",
      properties: {
        a: {
          type: "number",
          description: "First number"
        },
        b: {
          type: "number", 
          description: "Second number"
        }
      },
      required: ["a", "b"]
    }
  },
  {
    name: "get_weather",
    description: "Gets weather information for a location", 
    inputSchema: {
      type: "object",
      properties: {
        location: {
          type: "string",
          description: "Location to get weather for"
        },
        units: {
          type: "string",
          enum: ["celsius", "fahrenheit"],
          description: "Temperature units"
        }
      },
      required: ["location"]
    }
  }
];

let messageId = 0;

function sendMessage(message) {
  console.log(JSON.stringify(message));
}

function handleMessage(message) {
  if (message.method === 'initialize') {
    sendMessage({
      jsonrpc: '2.0',
      id: message.id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {}
        },
        serverInfo: {
          name: 'mock-mcp-server',
          version: '1.0.0'
        }
      }
    });
  } else if (message.method === 'tools/list') {
    sendMessage({
      jsonrpc: '2.0', 
      id: message.id,
      result: {
        tools: tools
      }
    });
  } else if (message.method === 'tools/call') {
    const { name, arguments: args } = message.params;
    
    let result;
    if (name === 'echo') {
      result = {
        content: [
          {
            type: 'text',
            text: `Echo: ${args.message}`
          }
        ]
      };
    } else if (name === 'add_numbers') {
      const sum = args.a + args.b;
      result = {
        content: [
          {
            type: 'text', 
            text: `The sum of ${args.a} and ${args.b} is ${sum}`
          }
        ]
      };
    } else if (name === 'get_weather') {
      result = {
        content: [
          {
            type: 'text',
            text: `Weather in ${args.location}: 22°C, sunny (simulated data)`
          }
        ]
      };
    } else {
      sendMessage({
        jsonrpc: '2.0',
        id: message.id,
        error: {
          code: -32601,
          message: `Unknown tool: ${name}`
        }
      });
      return;
    }
    
    sendMessage({
      jsonrpc: '2.0',
      id: message.id, 
      result: result
    });
  } else {
    sendMessage({
      jsonrpc: '2.0',
      id: message.id,
      error: {
        code: -32601,
        message: `Unknown method: ${message.method}`
      }
    });
  }
}

// Handle input from stdin
process.stdin.setEncoding('utf8');
let buffer = '';

process.stdin.on('data', (chunk) => {
  buffer += chunk;
  const lines = buffer.split('\n');
  buffer = lines.pop(); // Keep incomplete line in buffer
  
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        handleMessage(message);
      } catch (error) {
        console.error('Failed to parse message:', line, error);
      }
    }
  }
});

process.stdin.on('end', () => {
  process.exit(0);
});

console.error('Mock MCP Server started - providing echo, add_numbers, and get_weather tools');