# Multi-stage Docker build for Wandr Backend API
# Stage 1: Development base image
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Dependencies
FROM base AS dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development
FROM dependencies AS development

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash --user-group app

# Change ownership of app directory
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Production
FROM dependencies AS production

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash --user-group app

# Change ownership of app directory
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]