FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setup MCP Server
RUN git clone https://github.com/modelcontextprotocol/servers.git /app/mcp-servers
WORKDIR /app/mcp-servers/src/everything
RUN npm install

# Setup Backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Setup Chat App
WORKDIR /app/chat-app
COPY chat-app/requirements.txt .
RUN pip install --no-cache-dir -r chat-app/requirements.txt
COPY chat-app/ .

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