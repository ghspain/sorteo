FROM python:3.12-slim

WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

    # Set environment variables
    ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for layer caching and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Default port for Streamlit
EXPOSE 8501

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail -http://localhost:8501/_stcore/health || exit 1

  # Copy application code
COPY . .

# Command to run the application
CMD ["streamlit", "run", "app.py"]
