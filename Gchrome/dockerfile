# Use Python 3.11 as the base image
FROM python:3.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    default-jdk \
    && wget -q https://ftp.mozilla.org/pub/firefox/releases/115.14.0esr/linux-x86_64/en-US/firefox-115.14.0esr.tar.bz2 \
    && tar xjf firefox-115.14.0esr.tar.bz2 \
    && mv firefox /opt/firefox \
    && ln -s /opt/firefox/firefox /usr/bin/firefox \
    && rm -rf /var/lib/apt/lists/* \
    && rm firefox-115.14.0esr.tar.bz2


RUN pip install --no-cache-dir -r req.txt

ENTRYPOINT ["python", "main.py"]
