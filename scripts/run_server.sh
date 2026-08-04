#!/usr/bin/env bash
# Launches the FastAPI backend locally with auto-reload.
set -e

if [ ! -f ".env" ]; then
  echo "No .env found, copying from .env.example"
  cp .env.example .env
fi

export $(grep -v '^#' .env | xargs) 2>/dev/null || true

echo "Starting FastAPI backend on http://${APP_HOST:-0.0.0.0}:${APP_PORT:-8000}"
uvicorn app.main:app --reload --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}"
