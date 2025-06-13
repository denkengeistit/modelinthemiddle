# MCP Framework: Model in the Middle Architecture

An innovative multi-layered MCP (Model Context Protocol) framework that dramatically simplifies AI tool interaction through intelligent abstraction and automatic optimization.

## 🚀 The Game-Changing Concept

Instead of forcing LLMs to deal with complex tool schemas and requiring massive system prompts, this framework introduces a **"Model in the Middle"** architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  User/AI Client │ ── │  Simplified MCP  │ ── │   Model Bridge      │
│                 │    │  (3 tools only) │    │ (Smart Fine-tuned   │
│                 │    │                  │    │  Small Model)       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                            │
                                                            │
                                                ┌─────────────────────┐
                                                │   Complex MCP       │
                                                │   Server            │
                                                │ (Many complex tools)│
                                                └─────────────────────┘
```

## 🎯 Key Innovation

### The Problem
- Complex MCP servers have dozens of tools with intricate schemas
- LLMs need massive system prompts to understand tool usage
- Parameter optimization requires extensive trial and error
- No learning from past interactions

### The Solution
**Three simple tools for any complexity:**

1. **`what_tools`** - Discover available tools with intelligent categorization
2. **`how_tool`** - Get AI-optimized usage examples and best practices  
3. **`use_tool`** - Execute any tool with automatic parameter optimization

### The Magic
The **Model Bridge** is a fine-tuned small model (like Qwen2.5-0.5B) that:
- **Knows** all the complex tools intimately
- **Optimizes** parameters based on user intent and past successes
- **Learns** from every interaction to improve future calls
- **Suggests** related tools and next steps
- **Translates** between simple user requests and complex tool requirements

## 🛠 Architecture Components

### 1. Simplified MCP Server (User-Facing)
```typescript
// Only 3 tools - that's it!
interface SimplifiedTools {
  what_tools(category?: string, search?: string): ToolList;
  how_tool(toolName: string): UsageGuide;
  use_tool(toolName: string, parameters: any, context?: string): Result;
}
```

### 2. Model Bridge (The Intelligence Layer)
- **Fine-tuned small model** specifically trained on tool usage patterns
- **Caches** tool knowledge and usage examples
- **Optimizes** requests based on historical success patterns
- **Enhances** results with context and suggestions
- **Learns** continuously from user feedback

### 3. Complex MCP Server (Existing Infrastructure)
- Any existing MCP server (file operations, APIs, databases, etc.)
- No modifications needed - plug and play!

## 🚦 Getting Started

### Prerequisites
```bash
npm install @modelcontextprotocol/sdk zod zod-to-json-schema openai dotenv
npm install -D @types/node typescript ts-node
```

### Environment Setup
```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
```

### Basic Usage

1. **Start the framework:**
```bash
npm run build
npm run start:simplified
```

2. **Connect from Claude Desktop** (add to `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mcp-framework": {
      "command": "node",
      "args": ["path/to/dist/simplified-server/index.js"]
    }
  }
}
```

3. **Use the simple interface:**
```
User: "what_tools"
Framework: Lists all available tools with smart categorization

User: "how_tool echo"  
Framework: Shows examples, best practices, related tools

User: "use_tool echo {'message': 'Hello World'}"
Framework: Executes with optimization and provides suggestions
```

## 💡 Example Interaction Flow

```typescript
// Traditional MCP (Complex):
await mcpServer.callTool('complex_api_tool', {
  endpoint: '/users',
  method: 'GET', 
  headers: { 'Authorization': 'Bearer ...' },
  pagination: { page: 1, limit: 50 },
  filters: { active: true, role: 'admin' },
  format: 'json'
});

// MCP Framework (Simple):
await useTool('get_users', { role: 'admin' }, 'I need active admin users');
// Framework automatically:
// - Determines this maps to 'complex_api_tool'
// - Fills in auth headers from past successful calls
// - Sets appropriate pagination and format
// - Suggests related tools like 'get_user_permissions'
```

## 🧠 Model Training Strategy

The Model Bridge can be trained using:

1. **Existing tool documentation** and schemas
2. **Successful interaction patterns** from logs
3. **User feedback** (positive/negative/neutral)
4. **Tool usage analytics** and optimization data

Training data format:
```typescript
{
  userIntent: "Get user data for analysis",
  toolCall: { toolName: "fetch_users", parameters: {...} },
  result: { success: true, ... },
  feedback: "positive" // from user or success metrics
}
```

## 🔧 Configuration

### Model Provider Configuration
```typescript
const modelConfig: ModelBridgeConfig = {
  modelProvider: 'openai', // 'anthropic' | 'local'
  modelName: 'gpt-4o-mini',
  apiKey: process.env.OPENAI_API_KEY,
  temperature: 0.7,
  maxTokens: 1000
};
```

### Target MCP Server Configuration
```typescript
const mcpServerConfig: ComplexMCPServerConfig = {
  command: 'node',
  args: ['path/to/complex-mcp-server/index.js', 'stdio'],
  cwd: '/path/to/server',
  env: { /* environment variables */ }
};
```

## 🎨 Advanced Features

### Automatic Tool Discovery
- Scans connected MCP servers
- Categorizes tools by functionality
- Generates usage examples automatically
- Builds relationship maps between tools

### Intelligent Parameter Optimization
- Learns from successful tool calls
- Optimizes parameters based on user intent
- Handles authentication and common patterns automatically
- Suggests parameter improvements

### Contextual Learning
- Maintains conversation context
- Learns user preferences over time
- Adapts suggestions based on workflow patterns
- Provides proactive tool recommendations

## 🚀 Future Roadmap

### Phase 1: Core Framework ✅
- [x] Multi-layered MCP architecture
- [x] Simplified 3-tool interface
- [x] Model Bridge with caching
- [x] Integration with existing MCP servers

### Phase 2: Intelligence Enhancement
- [ ] Fine-tuned small model integration (Qwen2.5-0.5B)
- [ ] Advanced parameter optimization
- [ ] Feedback learning system
- [ ] Tool relationship discovery

### Phase 3: Automatic API Integration
- [ ] REST API to MCP server generation
- [ ] OpenAPI spec parsing and conversion
- [ ] Automatic authentication handling
- [ ] Rate limiting and error recovery

### Phase 4: Ecosystem
- [ ] Pre-trained models for common APIs
- [ ] Community tool knowledge sharing
- [ ] Visual tool workflow builder
- [ ] Performance analytics and optimization

## 🤝 Contributing

This framework represents a paradigm shift in how AI agents interact with tools. We're looking for contributors who share the vision of making complex tool interactions as simple as natural conversation.

### Areas for Contribution:
- **Model Training**: Help fine-tune small models for specific tool domains
- **API Integrations**: Build automatic converters for popular APIs
- **Optimization**: Improve parameter optimization algorithms
- **Documentation**: Create examples and tutorials
- **Testing**: Build comprehensive test suites

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

Built on the Model Context Protocol by Anthropic and inspired by the need to make AI tool interaction truly intelligent and effortless.

---

**This framework turns every AI agent into a power user, without the complexity.**