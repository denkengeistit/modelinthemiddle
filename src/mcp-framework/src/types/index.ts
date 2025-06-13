export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

export interface MCPToolResult {
  content: Array<{
    type: string;
    text?: string;
    data?: string;
    mimeType?: string;
  }>;
  isError?: boolean;
}

export interface ModelBridgeConfig {
  modelProvider: 'openai' | 'anthropic' | 'local';
  modelName: string;
  apiKey?: string;
  baseUrl?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface ComplexMCPServerConfig {
  command: string;
  args: string[];
  cwd?: string;
  env?: Record<string, string>;
}

export interface ToolDiscoveryResult {
  tools: MCPTool[];
  totalCount: number;
  categories?: string[];
}

export interface ToolUsageInfo {
  name: string;
  description: string;
  inputSchema: any;
  examples?: Array<{
    input: any;
    output: any;
    description: string;
  }>;
  relatedTools?: string[];
  category?: string;
}

export interface ToolExecutionRequest {
  toolName: string;
  parameters: any;
  context?: string | undefined;
  userIntent?: string | undefined;
}

export interface ToolExecutionResult {
  success: boolean;
  result?: MCPToolResult;
  error?: string;
  suggestions?: string[];
}

export interface ModelBridgeInterface {
  discoverTools(): Promise<ToolDiscoveryResult>;
  getToolUsage(toolName: string): Promise<ToolUsageInfo>;
  executeToolCall(request: ToolExecutionRequest): Promise<ToolExecutionResult>;
  trainOnInteraction(
    userIntent: string, 
    toolCall: ToolExecutionRequest, 
    result: ToolExecutionResult,
    userFeedback?: 'positive' | 'negative' | 'neutral'
  ): Promise<void>;
}

export interface SimplifiedMCPServerInterface {
  whatTools(): Promise<ToolDiscoveryResult>;
  howTool(toolName: string): Promise<ToolUsageInfo>;
  useTool(toolName: string, parameters: any, context?: string): Promise<ToolExecutionResult>;
}