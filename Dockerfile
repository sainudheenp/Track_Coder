FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TRACKCODER_DATA_DIR=/data \
    TRACKCODER_WORKBOOK=/data/trackcoder.xlsx \
    TRACKCODER_SCREENSHOT_DIR=/data/screenshots \
    TRACKCODER_HEADLESS=true \
    CHROME_BINARY=/usr/bin/chromium \
    CHROME_DRIVER_PATH=/usr/bin/chromedriver

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install ".[sheets]" \
    && useradd --create-home --uid 10001 trackcoder \
    && mkdir -p /data \
    && chown -R trackcoder:trackcoder /app /data

USER trackcoder
VOLUME ["/data"]

ENTRYPOINT ["trackcoder"]
CMD ["--help"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["trackcoder", "--version"]
