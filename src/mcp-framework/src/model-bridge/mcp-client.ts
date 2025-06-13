import { spawn, ChildProcess } from 'child_process';
import * as process from 'process';
import { 
  MCPTool, 
  MCPToolResult, 
  ComplexMCPServerConfig,
  ToolDiscoveryResult 
} from '../types/index.js';

export class MCPClient {
  private process: ChildProcess | null = null;
  private messageId = 0;
  private pendingRequests = new Map<number, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
  }>();
  private connected = false;

  constructor(private config: ComplexMCPServerConfig) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.process = spawn(this.config.command, this.config.args, {
        cwd: this.config.cwd,
        env: { ...process.env, ...this.config.env },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      if (!this.process.stdin || !this.process.stdout) {
        reject(new Error('Failed to create MCP server process'));
        return;
      }

      this.process.stdout.on('data', (data: any) => {
        const lines = data.toString().split('\n').filter((line: string) => line.trim());
        for (const line of lines) {
          try {
            const message = JSON.parse(line);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse MCP message:', line, error);
          }
        }
      });

      this.process.stderr?.on('data', (data: any) => {
        console.error('MCP Server stderr:', data.toString());
      });

      this.process.on('error', (error: Error) => {
        console.error('MCP Server process error:', error);
        if (!this.connected) {
          reject(error);
        }
      });

      this.process.on('exit', (code: number | null) => {
        console.log('MCP Server process exited with code:', code);
        this.connected = false;
      });

      // Initialize the connection
      this.sendRequest({
        jsonrpc: '2.0',
        id: this.getNextId(),
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          clientInfo: {
            name: 'mcp-framework',
            version: '0.1.0'
          }
        }
      }).then(() => {
        this.connected = true;
        resolve();
      }).catch(reject);
    });
  }

  async disconnect(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
    this.connected = false;
  }

  async listTools(): Promise<ToolDiscoveryResult> {
    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: this.getNextId(),
      method: 'tools/list'
    });

    const tools: MCPTool[] = response.tools.map((tool: any) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema
    }));

    return {
      tools,
      totalCount: tools.length,
      categories: this.extractCategories(tools)
    };
  }

  async callTool(name: string, arguments_: any): Promise<MCPToolResult> {
    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: this.getNextId(),
      method: 'tools/call',
      params: {
        name,
        arguments: arguments_
      }
    });

    return {
      content: response.content || [],
      isError: response.isError || false
    };
  }

  private getNextId(): number {
    return ++this.messageId;
  }

  private sendRequest(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.process?.stdin) {
        reject(new Error('MCP server not connected'));
        return;
      }

      const id = request.id;
      this.pendingRequests.set(id, { resolve, reject });

      const message = JSON.stringify(request) + '\n';
      this.process.stdin.write(message);

      // Set timeout for requests
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request ${id} timed out`));
        }
      }, 30000); // 30 second timeout
    });
  }

  private handleMessage(message: any): void {
    if (message.id && this.pendingRequests.has(message.id)) {
      const request = this.pendingRequests.get(message.id)!;
      this.pendingRequests.delete(message.id);

      if (message.error) {
        request.reject(new Error(message.error.message || 'Unknown error'));
      } else {
        request.resolve(message.result);
      }
    }
  }

  private extractCategories(tools: MCPTool[]): string[] {
    const categories = new Set<string>();
    
    for (const tool of tools) {
      // Simple categorization based on tool name patterns
      const name = tool.name.toLowerCase();
      if (name.includes('file') || name.includes('read') || name.includes('write')) {
        categories.add('File Operations');
      } else if (name.includes('git') || name.includes('repo')) {
        categories.add('Version Control');
      } else if (name.includes('search') || name.includes('find')) {
        categories.add('Search');
      } else if (name.includes('fetch') || name.includes('http') || name.includes('api')) {
        categories.add('Network');
      } else if (name.includes('memory') || name.includes('store')) {
        categories.add('Data Storage');
      } else {
        categories.add('Utility');
      }
    }

    return Array.from(categories);
  }
}