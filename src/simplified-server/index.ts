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
  apiKey: process.env.OPENAI_API_KEY,
  temperature: 0.7,
  maxTokens: 1000
};

// 🎯 DEMO: Connect to the REAL paperless-mcp server to show actual complexity!
const mcpServerConfig: ComplexMCPServerConfig = {
  command: 'node',
  args: [
    'src/index.js',
    'http://kubestore.cow-capella.ts.net:8080', 
    '4f8059be791d7b8396f8cc839c8046fceec68ac1'                    
  ],
  cwd: '../../paperless-mcp', // Path to real paperless-mcp directory
  env: {
    ...process.env
  }
};

async function main() {
  console.error('🚀 MCP FRAMEWORK DEMONSTRATION: Real Paperless-MCP Transformation!');
  console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.error('');
  console.error('🔴 TRADITIONAL MCP: The paperless-mcp server you found "too complicated"');
  console.error('   📋 16+ complex tools with intricate schemas:');
  console.error('   • bulk_edit_documents (14 methods: merge, split, rotate, set_permissions...)');
  console.error('   • post_document (8 parameters: file, metadata, tags, correspondents...)');  
  console.error('   • list/get/search/download documents with pagination & filtering');
  console.error('   • tag management (create, update, delete, bulk operations)');
  console.error('   • correspondent management with matching algorithms');
  console.error('   • document type management with complex schemas');
  console.error('   ❌ Result: "Too complicated to properly use"');
  console.error('');
  console.error('🟢 MCP FRAMEWORK: Revolutionary 3-tool simplification');
  console.error('   ✨ what_tools - "Show me what I can do"');
  console.error('   ✨ how_tool   - "How do I use bulk_edit_documents?"');
  console.error('   ✨ use_tool   - "Merge documents 1,2,3 into one file"');
  console.error('   ✅ Result: Natural conversation with ANY complexity!');
  console.error('');
  console.error('🎬 Starting demonstration...');
  console.error('');
  
  try {
    const server = new SimplifiedMCPServer(modelConfig, mcpServerConfig);
    await server.initialize();
    
    console.error('✅ Model Bridge connected to REAL paperless-mcp successfully!');
    console.error('🎯 Complex server with 16+ tools → Simple 3-tool interface');
    console.error('🧠 AI intelligence now handles all the complexity behind the scenes');
    console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.error('');
    console.error('🎮 Ready for demo! Try these commands:');
    console.error('   what_tools');
    console.error('   how_tool bulk_edit_documents'); 
    console.error('   use_tool search_documents {"query": "invoice"}');
    console.error('');
    
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
    console.error("");
    console.error("📝 Note: This demo shows tool discovery even with dummy credentials.");
    console.error("    The key is seeing how 16+ complex tools become 3 simple ones!");
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("❌ Unexpected error:", error);
  process.exit(1);
});