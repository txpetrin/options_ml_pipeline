FROM python:3.10-slim
WORKDIR /app
COPY app.py .
RUN pip install flask pika flask-cors

CMD ["python", "app.py"]
