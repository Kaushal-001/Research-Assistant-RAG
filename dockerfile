# Use official Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install minimal build tools required by some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Ensure data directory exists (will be persisted via Docker volume)
RUN mkdir -p /app/data

# Expose both ports (Uvicorn & Streamlit). Compose will publish appropriate ports.
EXPOSE 8000 8501

# Default command: run FastAPI via Uvicorn.
# Compose will override this for Streamlit service.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]