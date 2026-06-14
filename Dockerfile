# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL scripts and data folders
COPY src ./src
COPY dataset ./dataset

# Default command (example: run ETL only)
CMD ["python", "-m", "src.etl"]
