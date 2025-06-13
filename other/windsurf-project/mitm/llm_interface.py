import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any, Tuple

from .models import ToolDefinition, ToolSearchResult
from .config import settings

logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or settings.LOCAL_LLM_ENDPOINT
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search_tools(
        self,
        query: str,
        tools: List[ToolDefinition],
        limit: int = 5
    ) -> ToolSearchResult:
        """
        Use the local LLM to find the most relevant tools for the given query.
        
        Args:
            query: The user's query
            tools: List of available tools
            limit: Maximum number of tools to return
            
        Returns:
            ToolSearchResult containing the most relevant tools and confidence scores
        """
        if not tools:
            return ToolSearchResult(tools=[], confidence_scores={})
        
        # If we have a small number of tools, just return them all
        if len(tools) <= limit:
            return ToolSearchResult(
                tools=tools,
                confidence_scores={tool.name: 1.0 for tool in tools}
            )
        
        # Prepare the prompt for the LLM
        tools_json = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    name: {"type": param.type, "description": param.description}
                    for name, param in tool.parameters.items()
                },
                "return_type": tool.return_type,
                "server_name": tool.server_name
            }
            for tool in tools
        ]
        
        prompt = self._create_search_prompt(query, tools_json, limit)
        
        try:
            # Call the local LLM
            response = await self._call_llm(prompt)
            
            # Parse the response to get the ranked tool names
            ranked_tools = self._parse_llm_response(response)
            
            # Map back to ToolDefinition objects
            tool_map = {tool.name: tool for tool in tools}
            result_tools = []
            confidence_scores = {}
            
            for i, (tool_name, score) in enumerate(ranked_tools):
                if tool_name in tool_map:
                    result_tools.append(tool_map[tool_name])
                    confidence_scores[tool_name] = score
                    
                    if len(result_tools) >= limit:
                        break
            
            # If we didn't get enough tools, add some random ones
            if len(result_tools) < limit:
                remaining = limit - len(result_tools)
                for tool in tools:
                    if tool.name not in confidence_scores:
                        result_tools.append(tool)
                        confidence_scores[tool.name] = 0.5  # Low confidence
                        remaining -= 1
                        if remaining <= 0:
                            break
            
            return ToolSearchResult(
                tools=result_tools,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            logger.error(f"Error searching tools with LLM: {e}")
            # Fallback to simple substring matching if LLM fails
            return self._fallback_search(query, tools, limit)
    
    def _create_search_prompt(self, query: str, tools: List[Dict], limit: int) -> str:
        """Create a prompt for the LLM to rank tools based on the query."""
        tools_json = json.dumps(tools, indent=2)
        
        return f"""You are a tool discovery assistant. Your task is to find the most relevant tools for a user's query from a list of available tools.

Available tools (in JSON format):
{tools_json}

User query: "{query}"

Please return a JSON array of the top {limit} most relevant tools, ordered by relevance. For each tool, include the tool name and a confidence score between 0 and 1.

Example format:
[
  {{"name": "tool_name_1", "confidence": 0.95}},
  {{"name": "tool_name_2", "confidence": 0.85}}
]

Your response (JSON array only, no other text):"""

    def _parse_llm_response(self, response: str) -> List[Tuple[str, float]]:
        """Parse the LLM response to extract tool names and confidence scores."""
        try:
            # Try to parse the response as JSON
            data = json.loads(response.strip())
            if not isinstance(data, list):
                raise ValueError("Expected a JSON array")
                
            # Extract tool names and confidence scores
            return [
                (item["name"], float(item["confidence"]))
                for item in data
                if isinstance(item, dict) and "name" in item and "confidence" in item
            ]
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return []
    
    async def _call_llm(self, prompt: str) -> str:
        """Make an API call to the local LLM."""
        if not self.session:
            await self.initialize()
        
        payload = {
            "prompt": prompt,
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE,
        }
        
        try:
            async with self.session.post(self.endpoint, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("text", "").strip()
        except Exception as e:
            logger.error(f"Error calling LLM endpoint: {e}")
            raise
    
    def _fallback_search(
        self,
        query: str,
        tools: List[ToolDefinition],
        limit: int
    ) -> ToolSearchResult:
        """Fallback search implementation when LLM is not available."""
        # Simple substring matching as fallback
        query = query.lower()
        scored_tools = []
        
        for tool in tools:
            score = 0.0
            
            # Check name
            if query in tool.name.lower():
                score += 0.6
            
            # Check description
            if query in tool.description.lower():
                score += 0.3
            
            # Check parameter descriptions
            for param in tool.parameters.values():
                if query in param.description.lower():
                    score += 0.1
                    break
            
            if score > 0:
                scored_tools.append((tool, score))
        
        # Sort by score (highest first)
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N
        result_tools = [tool for tool, _ in scored_tools[:limit]]
        confidence_scores = {tool.name: score for tool, score in scored_tools[:limit]}
        
        return ToolSearchResult(
            tools=result_tools,
            confidence_scores=confidence_scores
        )
