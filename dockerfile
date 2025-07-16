# Use Python 3.11 as the base image
FROM python:3.11-slim

# Install system dependencies needed for Selenium WebDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libxrandr2 \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies with trusted hosts to handle SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy the rest of the application
COPY . /app

# Create directories for outputs
RUN mkdir -p /app/output /app/screenshots

# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Note: Chrome will be installed by webdriver-manager at runtime
# This approach allows the container to download the compatible Chrome version

ENTRYPOINT ["python", "main.py"]
