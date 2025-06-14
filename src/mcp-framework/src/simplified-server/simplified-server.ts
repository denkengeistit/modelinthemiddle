import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  ToolSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import { 
  SimplifiedMCPServerInterface,
  ToolDiscoveryResult,
  ToolUsageInfo,
  ToolExecutionResult,
  ModelBridgeConfig,
  ComplexMCPServerConfig
} from '../types/index.js';
import { ModelBridge } from '../model-bridge/model-bridge.js';

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

// Input schemas for the three simplified tools
const WhatToolsSchema = z.object({
  category: z.string().optional().describe("Filter tools by category (optional)"),
  search: z.string().optional().describe("Search term to filter tools (optional)")
});

const HowToolSchema = z.object({
  toolName: z.string().describe("The name of the tool to get usage information for")
});

const UseToolSchema = z.object({
  toolName: z.string().describe("The name of the tool to execute"),
  parameters: z.any().describe("Parameters to pass to the tool"),
  context: z.string().optional().describe("Additional context about what you're trying to achieve")
});

enum SimplifiedToolName {
  WHAT_TOOLS = "what_tools",
  HOW_TOOL = "how_tool",
  USE_TOOL = "use_tool"
}

export class SimplifiedMCPServer implements SimplifiedMCPServerInterface {
  private server: Server;
  private modelBridge: ModelBridge;

  constructor(
    private modelConfig: ModelBridgeConfig,
    private mcpServerConfig: ComplexMCPServerConfig
  ) {
    this.server = new Server(
      {
        name: "mcp-framework/simplified-server",
        version: "0.1.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.modelBridge = new ModelBridge(this.modelConfig, this.mcpServerConfig);
    this.setupHandlers();
  }

  async initialize(): Promise<void> {
    await this.modelBridge.initialize();
  }

  async whatTools(): Promise<ToolDiscoveryResult> {
    return await this.modelBridge.discoverTools();
  }

  async howTool(toolName: string): Promise<ToolUsageInfo> {
    return await this.modelBridge.getToolUsage(toolName);
  }

  async useTool(toolName: string, parameters: any, context?: string): Promise<ToolExecutionResult> {
    const request = {
      toolName,
      parameters,
      userIntent: context
    };

    // Only add context if it's defined
    if (context !== undefined) {
      (request as any).context = context;
    }

    const result = await this.modelBridge.executeToolCall(request);

    // Record this interaction for training
    const trainingRequest = {
      toolName,
      parameters
    };
    if (context !== undefined) {
      (trainingRequest as any).context = context;
    }

    await this.modelBridge.trainOnInteraction(
      context || `Execute ${toolName}`,
      trainingRequest,
      result
    );

    return result;
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools: Tool[] = [
        {
          name: SimplifiedToolName.WHAT_TOOLS,
          description: "Discover what tools are available. Returns a list of all tools you can use, optionally filtered by category or search term.",
          inputSchema: zodToJsonSchema(WhatToolsSchema) as ToolInput,
        },
        {
          name: SimplifiedToolName.HOW_TOOL,
          description: "Get detailed usage information for a specific tool. Returns examples, best practices, and parameter details.",
          inputSchema: zodToJsonSchema(HowToolSchema) as ToolInput,
        },
        {
          name: SimplifiedToolName.USE_TOOL,
          description: "Execute a tool with the given parameters. The system will intelligently optimize your request and provide helpful feedback.",
          inputSchema: zodToJsonSchema(UseToolSchema) as ToolInput,
        },
      ];

      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request: any) => {
      const { name, arguments: args } = request.params;

      if (name === SimplifiedToolName.WHAT_TOOLS) {
        const validatedArgs = WhatToolsSchema.parse(args);
        const result = await this.whatTools();
        
        // Apply filters if provided
        let filteredTools = result.tools;
        
        if (validatedArgs.category) {
          filteredTools = filteredTools.filter(_tool => 
            result.categories?.includes(validatedArgs.category!)
          );
        }
        
        if (validatedArgs.search) {
          const searchTerm = validatedArgs.search.toLowerCase();
          filteredTools = filteredTools.filter(tool =>
            tool.name.toLowerCase().includes(searchTerm) ||
            tool.description.toLowerCase().includes(searchTerm)
          );
        }

        const response = {
          tools: filteredTools,
          totalCount: filteredTools.length,
          categories: result.categories,
          summary: `Found ${filteredTools.length} tools` + 
                  (validatedArgs.category ? ` in category "${validatedArgs.category}"` : '') +
                  (validatedArgs.search ? ` matching "${validatedArgs.search}"` : '')
        };

        return {
          content: [
            {
              type: "text",
              text: `## Available Tools\n\n${response.summary}\n\n### Categories:\n${result.categories?.join(', ') || 'None'}\n\n### Tools:\n${filteredTools.map(tool => `**${tool.name}**: ${tool.description}`).join('\n')}`
            }
          ],
        };
      }

      if (name === SimplifiedToolName.HOW_TOOL) {
        const validatedArgs = HowToolSchema.parse(args);
        const usageInfo = await this.howTool(validatedArgs.toolName);

        const examplesText = usageInfo.examples?.length 
          ? `\n\n### Examples:\n${usageInfo.examples.map((ex, i) => 
              `**Example ${i + 1}**: ${ex.description}\n\`\`\`json\n${JSON.stringify(ex.input, null, 2)}\n\`\`\``
            ).join('\n\n')}`
          : '';

        const relatedText = usageInfo.relatedTools?.length
          ? `\n\n### Related Tools:\n${usageInfo.relatedTools.join(', ')}`
          : '';

        return {
          content: [
            {
              type: "text",
              text: `## How to use: ${usageInfo.name}\n\n**Category**: ${usageInfo.category}\n\n**Description**: ${usageInfo.description}\n\n### Input Schema:\n\`\`\`json\n${JSON.stringify(usageInfo.inputSchema, null, 2)}\n\`\`\`${examplesText}${relatedText}`
            }
          ],
        };
      }

      if (name === SimplifiedToolName.USE_TOOL) {
        const validatedArgs = UseToolSchema.parse(args);
        const result = await this.useTool(
          validatedArgs.toolName, 
          validatedArgs.parameters,
          validatedArgs.context
        );

        if (!result.success) {
          return {
            content: [
              {
                type: "text",
                text: `❌ **Tool execution failed**: ${result.error}\n\n### Suggestions:\n${result.suggestions?.map(s => `• ${s}`).join('\n') || 'None'}`
              }
            ],
            isError: true,
          };
        }

        // Format the successful result
        let resultText = `✅ **Successfully executed**: ${validatedArgs.toolName}\n\n`;
        
        if (result.result?.content) {
          resultText += '### Result:\n';
          for (const content of result.result.content) {
            if (content.type === 'text' && content.text) {
              resultText += content.text + '\n';
            } else if (content.type === 'image') {
              resultText += '[Image result included]\n';
            }
          }
        }

        if (result.suggestions?.length) {
          resultText += `\n### Suggestions:\n${result.suggestions.map(s => `• ${s}`).join('\n')}`;
        }

        return {
          content: [
            {
              type: "text",
              text: resultText
            }
          ],
        };
      }

      throw new Error(`Unknown tool: ${name}`);
    });
  }

  getServer(): Server {
    return this.server;
  }

  async shutdown(): Promise<void> {
    await this.modelBridge.shutdown();
  }
}