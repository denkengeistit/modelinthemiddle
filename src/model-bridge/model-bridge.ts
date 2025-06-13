import { 
  ModelBridgeInterface,
  ModelBridgeConfig,
  ComplexMCPServerConfig,
  ToolDiscoveryResult,
  ToolUsageInfo,
  ToolExecutionRequest,
  ToolExecutionResult,
  MCPTool
} from '../types/index.js';
import { MCPClient } from './mcp-client.js';

interface TrainingData {
  userIntent: string;
  toolCall: ToolExecutionRequest;
  result: ToolExecutionResult;
  feedback: 'positive' | 'negative' | 'neutral';
  timestamp: Date;
}

interface ModelProvider {
  generateResponse(prompt: string, context?: string): Promise<string>;
}

export class ModelBridge implements ModelBridgeInterface {
  private mcpClient: MCPClient;
  private modelProvider: ModelProvider;
  private trainingData: TrainingData[] = [];
  private toolCache = new Map<string, MCPTool>();
  private usageExamples = new Map<string, ToolUsageInfo>();

  constructor(
    _modelConfig: ModelBridgeConfig,
    _mcpServerConfig: ComplexMCPServerConfig
  ) {
    this.mcpClient = new MCPClient(_mcpServerConfig);
    this.modelProvider = this.createModelProvider();
  }

  async initialize(): Promise<void> {
    await this.mcpClient.connect();
    await this.cacheAvailableTools();
    await this.generateToolUsageExamples();
  }

  async discoverTools(): Promise<ToolDiscoveryResult> {
    if (this.toolCache.size === 0) {
      await this.cacheAvailableTools();
    }

    const tools = Array.from(this.toolCache.values());
    return {
      tools,
      totalCount: tools.length,
      categories: this.categorizeTools(tools)
    };
  }

  async getToolUsage(toolName: string): Promise<ToolUsageInfo> {
    const cachedUsage = this.usageExamples.get(toolName);
    if (cachedUsage) {
      return cachedUsage;
    }

    const tool = this.toolCache.get(toolName);
    if (!tool) {
      throw new Error(`Tool '${toolName}' not found`);
    }

    // Generate intelligent usage information using the model
    const usageInfo = await this.generateToolUsageInfo(tool);
    this.usageExamples.set(toolName, usageInfo);
    return usageInfo;
  }

