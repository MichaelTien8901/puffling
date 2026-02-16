# Puffling - AI-Powered Algorithmic Trading App

A personal AI-powered trading application built on top of [Puffin](https://github.com/MichaelTien8901/puffin) — the algorithmic trading library.

## Architecture

- **Backend**: FastAPI — REST/WebSocket API wrapping Puffin's trading modules
- **Frontend**: Next.js + React — Rich trading dashboard with real-time charts
- **Desktop**: Tauri — Lightweight native app for Linux/Windows

## Project Structure

```
puffling/
├── backend/         # FastAPI application
│   ├── api/         # REST routes & WebSocket handlers
│   ├── services/    # Thin wrappers around Puffin modules
│   ├── models/      # SQLAlchemy ORM models
│   └── core/        # Config, database, dependencies
├── frontend/        # Next.js application
│   └── src/
├── desktop/         # Tauri desktop shell
└── pyproject.toml
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Rust toolchain (for Tauri desktop builds)
- [Puffin](https://github.com/MichaelTien8901/puffin) library

## Setup

```bash
# Install Puffin as editable dependency
pip install -e ~/projects/puffin

# Install Puffling backend
pip install -e .

# Install frontend dependencies
cd frontend && npm install

# Run backend
uvicorn backend.main:app --reload

# Run frontend (separate terminal)
cd frontend && npm run dev
```
