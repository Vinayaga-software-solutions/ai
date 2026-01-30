#!/bin/sh

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done

# Pull the model defined in environment or default to gemma2:2b
MODEL=${LLM_MODEL:-gemma2:2b}
echo "Pulling model: $MODEL..."
ollama pull $MODEL

# Keep the container running
wait
