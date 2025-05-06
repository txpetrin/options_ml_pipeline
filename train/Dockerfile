FROM tensorflow/tensorflow:nightly

WORKDIR /app

COPY requirements.txt .
RUN pip install --ignore-installed blinker
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py .
COPY model_utils.py .
COPY data_utils.py .

CMD ["python", "train.py"]