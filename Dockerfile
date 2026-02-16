FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv setuptools>=77

COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]" || true
RUN uv pip install --system statsmodels || true

COPY . .
