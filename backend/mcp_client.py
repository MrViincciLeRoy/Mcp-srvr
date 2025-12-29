import httpx
from typing import List, Dict
import json
from config import config

class MCPClient:
    def __init__(self):
        self.base_url = config.MCP_SERVER_URL
        
    async def get_tools(self) -> List[Dict]:
        """Get available tools from MCP server"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/tools", timeout=10.0)
                return response.json()
        except Exception as e:
            print(f"Error getting MCP tools: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool on the MCP server"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/execute",
                    json={
                        "tool": tool_name,
                        "arguments": arguments
                    }
                )
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_tools(self, tool_calls: List) -> List[Dict]:
        """Execute multiple tool calls"""
        results = []
        for tool_call in tool_calls:
            result = await self.execute_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            results.append({
                "tool_call_id": tool_call.id,
                "result": result
            })
        return results