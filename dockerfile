# Use Python 3.11 as the base image
FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install -r ./requirements.txt

RUN chmod +x main.py

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]
