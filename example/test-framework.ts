#!/usr/bin/env node

/**
 * MCP Framework Demo
 * 
 * This script demonstrates the revolutionary simplicity of the MCP Framework
 * compared to traditional complex MCP server interactions.
 */

import { SimplifiedMCPServer } from '../src/simplified-server/simplified-server.js';
import { ModelBridgeConfig, ComplexMCPServerConfig } from '../src/types/index.js';

// Mock configurations for demo
const modelConfig: ModelBridgeConfig = {
  modelProvider: 'openai',
  modelName: 'gpt-4o-mini',
  apiKey: 'demo-key', // In real usage, use environment variable
  temperature: 0.7,
  maxTokens: 1000
};

const mcpServerConfig: ComplexMCPServerConfig = {
  command: 'node',
  args: ['../everything/index.js', 'stdio'],
  cwd: process.cwd()
};

async function demonstrateFramework() {
  console.log('🚀 MCP Framework Demo: Model in the Middle Architecture\n');
  
  try {
    // Initialize the framework
    console.log('📡 Initializing MCP Framework...');
    const server = new SimplifiedMCPServer(modelConfig, mcpServerConfig);
    await server.initialize();
    console.log('✅ Framework initialized successfully!\n');

    // Demo 1: Discover tools with what_tools
    console.log('🔍 Demo 1: Tool Discovery with "what_tools"');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const toolDiscovery = await server.whatTools();
    console.log(`📋 Found ${toolDiscovery.totalCount} tools across ${toolDiscovery.categories?.length || 0} categories`);
    console.log(`📂 Categories: ${toolDiscovery.categories?.join(', ')}`);
    console.log('🛠  Sample tools:');
    toolDiscovery.tools.slice(0, 5).forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description}`);
    });
    console.log('');

    // Demo 2: Get tool usage with how_tool
    console.log('📖 Demo 2: Smart Tool Documentation with "how_tool"');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    if (toolDiscovery.tools.length > 0) {
      const sampleTool = toolDiscovery.tools[0];
      console.log(`📚 Getting usage info for: ${sampleTool.name}`);
      
      const usageInfo = await server.howTool(sampleTool.name);
      console.log(`📝 Description: ${usageInfo.description}`);
      console.log(`🏷  Category: ${usageInfo.category}`);
      console.log(`🔗 Related tools: ${usageInfo.relatedTools?.join(', ') || 'None'}`);
      
      if (usageInfo.examples && usageInfo.examples.length > 0) {
        console.log('💡 Example usage:');
        console.log(`   ${JSON.stringify(usageInfo.examples[0].input, null, 2)}`);
      }
    }
    console.log('');

    // Demo 3: Execute tool with use_tool
    console.log('⚡ Demo 3: Intelligent Tool Execution with "use_tool"');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    // Find a simple tool to demonstrate
    const echoTool = toolDiscovery.tools.find(t => t.name.toLowerCase().includes('echo'));
    
    if (echoTool) {
      console.log(`🎯 Executing: ${echoTool.name}`);
      console.log('💭 User intent: "I want to test the system with a simple message"');
      
      const result = await server.useTool(
        echoTool.name,
        { message: 'Hello from MCP Framework!' },
        'I want to test the system with a simple message'
      );
      
      if (result.success) {
        console.log('✅ Execution successful!');
        console.log('📤 Result:', result.result?.content?.[0]?.text || 'No text content');
        
        if (result.suggestions && result.suggestions.length > 0) {
          console.log('💡 AI Suggestions:');
          result.suggestions.forEach(suggestion => {
            console.log(`   • ${suggestion}`);
          });
        }
      } else {
        console.log('❌ Execution failed:', result.error);
        if (result.suggestions) {
          console.log('🔧 Suggestions:');
          result.suggestions.forEach(suggestion => {
            console.log(`   • ${suggestion}`);
          });
        }
      }
    }
    console.log('');

    // Demo 4: Show the power of simplification
    console.log('🎭 Demo 4: Traditional vs Framework Comparison');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    console.log('🔴 Traditional MCP interaction:');
    console.log(`   • ${toolDiscovery.totalCount} different tools to understand`);
    console.log('   • Complex schemas for each tool');
    console.log('   • No parameter optimization');
    console.log('   • No learning from past interactions');
    console.log('   • Requires massive system prompts');
    console.log('');
    
    console.log('🟢 MCP Framework interaction:');
    console.log('   • Just 3 simple tools: what_tools, how_tool, use_tool');
    console.log('   • AI-optimized parameters automatically');
    console.log('   • Learns from every interaction');
    console.log('   • Intelligent suggestions and guidance');
    console.log('   • No complex system prompts needed');
    console.log('');

    // Cleanup
    await server.shutdown();
    console.log('💤 Framework shutdown complete');
    
    console.log('\n🎉 Demo completed! The MCP Framework transforms complex tool interactions');
    console.log('   into simple, intelligent conversations. This is the future of AI tool use!');
    
  } catch (error) {
    console.error('❌ Demo failed:', error);
    console.log('\n📝 Note: This demo requires a running MCP server to connect to.');
    console.log('   In a real deployment, the framework would connect to actual MCP servers.');
    
    // Show conceptual output even if connection fails
    console.log('\n🎬 Conceptual Demo Output:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('what_tools() →');
    console.log('  📋 Found 8 tools across 4 categories');
    console.log('  📂 Categories: File Operations, Version Control, Search, Utility');
    console.log('  🛠  Tools: echo, add, longRunningOperation, printEnv, ...');
    console.log('');
    console.log('how_tool("echo") →');
    console.log('  📚 Echo tool - Echoes back the input message');
    console.log('  💡 Example: {"message": "Hello World"}');
    console.log('  🔗 Related: add, printEnv');
    console.log('');
    console.log('use_tool("echo", {"message": "AI is amazing!"}) →');
    console.log('  ✅ Echo: AI is amazing!');
    console.log('  💡 Suggestion: Try "add" for mathematical operations');
  }
}

// Run the demo
demonstrateFramework().catch(console.error);