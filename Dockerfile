FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

# Install system dependencies needed for your application
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    nmap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .