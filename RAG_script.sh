#!/bin/bash

RAG_URL="http://127.0.0.1:8000/status"
RAG_START_CMD="cd /Users/admin/AstraTrade-Project/claude-rag && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
RAG_INDEX_PATH="/Users/admin/AstraTrade-Project/claude-rag/digest_resource"

# Check if RAG API is running
if curl --silent --fail "$RAG_URL" > /dev/null; then
  echo "✅ RAG API is already running at $RAG_URL"
else
  echo "⚠️  RAG API is not running. Starting it now..."
  eval "$RAG_START_CMD &"
  sleep 5
  if curl --silent --fail "$RAG_URL" > /dev/null; then
    echo "✅ RAG API started successfully at $RAG_URL"
  else
    echo "❌ Failed to start RAG API. Please check logs."
    exit 1
  fi
fi

# Index the digest_resource directory automatically
curl -X POST "http://127.0.0.1:8000/index" \
  -H "Content-Type: application/json" \
  -d "{\"project_path\": \"$RAG_INDEX_PATH\", \"force_reindex\": true}" 