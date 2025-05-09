FROM tensorflow/tensorflow:nightly

WORKDIR /app

# Install curl and network debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    net-tools

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --ignore-installed blinker
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY predict.py .
COPY data_utils.py .

# Verify installations and network tools
RUN curl --version && \
    ping -c 1 127.0.0.1 && \
    python -c "import requests; print('Requests package installed')"

# Command to run the prediction script
CMD ["python", "predict.py"]