# Track Coder Makefile
# Provides convenient commands for Docker operations

.PHONY: help setup build run run-date clean logs shell test

# Default target
help:
	@echo "Track Coder Docker Commands"
	@echo "=========================="
	@echo "make setup      - Initial setup (build image, create dirs, copy .env)"
	@echo "make build      - Build Docker image"
	@echo "make run        - Run Track Coder (yesterday's data)"
	@echo "make run-date   - Run with custom date (DATE=2025-01-01)"
	@echo "make compose    - Run with Docker Compose"
	@echo "make logs       - View Docker Compose logs"
	@echo "make shell      - Open shell in container"
	@echo "make clean      - Clean up containers and images"
	@echo "make test       - Test the setup"
	@echo ""
	@echo "Examples:"
	@echo "  make run-date DATE=2025-01-01"
	@echo "  make setup && make run"

setup:
	@echo "🚀 Setting up Track Coder..."
	@mkdir -p output screenshots
	@if [ ! -f .env ] && [ -f .env.example ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from template"; \
		echo "⚠️  Please edit .env with your credentials"; \
	fi
	@$(MAKE) build

build:
	@echo "🏗️  Building Docker image..."
	docker build -t track-coder .
	@echo "✅ Build complete"

run:
	@echo "🔄 Running Track Coder..."
	@mkdir -p output screenshots
	docker run --rm \
		--env-file .env \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/screenshots:/app/screenshots \
		track-coder

run-date:
	@echo "🔄 Running Track Coder for date: $(DATE)"
	@mkdir -p output screenshots
	docker run --rm \
		--env-file .env \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/screenshots:/app/screenshots \
		track-coder python main.py -date $(DATE)

compose:
	@echo "🐋 Running with Docker Compose..."
	docker-compose up

compose-bg:
	@echo "🐋 Running with Docker Compose in background..."
	docker-compose up -d

logs:
	docker-compose logs -f

shell:
	@echo "🐚 Opening shell in container..."
	docker run --rm -it \
		--env-file .env \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/screenshots:/app/screenshots \
		track-coder bash

test:
	@echo "🧪 Testing setup..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file missing"; \
		exit 1; \
	fi
	docker run --rm track-coder python -c "import selenium; print('✅ Selenium available')"
	@echo "✅ Basic test passed"

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v 2>/dev/null || true
	docker rmi track-coder 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Development helpers
dev-build:
	docker build --no-cache -t track-coder .

dev-shell:
	docker run --rm -it \
		--env-file .env \
		-v $$(pwd):/app \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/screenshots:/app/screenshots \
		track-coder bash