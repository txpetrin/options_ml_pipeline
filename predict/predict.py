import pandas as pd
import numpy as np
from data_utils import prepare_latest_input
import mlflow

def predict_stock_price():
    
    print("Starting prediction...")

    try:
        print("Setting MLflow tracking URI...")
        mlflow.set_tracking_uri("http://mlflow:5000")
        client = mlflow.tracking.MlflowClient()
        print("Successfully connected to MLflow server.")
    except ConnectionError as e:
        print(f"Error connecting to MLflow server: {e}")
        return
    
    ticker = "AAPL"

    experiment_name = f"{ticker}"

    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found.")
    
    experiment_id = experiment.experiment_id

    print(f"Experiment ID: {experiment_id}")

    # Search runs with the tag and order by start_time DESC (latest first)
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )

    if not runs:
        raise ValueError("No runs found with the specified tag.")
    
    print(f"Number of runs found: {len(runs)}")
    
    # Get the latest run ID
    latest_run = runs[0]
    run_id = latest_run.info.run_id
    print(f"Latest run with ticker '{ticker}': {run_id}")

    # Build model URI
    model_uri = f"runs:/{run_id}/model"

    # Load the model (pyfunc flavor)
    model = mlflow.pyfunc.load_model(model_uri)

    # TODO : Pull data from the data_utils.py file
    stock_input_data = prepare_latest_input(ticker=ticker, lookback_days=10)

    print(f"Input data for prediction: {stock_input_data}")
    print(f"Input data shape: {stock_input_data.shape}")

    # predictions = model.predict(pd.Dataframe(stock_input_data))
    # print(f"Predictions: {predictions}")
    # return predictions

if __name__ == "__main__":
    predict_stock_price()