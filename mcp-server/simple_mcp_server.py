"""
Simple MCP Server for AI Chatbot
Provides basic tools that LLMs can use
"""
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import platform
import os

# Create FastMCP server
mcp = FastMCP("Simple Tools Server")

@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Example: "2 + 2", "10 * 5", "100 / 4"
    """
    try:
        # Only allow basic math operations for safety
        allowed_chars = set("0123456789+-*/.()")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "Error: Only basic math operations (+, -, *, /, parentheses) are allowed"
        
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

@mcp.tool()
def get_system_info() -> dict:
    """Get basic system information"""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse any text string"""
    return text[::-1]

@mcp.tool()
def count_words(text: str) -> dict:
    """Count words, characters, and lines in text"""
    lines = text.split('\n')
    words = text.split()
    
    return {
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
        "characters_no_spaces": len(text.replace(" ", ""))
    }

@mcp.resource("server://info")
def get_server_info() -> str:
    """Get information about this MCP server"""
    return """
    Simple Tools MCP Server
    
    Available Tools:
    - get_current_time: Get current date and time
    - calculate: Perform basic math calculations
    - get_system_info: Get system information
    - reverse_string: Reverse any text
    - count_words: Count words, chars, and lines
    
    Version: 1.0.0
    """

def main():
    """Run the MCP server"""
    # Run with SSE transport for Docker/HTTP
    import uvicorn
    uvicorn.run(mcp.get_asgi_app(), host="0.0.0.0", port=3000, log_level="info")

if __name__ == "__main__":
    main()