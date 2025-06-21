# Enhanced Printify Automation Tool
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r printify && useradd -r -g printify -d /app -s /bin/bash printify

# Create app directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/printify/.local

# Copy application code
COPY --chown=printify:printify . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/temp && \
    chown -R printify:printify /app

# Create a default config template if none exists
RUN if [ ! -f config.json ]; then \
    echo '{"api": {"access_token": "", "shop_id": ""}}' > config-template.json; \
    fi

# Set PATH to include user packages
ENV PATH=/home/printify/.local/bin:$PATH

# Switch to non-root user
USER printify

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Expose port
EXPOSE 7860

# Default command
CMD ["python3", "app.py"]

# Build-time metadata
LABEL maintainer="Enhanced Printify Automation Tool" \
      version="2.0" \
      description="AI-powered Printify automation with web interface" \
      org.opencontainers.image.source="https://github.com/your-repo/printify-automation" \
      org.opencontainers.image.title="Printify Automation Tool" \
      org.opencontainers.image.description="Smart automation tool for Printify product creation with AI-powered features"