  async executeToolCall(request: ToolExecutionRequest): Promise<ToolExecutionResult> {
    try {
      // Use the model to interpret the user's intent and generate appropriate parameters
      const optimizedRequest = await this.optimizeToolRequest(request);
      
      // Execute the tool call via the MCP client
      const result = await this.mcpClient.callTool(
        optimizedRequest.toolName, 
        optimizedRequest.parameters
      );

      // Post-process the result using the model for better user experience
      const enhancedResult = await this.enhanceToolResult(result, request);

      const executionResult: ToolExecutionResult = {
        success: !result.isError,
        result: enhancedResult,
        suggestions: await this.generateSuggestions(request, enhancedResult)
      };

      return executionResult;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        suggestions: await this.generateErrorSuggestions(request, error)
      };
    }
  }

  async trainOnInteraction(
    userIntent: string,
    toolCall: ToolExecutionRequest,
    result: ToolExecutionResult,
    userFeedback: 'positive' | 'negative' | 'neutral' = 'neutral'
  ): Promise<void> {
    const trainingEntry: TrainingData = {
      userIntent,
      toolCall,
      result,
      feedback: userFeedback,
      timestamp: new Date()
    };

    this.trainingData.push(trainingEntry);

    // Keep only the last 1000 interactions for memory efficiency
    if (this.trainingData.length > 1000) {
      this.trainingData = this.trainingData.slice(-1000);
    }

    // In a real implementation, this would update the fine-tuned model
    console.log(`Training data recorded: ${userFeedback} feedback for ${toolCall.toolName}`);
  }

  private async cacheAvailableTools(): Promise<void> {
    const toolDiscovery = await this.mcpClient.listTools();
    this.toolCache.clear();
    
    for (const tool of toolDiscovery.tools) {
      this.toolCache.set(tool.name, tool);
    }
  }

  private async generateToolUsageExamples(): Promise<void> {
    for (const [toolName, tool] of this.toolCache) {
      if (!this.usageExamples.has(toolName)) {
        const usageInfo = await this.generateToolUsageInfo(tool);
        this.usageExamples.set(toolName, usageInfo);
      }
    }
  }

  private async generateToolUsageInfo(tool: MCPTool): Promise<ToolUsageInfo> {
    const prompt = `
    Generate comprehensive usage information for this MCP tool:
    
    Tool Name: ${tool.name}
    Description: ${tool.description}
    Input Schema: ${JSON.stringify(tool.inputSchema, null, 2)}
    
    Please provide:
    1. Detailed usage examples with realistic inputs and expected outputs
    2. Common use cases and scenarios
    3. Related tools that work well together
    4. Best practices and tips
    
    Format as JSON with examples array, relatedTools array, and category.
    `;

    const response = await this.modelProvider.generateResponse(prompt);
    
    try {
      const parsed = JSON.parse(response);
      return {
        name: tool.name,
        description: tool.description,
        inputSchema: tool.inputSchema,
        examples: parsed.examples || [],
        relatedTools: parsed.relatedTools || [],
        category: parsed.category || 'Utility'
      };
    } catch {
      // Fallback if model response is not valid JSON
      return {
        name: tool.name,
        description: tool.description,
        inputSchema: tool.inputSchema,
        examples: [],
        relatedTools: [],
        category: 'Utility'
      };
    }
  }

  private async optimizeToolRequest(request: ToolExecutionRequest): Promise<ToolExecutionRequest> {
    const tool = this.toolCache.get(request.toolName);
    if (!tool) {
      return request;
    }

    // Use historical training data to optimize the request
    const relevantTraining = this.trainingData
      .filter(data => data.toolCall.toolName === request.toolName)
      .filter(data => data.feedback === 'positive')
      .slice(-5); // Last 5 successful interactions

    const prompt = `
    Optimize this tool call based on successful past interactions:
    
    Tool: ${request.toolName}
    User Intent: ${request.userIntent || 'Not specified'}
    Current Parameters: ${JSON.stringify(request.parameters, null, 2)}
    Tool Schema: ${JSON.stringify(tool.inputSchema, null, 2)}
    
    Successful past interactions:
    ${relevantTraining.map(t => JSON.stringify(t.toolCall.parameters)).join('\n')}
    
    Return optimized parameters as JSON that best fulfills the user intent.
    `;

    try {
      const response = await this.modelProvider.generateResponse(prompt);
      const optimizedParams = JSON.parse(response);
      
      return {
        ...request,
        parameters: optimizedParams
      };
    } catch {
      // Return original request if optimization fails
      return request;
    }
  }

  private async enhanceToolResult(result: any, _originalRequest: ToolExecutionRequest): Promise<any> {
    // For now, return result as-is, but in a real implementation this would:
    // 1. Format the output for better readability
    // 2. Add context and explanations
    // 3. Highlight important information
    // 4. Suggest follow-up actions
    return result;
  }

  private async generateSuggestions(request: ToolExecutionRequest, _result: any): Promise<string[]> {
    const relatedTools = Array.from(this.toolCache.values())
      .filter(tool => tool.name !== request.toolName)
      .slice(0, 3);

    return relatedTools.map(tool => 
      `Consider using '${tool.name}' for ${tool.description}`
    );
  }

  private async generateErrorSuggestions(request: ToolExecutionRequest, _error: any): Promise<string[]> {
    return [
      `Check if the parameters match the expected schema for '${request.toolName}'`,
      'Verify that all required fields are provided',
      'Try using the how_tool command to get usage examples'
    ];
  }

  private categorizeTools(tools: MCPTool[]): string[] {
    const categories = new Set<string>();
    
    for (const tool of tools) {
      const name = tool.name.toLowerCase();
      const desc = tool.description.toLowerCase();
      
      if (name.includes('file') || desc.includes('file')) {
        categories.add('File Operations');
      } else if (name.includes('git') || desc.includes('git')) {
        categories.add('Version Control');
      } else if (name.includes('search') || desc.includes('search')) {
        categories.add('Search');
      } else if (name.includes('fetch') || name.includes('http') || desc.includes('web')) {
        categories.add('Network');
      } else if (name.includes('memory') || desc.includes('memory')) {
        categories.add('Data Storage');
      } else {
        categories.add('Utility');
      }
    }

    return Array.from(categories);
  }

  private createModelProvider(): ModelProvider {
    // For now, return a mock implementation
    // In a real implementation, this would connect to OpenAI, Anthropic, or a local model
    return {
      async generateResponse(prompt: string, _context?: string): Promise<string> {
        // Mock implementation - in reality this would call the configured model
        console.log('Model prompt:', prompt);
        return JSON.stringify({
          examples: [],
          relatedTools: [],
          category: 'Utility'
        });
      }
    };
  }

  async shutdown(): Promise<void> {
    await this.mcpClient.disconnect();
  }
}