# Syntax: Dockerfile for deploying the FastAPI service
# Free-tier friendly; uses Python 3.8 to match project constraint

FROM python:3.8-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional; kept minimal for slim image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps (API-only for Space)
COPY requirements.api.txt ./
RUN pip install --no-cache-dir -r requirements.api.txt

# Copy source and processed data used by the API endpoints
COPY src ./src
COPY data/processed ./data/processed

# Expose the API port (Hugging Face Spaces expects $PORT, typically 7860)
EXPOSE 7860
ENV PORT=7860

# Add a simple container healthcheck hitting the internal /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
    CMD python -c "import os,sys,urllib.request; port=int(os.environ.get('PORT','7860')); url=f'http://127.0.0.1:{port}/health';\
try:\
        with urllib.request.urlopen(url, timeout=4) as r:\
                sys.exit(0 if r.status==200 else 1)\
except Exception:\
        sys.exit(1)"

# Start the FastAPI app; PORT is provided by most PaaS (default 7860 for HF Spaces)
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-7860} --loop asyncio --http h11"]
