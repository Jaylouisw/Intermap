# Dockerfile for Intermap
# Multi-stage build for minimal image size

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend
COPY frontend/package*.json frontend/
WORKDIR /app/frontend
RUN npm ci --only=production

# Build frontend
COPY frontend/ .
RUN npm run build

# Download Kubo
WORKDIR /tmp
RUN wget https://dist.ipfs.tech/kubo/v0.31.0/kubo_v0.31.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.31.0_linux-amd64.tar.gz && \
    mv kubo/ipfs /usr/local/bin/ipfs && \
    chmod +x /usr/local/bin/ipfs


# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    traceroute \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy IPFS binary
COPY --from=builder /usr/local/bin/ipfs /usr/local/bin/ipfs

# Create app user
RUN useradd -m -u 1000 intermap && \
    mkdir -p /home/intermap/.ipfs && \
    chown -R intermap:intermap /home/intermap

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application
COPY --chown=intermap:intermap . .
COPY --from=builder --chown=intermap:intermap /app/frontend/build /app/frontend/build

# Switch to app user
USER intermap

# Initialize IPFS
RUN ipfs init

# Expose ports
EXPOSE 5000 8000 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start script
COPY --chown=intermap:intermap docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "launch.py"]
