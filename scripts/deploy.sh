#!/usr/bin/env bash
# Builds and runs the full stack (FastAPI backend + Ollama) locally via Docker Compose.
set -e

echo "Building and starting containers..."
docker compose -f docker/docker-compose.yml up --build -d

echo ""
echo "Deployed."
echo "  API:       http://localhost:8000"
echo "  Docs:      http://localhost:8000/docs"
echo "  Dashboard: http://localhost:8000/dashboard"
echo ""
echo "View logs with: docker compose -f docker/docker-compose.yml logs -f"
