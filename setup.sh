#!/bin/bash

# Track Coder Docker Setup Script
# This script helps you get started with Track Coder using Docker

set -e

echo "🚀 Track Coder Docker Setup"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create output directories
echo "📁 Creating output directories..."
mkdir -p output screenshots
echo "✅ Created output and screenshots directories"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env file with your credentials before running"
        echo "   Required: MonkeyType and Software.com login details"
    else
        echo "❌ .env.example not found. Please create .env manually with your credentials."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Build Docker image
echo "🏗️  Building Docker image..."
docker build -t track-coder . || {
    echo "❌ Failed to build Docker image"
    exit 1
}
echo "✅ Docker image built successfully"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Run Track Coder:"
echo "   ./run.sh"
echo ""
echo "Or use Docker Compose:"
echo "   docker-compose up"
echo ""
echo "For more options, see DOCKER.md"