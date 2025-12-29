# AI Chatbot with Groq Rotation & MCP

Multi-LLM chatbot with automatic API key rotation (Groq) and HuggingFace fallback, integrated with MCP (Model Context Protocol) for extended capabilities.

## Features

- 🚀 FastAPI backend with async LLM routing
- 🎨 Flask chat interface with modern UI
- 🔄 Automatic Groq API key rotation
- 🛡️ HuggingFace fallback on failure
- 🔧 MCP server integration (filesystem, database, web tools)
- 🐳 Docker containerized (unified container for easy deployment)
- 💾 Session-based conversation history

## Tech Stack

- **Backend**: Python FastAPI + Uvicorn
- **Frontend**: Python Flask + HTML/CSS/JS
- **LLM**: Groq (primary) + HuggingFace (fallback)
- **Tools**: MCP Everything Server
- **Container**: Docker with Supervisor

## Quick Start (Local)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Build and run with Docker:
```bash
docker build -f unified/Dockerfile -t ai-chatbot .
docker run -p 5000:5000 --env-file .env ai-chatbot
```

4. Access the chat at http://localhost:5000

## Deploy on Render

1. Push to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Settings:
   - **Docker Path**: `unified/Dockerfile`
   - **Environment Variables**: Add from `.env.example`
5. Deploy!

## Deploy on Railway
```bash
railway login
railway init
railway up
```

## Deploy on VPS
```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and run
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot

# Create .env file
nano .env
# (Add your API keys)

# Build and run
docker build -f unified/Dockerfile -t ai-chatbot .
docker run -d -p 80:5000 --env-file .env --restart unless-stopped ai-chatbot
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEYS` | Comma-separated Groq API keys for rotation | Yes |
| `HF_TOKEN` | HuggingFace API token for fallback | Yes |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | Yes |

## API Endpoints

### Chat Interface
- `GET /` - Main chat interface
- `POST /api/send` - Send message
- `POST /api/clear` - Clear conversation
- `GET /api/history` - Get conversation history

### Backend API (Internal)
- `GET /health` - Health check
- `POST /api/chat` - LLM chat endpoint
- `GET /api/mcp/tools` - Get available MCP tools

## Architecture
```
User Browser
    ↓
Flask Chat App (Port 5000)
    ↓
FastAPI Backend (Port 8000)
    ↓
LLM Router → [Groq APIs] → [HuggingFace]
    ↓
MCP Server (Port 3000) → [Filesystem, Database, Web Tools]
```

All services run in a single container managed by Supervisor.

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## License

MIT