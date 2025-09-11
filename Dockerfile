FROM python:3.9-slim

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
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs captures

# Set environment variables
ENV PYTHONPATH=/app
ENV NETKRAK_LOG_FILE=/app/logs/netkrak.jsonlog

# Make scripts executable
RUN chmod +x *.sh *.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "dashboard_api:app"]