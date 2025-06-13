"""
Model in the Middle (MitM) - A minimalist framework for MCP server interfaces using local LLMs.

This package provides a framework for creating lightweight interfaces between LLMs and MCP servers,
enabling efficient tool discovery and usage without requiring fine-tuning or large system prompts.
"""

__version__ = "0.1.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

# Import key components for easier access
from .server import app
from .tool_discovery import ToolDiscovery
from .llm_interface import LLMInterface
from .models import (
    ToolDefinition,
    ToolSearchResult,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ServerInfo
)
from .config import settings

# Define public API
__all__ = [
    'app',
    'ToolDiscovery',
    'LLMInterface',
    'ToolDefinition',
    'ToolSearchResult',
    'ToolExecutionRequest',
    'ToolExecutionResponse',
    'ServerInfo',
    'settings'
]
