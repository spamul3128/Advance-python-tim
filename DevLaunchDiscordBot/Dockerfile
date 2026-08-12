# syntax=docker/dockerfile:1.7
FROM python:3.13-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps (build tools for common wheels) and uv
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends build-essential curl && \
    pip install --no-cache-dir uv && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy lockfiles and dependency manifests first for better caching
COPY uv.lock ./
COPY requirements.txt ./
# If a pyproject.toml exists, copy it too for better uv detection
# (safe even if missing at build time)
COPY pyproject.toml ./

# Install dependencies with uv. Prefer the lockfile; fall back to requirements.
# --frozen ensures lockfile is authoritative when present.
RUN (test -f uv.lock && uv sync --frozen) || uv sync --from requirements.txt

# Copy the rest of the source code
COPY . .

# Default command: run the bot using uv
CMD ["uv", "run", "python", "bot.py"]

