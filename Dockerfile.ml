# GPU-enabled ML Service Dockerfile
FROM nvidia/cuda:12.2-base-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Create app directory
WORKDIR /app

# Install Python dependencies with GPU support
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir tensorflow[and-cuda]==2.15.0

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs data

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import tensorflow as tf; print('GPU available:', len(tf.config.list_physical_devices('GPU')) > 0)" || exit 1

# Default command
CMD ["python", "backend/ml_server.py"]