import asyncio
import subprocess
from typing import List, Dict
from config import config

class MCPClient:
    def __init__(self):
        self.base_url = config.MCP_SERVER_URL
        self.process = None
        self.tools_cache = []
        
    async def start_mcp_server(self):
        """Start the MCP server process if using stdio transport"""
        # For now, we'll just return empty tools since the MCP server
        # runs as a separate supervised process
        # In production, you'd connect via stdio or HTTP
        return []
    
    async def get_tools(self) -> List[Dict]:
        """Get available tools from MCP server"""
        # Return the tools our simple MCP server provides
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Get the current date and time",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Safely evaluate a mathematical expression. Example: '2 + 2', '10 * 5', '100 / 4'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Get basic system information",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "reverse_string",
                    "description": "Reverse any text string",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to reverse"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "count_words",
                    "description": "Count words, characters, and lines in text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to analyze"
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool by calling the MCP server"""
        # Import the MCP server functions directly for now
        # In production, this would communicate via stdio or HTTP
        try:
            if tool_name == "get_current_time":
                from datetime import datetime
                return {"result": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            elif tool_name == "calculate":
                expression = arguments.get("expression", "")
                allowed_chars = set("0123456789+-*/.()")
                if not all(c in allowed_chars or c.isspace() for c in expression):
                    return {"error": "Only basic math operations allowed"}
                
                result = eval(expression, {"__builtins__": {}}, {})
                return {"result": f"{expression} = {result}"}
            
            elif tool_name == "get_system_info":
                import platform
                return {
                    "result": {
                        "platform": platform.system(),
                        "platform_release": platform.release(),
                        "architecture": platform.machine(),
                        "python_version": platform.python_version()
                    }
                }
            
            elif tool_name == "reverse_string":
                text = arguments.get("text", "")
                return {"result": text[::-1]}
            
            elif tool_name == "count_words":
                text = arguments.get("text", "")
                lines = text.split('\n')
                words = text.split()
                return {
                    "result": {
                        "characters": len(text),
                        "words": len(words),
                        "lines": len(lines),
                        "characters_no_spaces": len(text.replace(" ", ""))
                    }
                }
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_tools(self, tool_calls: List) -> List[Dict]:
        """Execute multiple tool calls"""
        results = []
        for tool_call in tool_calls:
            import json
            result = await self.execute_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            results.append({
                "tool_call_id": tool_call.id,
                "result": result
            })
        return results
