"""Tools registry and handlers."""
import os
import json
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime


# Tool registry
class ToolRegistry:
    """Registry for agent tools."""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default built-in tools."""
        # Web search tool
        self.register_tool({
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        }, web_search_handler)
        
        # Calculator tool
        self.register_tool({
            "name": "calculator",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"},
                },
                "required": ["expression"],
            },
        }, calculator_handler)
        
        # File read tool
        self.register_tool({
            "name": "file_read",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                },
                "required": ["path"],
            },
        }, file_read_handler)
        
        # Current time tool
        self.register_tool({
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {"type": "object"},
        }, get_current_time_handler)
    
    def register_tool(self, schema: Dict[str, Any], handler: Callable):
        """Register a new tool."""
        name = schema.get("name")
        self._tools[name] = schema
        self._handlers[name] = handler
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool schema by name."""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered tools."""
        return self._tools
    
    def get_handler(self, name: str) -> Optional[Callable]:
        """Get tool handler by name."""
        return self._handlers.get(name)


# Tool handlers
async def web_search_handler(args: Dict[str, Any]) -> str:
    """Handle web search."""
    query = args.get("query", "")
    num_results = args.get("num_results", 5)
    
    # In production, integrate with Tavily, Serper, or DuckDuckGo
    # For now, return mock results
    return json.dumps({
        "results": [
            {"title": f"Result for {query}", "url": "https://example.com", "snippet": "Sample result"}
            for i in range(num_results)
        ],
        "query": query,
    })


async def calculator_handler(args: Dict[str, Any]) -> str:
    """Handle mathematical calculation."""
    expression = args.get("expression", "")
    
    try:
        # Safe eval for basic math
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
        else:
            result = "Invalid expression"
    except Exception as e:
        result = f"Error: {str(e)}"
    
    return str(result)


async def file_read_handler(args: Dict[str, Any]) -> str:
    """Handle file reading."""
    path = args.get("path", "")
    
    try:
        with open(path, "r") as f:
            content = f.read()
        return content[:5000]  # Limit output
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


async def get_current_time_handler(args: Dict[str, Any]) -> str:
    """Handle getting current time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# Global registry
_registry = ToolRegistry()


def get_tool_handler(name: str) -> Optional[Callable]:
    """Get tool handler by name."""
    return _registry.get_handler(name)


def get_all_tools() -> Dict[str, Dict[str, Any]]:
    """Get all registered tools."""
    return _registry.get_all_tools()


def register_tool(schema: Dict[str, Any], handler: Callable):
    """Register a new tool."""
    _registry.register_tool(schema, handler)