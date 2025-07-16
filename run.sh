#!/bin/bash

# Track Coder Run Script
# Simple script to run Track Coder with Docker

set -e

# Default date is yesterday
DEFAULT_DATE=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")

# Parse command line arguments
DATE=${1:-$DEFAULT_DATE}

echo "🔄 Running Track Coder..."
echo "📅 Date: $DATE"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run ./setup.sh first."
    exit 1
fi

# Ensure output directories exist
mkdir -p output screenshots

# Run the container
if [ -n "$DATE" ]; then
    echo "🐋 Running Docker container with custom date: $DATE"
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/screenshots:/app/screenshots" \
        track-coder python main.py -date "$DATE"
else
    echo "🐋 Running Docker container with default date"
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/screenshots:/app/screenshots" \
        track-coder
fi

echo "✅ Track Coder completed!"
echo "📊 Check output/ directory for Excel files"
echo "📸 Check screenshots/ directory for images"