from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

from llm_router import LLMRouter
from mcp_client import MCPClient

app = FastAPI(title="Chatbot Backend API")

# CORS middleware for Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_router = LLMRouter()
mcp_client = MCPClient()

class ChatRequest(BaseModel):
    messages: List[Dict]
    use_mcp: bool = False

class ChatResponse(BaseModel):
    content: str
    model: str
    finish_reason: str

@app.get("/")
async def root():
    return {"status": "online", "service": "Chatbot Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with LLM routing and MCP support"""
    try:
        tools = None
        
        # Get MCP tools if requested
        if request.use_mcp:
            tools = await mcp_client.get_tools()
        
        # Get LLM response
        response = await llm_router.chat(request.messages, tools)
        
        # Handle tool calls if present
        if response.get("tool_calls"):
            # Execute tools
            tool_results = await mcp_client.execute_tools(response["tool_calls"])
            
            # Add tool results to conversation
            request.messages.append({
                "role": "assistant",
                "content": response["content"],
                "tool_calls": response["tool_calls"]
            })
            
            for result in tool_results:
                request.messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": json.dumps(result["result"])
                })
            
            # Get final response with tool results
            final_response = await llm_router.chat(request.messages, tools)
            return ChatResponse(
                content=final_response["content"],
                model=final_response["model"],
                finish_reason=final_response["finish_reason"]
            )
        
        return ChatResponse(
            content=response["content"],
            model=response["model"],
            finish_reason=response["finish_reason"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools"""
    tools = await mcp_client.get_tools()
    return {"tools": tools}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)