import pika
import json
import time
import mlflow
import pandas as pd
import numpy as np
import statsmodels as sm
from polygon import RESTClient
import os
from datetime import datetime


print(f"{os.getenv('POLYGON_KEY')}", flush=True)
client = RESTClient(api_key=os.getenv("POLYGON_KEY"))


# Retry connection
for _ in range(20):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='stock')
        break
    except pika.exceptions.AMQPConnectionError:
        time.sleep(3)

# Message handler
def callback(ch, method, properties, body):
    message = json.loads(body)
    stock_read = message['stock']

    # set the MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

    tickers = ["AAPL", "LEVI"]

    return_data = pd.DataFrame()

    # List Aggregates (Bars)
    for ticker in tickers:
        dates = []
        aggs = []
        for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="day", from_="2025-01-01", to="2025-02-14", limit=400):
            dates.append(datetime.fromtimestamp(a.timestamp / 1000).date())
            aggs.append(a.close)

        return_data[ticker] = aggs
        return_data.index = dates

    results = pd.DataFrame()

    for stock in return_data.columns:
        experiment_name = stock+"-arima-forecasting"
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run():
            mlflow.autolog()

            input_data = return_data[stock].values
            print(f"DATA : {input_data}", flush=True)

            model = sm.tsa.arima.model.ARIMA(input_data, order=(1,0,0))
            model_fit = model.fit()
            print(model_fit.summary(), flush=True)

            n_periods = 5
            forecast = model_fit.get_forecast(steps=n_periods)

            ci = forecast.conf_int()
            avg_bounds = ci.mean(axis=1)
            results[stock] = avg_bounds

    print(results.head(), flush=True)

    response = json.dumps({'stock_history': return_data.to_dict(orient='records'),
                           'forecast': results.to_dict(orient='records')})
    
    # Publish result back to reply_to queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=response
    )

# Start consuming
channel.basic_consume(queue='stock', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
