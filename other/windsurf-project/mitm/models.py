from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class ToolType(str, Enum):
    MCP = "mcp"
    NATIVE = "native"

class ParameterSchema(BaseModel):
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ParameterSchema]
    server_name: str
    tool_type: ToolType
    return_type: str = "Any"

class ToolSearchResult(BaseModel):
    tools: List[ToolDefinition]
    confidence_scores: Dict[str, float]

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float

class ServerInfo(BaseModel):
    name: str
    description: str
    version: str
    tools_count: int
