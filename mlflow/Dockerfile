FROM ghcr.io/mlflow/mlflow:v2.19.0

# TODO : Get these into a requirements.txt file for consistency
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt