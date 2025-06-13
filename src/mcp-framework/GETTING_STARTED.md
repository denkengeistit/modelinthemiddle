# MCP Framework: Quick Start Guide

## 🚀 What You've Built

You now have a revolutionary **Model in the Middle** architecture that transforms any complex MCP server into a simple 3-tool interface:

- **`what_tools`** - Discover available tools with AI categorization
- **`how_tool`** - Get intelligent usage examples and best practices  
- **`use_tool`** - Execute any tool with automatic optimization

## 📁 Project Structure

```
src/mcp-framework/
├── src/
│   ├── types/index.ts              # Core interfaces and types
│   ├── model-bridge/
│   │   ├── mcp-client.ts           # Connects to existing MCP servers
│   │   └── model-bridge.ts         # The intelligent layer
│   └── simplified-server/
│       ├── simplified-server.ts    # 3-tool MCP server
│       └── index.ts                # Entry point with stdio transport
├── example/
│   └── test-framework.ts           # Demo script
├── package.json                    # Dependencies and scripts
├── tsconfig.json                   # TypeScript configuration
├── README.md                       # Full documentation
├── .env.example                    # Environment configuration
└── GETTING_STARTED.md              # This file
```

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
cd src/mcp-framework
npm install
```

### 2. Install Required Types
```bash
npm install -D @types/node
```

### 3. Set Environment Variables
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 4. Build the Project
```bash
npm run build
```

### 5. Test with Existing MCP Server
```bash
# First, make sure you have the "everything" MCP server built
cd ../everything
npm run build

# Then test the framework
cd ../mcp-framework
npm run start:simplified
```

## 🧪 Testing the Framework

### Option 1: With Claude Desktop

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-framework": {
      "command": "node",
      "args": ["/path/to/src/mcp-framework/dist/simplified-server/index.js"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

Then use these simple commands in Claude:
```
- what_tools
- how_tool echo  
- use_tool echo {"message": "Hello Framework!"}
```

### Option 2: Run Demo Script

```bash
cd src/mcp-framework
npx ts-node example/test-framework.ts
```

## 🎯 Key Benefits Demonstrated

### Before (Traditional MCP):
```javascript
// Complex schema understanding required
await mcpServer.callTool('complex_tool', {
  parameter1: "value1",
  parameter2: { nested: "complex" },
  parameter3: ["array", "of", "values"],
  metadata: { required: true, format: "specific" }
});
```

### After (MCP Framework):
```javascript
// Simple, intelligent interface
await useTool('complex_tool', { goal: 'my objective' }, 'help me achieve this');
// Framework handles all complexity automatically!
```

## 🔄 What Happens Under the Hood

1. **`what_tools`** calls → Model Bridge discovers and categorizes all available tools
2. **`how_tool`** calls → AI generates contextual examples and best practices
3. **`use_tool`** calls → Model optimizes parameters, executes, learns from results

The **Model Bridge** is the magic:
- Connects to any existing MCP server
- Learns successful interaction patterns
- Optimizes parameters automatically
- Provides intelligent suggestions
- Maintains conversation context

## 🚀 Next Steps

### Phase 1: Test with Real MCP Servers
- Connect to filesystem, git, or API servers
- Test the 3-tool simplification
- Validate the abstraction works

### Phase 2: Enhance Intelligence
- Integrate actual fine-tuned models (Qwen2.5-0.5B)
- Implement real parameter optimization
- Add feedback learning system

### Phase 3: Auto-Generate from APIs
- Build REST API → MCP server converter
- Parse OpenAPI specifications
- Handle authentication automatically

## 🐛 Troubleshooting

### "Cannot find module" errors
```bash
npm install -D @types/node
npm install @modelcontextprotocol/sdk zod zod-to-json-schema
```

### MCP Server Connection Issues
- Ensure target MCP server is built and working
- Check file paths in configuration
- Verify environment variables are set

### Model Provider Errors
- Verify API keys are set in environment
- Check network connectivity
- Ensure sufficient API credits

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Framework starts without errors
- ✅ `what_tools` returns categorized tool list
- ✅ `how_tool` provides intelligent documentation
- ✅ `use_tool` executes and provides suggestions
- ✅ All interactions feel "magical" compared to raw MCP

## 📞 Support

This framework represents a fundamental shift in AI tool interaction. If you're having issues:

1. Check the console logs for specific errors
2. Verify all dependencies are installed
3. Ensure target MCP server is functional
4. Test with the provided demo script first

**Remember**: You've built something revolutionary - a framework that turns complex tool ecosystems into simple, intelligent conversations! 🚀