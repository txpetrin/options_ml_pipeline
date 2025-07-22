import pika
import json
import time
import mlflow
import pandas as pd
import yfinance as yf
import pmdarima as pm

### TEST HERE TO SEE IF MLFLOW IS WORKING ###
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# NOTE ON BEHAVIOR : 
# Trevor could have picked a better package than pdarima, it was being uncooperative
# Should have used statsmodels instead for the autolog feautres. 
# Good news is, though, that the connections are working and data is correctly flowing
# between frontend and backend with models being properly logged in MLflow.

# NOTE ON YFINANCE :
# Trevor will find an alternative to this. The rate limiting factors throws errors at 
# literally the worst times. Commented out for now but the pull currently works when
# rates are not limited. 

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
    mlflow.autolog()

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

    response = json.dumps({'number': number, 'squared': result, 
                           'predictions': y_pred.tolist(), 
                           'dataframe': df.to_dict(orient='records')})

    ### TODO : Import yfinance data and set up ARIMA model
    # yahoo_pull = yf.download("AAPL", start="2025-01-01", end="2025-02-01")
    # print(yahoo_pull.head(), flush=True)
    # print(yahoo_pull.columns, flush=True)
    # print(yahoo_pull[('Close', "AAPL")], flush=True)
    # 
    # 
    # input_data = yahoo_pull[('Close', "AAPL")].values
    # print(f"DATA : {input_data}", flush=True)
    # 
    # ts = pd.Series(input_data)
    # model = pm.auto_arima(ts, seasonal=False, stepwise=True, trace=True)
    # print(model.summary(), flush=True)
    # 
    # # Forecast the next 5 steps
    # # NOTE : forecast is currently a Series object, not a DataFrame
    # n_periods = 5
    # forecast = model.predict(n_periods=n_periods)
    # print(f"Forecast: {forecast}", flush=True)


    # response = json.dumps({'number': number, 'squared': result, 
    #                        'predictions': y_pred.tolist(), 
    #                        'dataframe': df.to_dict(orient='records'),
    #                        'yahoo_pull': yahoo_pull.to_dict(orient='records'),
    #                        'forecast': forecast.to_dict()})
    
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
