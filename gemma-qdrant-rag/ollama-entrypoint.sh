#!/bin/sh

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done

# Pull the model
echo "Pulling Gemma 2B model..."
ollama pull gemma:2b

# Keep the container running by bringing the background process to foreground
wait
