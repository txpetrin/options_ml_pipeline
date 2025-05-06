FROM tensorflow/tensorflow:nightly

WORKDIR /app

COPY requirements.txt .
RUN pip install --ignore-installed blinker
RUN pip install --no-cache-dir -r requirements.txt

COPY predict.py .
COPY data_utils.py . 

CMD ["python", "predict.py"]