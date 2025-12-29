import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEYS: List[str] = os.getenv('GROQ_API_KEYS', '').split(',')
    HF_TOKEN: str = os.getenv('HF_TOKEN', '')
    # Changed to localhost since all services run in same container
    MCP_SERVER_URL: str = os.getenv('MCP_SERVER_URL', 'http://localhost:3000')
    
config = Config()