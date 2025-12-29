FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setup Simple MCP Server
COPY mcp-server/simple_mcp_server.py ./mcp-server/
COPY mcp-server/requirements.txt ./mcp-server/
WORKDIR /app/mcp-server
RUN pip install --no-cache-dir -r requirements.txt

# Setup Backend
WORKDIR /app
COPY backend/ ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Setup Chat App
WORKDIR /app
COPY chat-app/ ./chat-app/
WORKDIR /app/chat-app
RUN pip install --no-cache-dir -r requirements.txt

# Copy supervisor config
COPY unified/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directory
RUN mkdir -p /var/log/supervisor

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
