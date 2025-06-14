#!/usr/bin/env node

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SimplifiedMCPServer } from "./simplified-server.js";
import { ModelBridgeConfig, ComplexMCPServerConfig } from "../types/index.js";
import * as dotenv from 'dotenv';

dotenv.config();

// Configuration - these could be loaded from environment variables or config files
const modelConfig: ModelBridgeConfig = {
  modelProvider: 'openai',
  modelName: 'gpt-4o-mini',
  apiKey: process.env.OPENAI_API_KEY || '',
  temperature: 0.7,
  maxTokens: 1000
};

// Example: Connect to the "everything" MCP server for testing
const mcpServerConfig: ComplexMCPServerConfig = {
  command: 'node',
  args: ['../everything/index.js', 'stdio'],
  cwd: process.cwd(),
  env: Object.fromEntries(
    Object.entries(process.env).filter(([_, v]) => v !== undefined)
  ) as Record<string, string>
};

async function main() {
  console.error('Starting MCP Framework - Simplified Server...');
  
  try {
    const server = new SimplifiedMCPServer(modelConfig, mcpServerConfig);
    await server.initialize();
    
    console.error('✅ Model Bridge initialized successfully');
    console.error('🚀 Simplified MCP Server ready with 3 tools: what_tools, how_tool, use_tool');
    
    const transport = new StdioServerTransport();
    await server.getServer().connect(transport);

    // Cleanup on exit
    process.on("SIGINT", async () => {
      console.error('💤 Shutting down MCP Framework...');
      await server.shutdown();
      await server.getServer().close();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      console.error('💤 Shutting down MCP Framework...');
      await server.shutdown();
      await server.getServer().close();
      process.exit(0);
    });

  } catch (error) {
    console.error("❌ Failed to start MCP Framework:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("❌ Unexpected error:", error);
  process.exit(1);
});