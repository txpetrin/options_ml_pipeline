import pika
import json
import time
import mlflow
import pandas as pd
import yfinance as yf
import numpy as np
# import pmdarima as pm
import statsmodels as sm

### TEST HERE TO SEE IF MLFLOW IS WORKING ###
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

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

    ### TEST HERE TO SEE IF MLFLOW IS WORKING ###
    # set the MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

    stocks = ["AAPL", "NVDA"]
    yahoo_pull = yf.download(stocks, start="2025-01-01", end="2025-02-01")
    print(yahoo_pull.head(), flush=True)
    print(yahoo_pull.columns, flush=True)
    print(yahoo_pull[('Close', "AAPL")], flush=True)

    return_data = pd.DataFrame()

    if yahoo_pull.empty:
        return_data['NULL'] = np.zeros(20)  # Default to zeroes if no data

    else:
        for stock in stocks:
            return_data[stock] = yahoo_pull['Close'][stock]

        return_data.index = return_data.index.astype(str)

    print(return_data.head())

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
