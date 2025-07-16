# Docker Guide for Track Coder

This guide provides detailed instructions for running Track Coder in a containerized environment.

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/sainudheenp/track_coder.git
   cd track_coder
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up
   ```

## Docker Commands

### Building the Image

```bash
# Build the Docker image
docker build -t track-coder .

# Build with specific tag
docker build -t track-coder:latest .
```

### Running the Container

#### Basic Run
```bash
docker run --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/screenshots:/app/screenshots \
  track-coder
```

#### Run with Custom Date
```bash
docker run --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/screenshots:/app/screenshots \
  track-coder python main.py -date 2025-01-01
```

#### Interactive Mode
```bash
docker run -it --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/screenshots:/app/screenshots \
  track-coder bash
```

## Docker Compose Usage

### Standard Run
```bash
# Run in foreground
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Custom Date with Profiles
```bash
# Run with manual profile for custom date
docker-compose --profile manual up track-coder-custom
```

### Managing Services
```bash
# Stop services
docker-compose down

# Rebuild and run
docker-compose up --build

# Remove containers and volumes
docker-compose down -v
```

## Volume Mounts

The container uses two volume mounts:

- **`./output:/app/output`**: Excel output files
- **`./screenshots:/app/screenshots`**: Screenshot files

Make sure these directories exist locally:
```bash
mkdir -p output screenshots
```

## Environment Variables

Required environment variables (put in `.env` file):

```env
# MonkeyType credentials
userEmail_monkey=your_email@gmail.com
password_monkey=your_password

# Software.com credentials  
userEmail_code_time=your_email@gmail.com
password_code_time=your_password
```

## Troubleshooting

### Chrome/WebDriver Issues
The container installs Chrome dependencies but lets webdriver-manager handle Chrome installation at runtime. If you encounter Chrome-related errors:

1. Ensure your internet connection is stable
2. The container may need to download Chrome on first run
3. WebDriver manager will handle version compatibility

### Permission Issues
If you encounter permission issues with volume mounts:

```bash
# Fix permissions for output directories
chmod 755 output screenshots
```

### Network Issues
If the container cannot download dependencies:

1. Check your internet connection
2. Verify DNS resolution
3. Consider using a different network if behind a corporate firewall

## Advanced Usage

### Custom Dockerfile

To extend the base image:

```dockerfile
FROM track-coder:latest

# Add custom dependencies
RUN pip install additional-package

# Override entrypoint
ENTRYPOINT ["python", "custom_script.py"]
```

### Using with CI/CD

Example GitHub Actions workflow:

```yaml
name: Run Track Coder
on:
  schedule:
    - cron: '0 9 * * *'  # Run daily at 9 AM

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and run
        run: |
          echo "userEmail_monkey=${{ secrets.MONKEY_EMAIL }}" > .env
          echo "password_monkey=${{ secrets.MONKEY_PASSWORD }}" >> .env
          echo "userEmail_code_time=${{ secrets.CODE_TIME_EMAIL }}" >> .env
          echo "password_code_time=${{ secrets.CODE_TIME_PASSWORD }}" >> .env
          docker-compose up
```

## Performance Optimization

### Multi-stage Build
The current Dockerfile is optimized for development. For production, consider:

```dockerfile
# Production optimized version
FROM python:3.11-slim as base
# ... (dependencies)

FROM base as production
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Caching
Docker layer caching is optimized by copying `requirements.txt` before application code.

## Security Considerations

1. **Never commit `.env` file** - it contains sensitive credentials
2. **Use secrets management** in production environments
3. **Regular updates** - keep base images and dependencies updated
4. **Network isolation** - run in isolated networks when possible

## Monitoring and Logging

### View Container Logs
```bash
# Docker
docker logs <container_id>

# Docker Compose
docker-compose logs -f track-coder
```

### Health Checks
Add health checks to docker-compose.yml:

```yaml
services:
  track-coder:
    # ... existing config
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
```