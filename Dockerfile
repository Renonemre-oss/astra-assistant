# ================================
# ALEX/JARVIS - Dockerfile
# Multi-stage build for optimized image
# ================================

# ================================
# Stage 1: Builder
# ================================
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    python3-pyaudio \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ================================
# Stage 2: Runtime
# ================================
FROM python:3.12-slim

# Labels
LABEL maintainer="António Pereira"
LABEL description="ALEX/JARVIS AI Assistant"
LABEL version="3.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Lisbon

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 alex && \
    mkdir -p /app /app/data /app/logs && \
    chown -R alex:alex /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=alex:alex jarvis/ ./jarvis/
COPY --chown=alex:alex requirements.txt .
COPY --chown=alex:alex mypy.ini .

# Switch to non-root user
USER alex

# Create necessary directories
RUN mkdir -p \
    /app/data/models \
    /app/data/user \
    /app/data/conversation \
    /app/data/personality \
    /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose ports
EXPOSE 8000 8001

# Default command
CMD ["python", "jarvis/main.py"]
