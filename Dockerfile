# Syntax: Dockerfile for deploying the FastAPI service
# Free-tier friendly; uses Python 3.8 to match project constraint

FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional; kept minimal for slim image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and processed data used by the API endpoints
COPY src ./src
COPY data/processed ./data/processed

# Expose the API port
EXPOSE 8000

# Add a simple container healthcheck hitting the internal /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
    CMD python -c "import os,sys,urllib.request; port=int(os.environ.get('PORT','8000')); url=f'http://127.0.0.1:{port}/health';\
try:\
        with urllib.request.urlopen(url, timeout=4) as r:\
                sys.exit(0 if r.status==200 else 1)\
except Exception:\
        sys.exit(1)"

# Start the FastAPI app; PORT is provided by most PaaS (default 8000)
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio --http h11"]
