FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y build-essential

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire codebase
COPY . .

# Entrypoint: Flask app
CMD ["python", "app/main.py"]
