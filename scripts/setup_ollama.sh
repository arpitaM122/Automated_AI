#!/usr/bin/env bash
# Installs (if needed), starts, and pulls the default model for Ollama —
# the local LLM runtime this platform uses.
set -e

MODEL="${OLLAMA_MODEL:-llama3.1}"

if ! command -v ollama &> /dev/null; then
  echo "Ollama is not installed."
  echo "Install it from https://ollama.com/download and re-run this script."
  exit 1
fi

echo "Starting Ollama server in the background (if not already running)..."
if ! pgrep -x "ollama" > /dev/null; then
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  sleep 3
fi

echo "Pulling model: $MODEL"
ollama pull "$MODEL"

echo "Ollama is ready. Server: http://localhost:11434  Model: $MODEL"
