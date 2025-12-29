import httpx
from groq import Groq
from typing import List, Dict, Optional
import json
from config import config

class LLMRouter:
    def __init__(self):
        self.groq_keys = config.GROQ_API_KEYS
        self.current_key_index = 0
        self.hf_token = config.HF_TOKEN
        self.groq_failed = False
        self.groq_clients = [Groq(api_key=key) for key in self.groq_keys if key]
        
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Route chat request through Groq (with rotation) or HuggingFace fallback"""
        
        # Try Groq first with rotating keys
        if not self.groq_failed and self.groq_clients:
            for i in range(len(self.groq_keys)):
                try:
                    return await self._call_groq(messages, tools)
                except Exception as e:
                    print(f"Groq key {self.current_key_index} failed: {e}")
                    self._rotate_key()
                    
                    if i == len(self.groq_keys) - 1:
                        print("All Groq keys exhausted, falling back to HuggingFace")
                        self.groq_failed = True
        
        # Fallback to HuggingFace
        return await self._call_huggingface(messages)
    
    def _rotate_key(self):
        """Rotate to next API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.groq_keys)
    
    async def _call_groq(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Call Groq API with current key"""
        client = self.groq_clients[self.current_key_index]
        
        params = {
            "model": "llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768"
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        response = client.chat.completions.create(**params)
        
        return {
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None,
            "model": "groq",
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _call_huggingface(self, messages: List[Dict]) -> Dict:
        """Fallback to HuggingFace Inference API"""
        
        # Format messages for HF
        formatted_prompt = self._format_messages_for_hf(messages)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-70B-Instruct",
                headers={
                    "Authorization": f"Bearer {self.hf_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": formatted_prompt,
                    "parameters": {
                        "max_new_tokens": 4096,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
            )
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                return {
                    "content": data[0].get("generated_text", ""),
                    "tool_calls": None,
                    "model": "huggingface",
                    "finish_reason": "stop"
                }
            else:
                raise Exception(f"HuggingFace API error: {data}")
    
    def _format_messages_for_hf(self, messages: List[Dict]) -> str:
        """Convert chat messages to HuggingFace prompt format"""
        formatted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted) + "\n\nAssistant:"