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
        channel.queue_declare(queue='square')
        break
    except pika.exceptions.AMQPConnectionError:
        time.sleep(3)

# Message handler
def callback(ch, method, properties, body):
    message = json.loads(body)
    number = message['number']
    result = number * number

    ### TEST HERE TO SEE IF CONNECTION IS WORKING ###
    print(f"Processed: {number} -> {result}", flush=True)


    ### TEST HERE TO SEE IF MLFLOW IS WORKING ###
    # set the MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

    # create an MLflow experiment
    experiment_name = "iris-classification"
    mlflow.set_experiment(experiment_name)


    with mlflow.start_run():
        mlflow.sklearn.autolog()
        # load the iris dataset
        db = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(db.data, db.target, test_size=0.2, random_state=42)

        # create and train a random forest classifier
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)

        print("HIT MODEL FIT", flush=True)

        # predict on the test set
        y_pred = rf.predict(X_test)

        df = pd.DataFrame(X_test, columns=db.feature_names)
        df['iris_actual'] = y_test
        df['iris_predictions'] = y_pred


        print(f"HIT PREDICT", flush=True)
        print(f"Prediction: {y_pred}", flush=True)





    # NOTE : SEE IF RUN NEEDS TO BE ENDED HERE


    # TODO : Separate the independent models for building process
    # TODO : Import yfinance data and set up ARIMA model

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

    response = json.dumps({'number': number, 'squared': result, 
                            'predictions': y_pred.tolist(), 
                           'dataframe': df.to_dict(orient='records'),
                           'yahoo_pull': return_data.to_dict(),
                           'forecast': results.to_dict()})
    
    # Publish result back to reply_to queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=response
    )

# Start consuming
channel.basic_consume(queue='square', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
