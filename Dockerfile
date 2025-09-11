# Multi-stage build for net.krak
# Stage 1: Build stage with all tools
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Full functionality image
FROM python:3.9-slim as full

# Install system dependencies
RUN apt-get update && apt-get install -y \
    net-tools \
    wireless-tools \
    aircrack-ng \
    reaver \
    bully \
    iw \
    iputils-ping \
    netcat-openbsd \
    curl \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs captures

# Set environment variables
ENV PYTHONPATH=/app
ENV NETKRAK_LOG_FILE=/app/logs/netkrak.jsonlog
ENV PATH=/root/.local/bin:$PATH

# Make scripts executable
RUN chmod +x *.sh *.py

# Create non-root user for security
RUN useradd -m -u 1000 netkrak && \
    chown -R netkrak:netkrak /app

# Switch to non-root user
USER netkrak

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "dashboard_api:app"]

# Stage 3: Minimal demo image (safe mode)
FROM python:3.9-slim as demo

# Install minimal dependencies for demo mode
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy only web interface files for demo mode
COPY dashboard_api.py .
COPY requirements.txt .
COPY utils/ ./utils/
COPY *.html .

# Install only web dependencies
RUN pip install --no-cache-dir --user flask gunicorn

# Create necessary directories
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV NETKRAK_LOG_FILE=/app/logs/netkrak.jsonlog
ENV PATH=/root/.local/bin:$PATH
ENV NETKRAK_DEMO_MODE=true

# Create non-root user
RUN useradd -m -u 1000 netkrak && \
    chown -R netkrak:netkrak /app

# Switch to non-root user
USER netkrak

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Demo mode command (no pentest tools)
CMD ["python3", "dashboard_api.py", "--demo-mode"]