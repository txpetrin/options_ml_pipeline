from flask import Flask, request, jsonify
import uuid
import threading
from src.data_utils import create_stock_price_prediction_dataset
from src.model_utils import create_lstm_dataset, train_lstm_model
from src.evaluation_utils import evaluate_and_promote_model
import mlflow
import mlflow.tensorflow

app = Flask(__name__)

def validate_training_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid input format: JSON expected.")

    ticker = payload.get("ticker")
    period = payload.get("period")
    epochs = payload.get("epochs")

    if not ticker or not isinstance(ticker, str):
        raise ValueError("Invalid 'ticker': Must be a non-empty string.")

    valid_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
    if period not in valid_periods:
        raise ValueError(f"Invalid 'period': Must be one of {valid_periods}.")

    if not isinstance(epochs, int) or epochs <= 0:
        raise ValueError("Invalid 'epochs': Must be a positive integer.")

    return ticker, period, epochs


def background_training(job_id, ticker, period, epochs):
    try:
        print(f"[INFO] [Job {job_id}] Starting training for {ticker} ({period}, {epochs} epochs)")

        # Set experiment name (create if doesn't exist)
        mlflow.set_tracking_uri("http://mlflow_server:5000")  # Update this if different
        mlflow.set_experiment("Stock_Price_Prediction")

        with mlflow.start_run(run_name=f"Training-{ticker}-{job_id}"):
            mlflow.log_param("ticker", ticker)
            mlflow.log_param("period", period)
            mlflow.log_param("epochs", epochs)

            stock_data, label_series = create_stock_price_prediction_dataset(
                ticker, days_to_predict=5, period=period
            )

            if len(stock_data) == 0 or len(label_series) == 0:
                print(f"[ERROR] [Job {job_id}] Insufficient data.")
                mlflow.log_param("status", "failed")
                return

            dataset, input_shape, output_shape = create_lstm_dataset(stock_data, label_series)

            run_id, model_path, final_loss = train_lstm_model(
                dataset=dataset,
                input_shape=input_shape,
                output_shape=output_shape,
                ticker=ticker,
                epochs=epochs
            )

            mlflow.log_metric("final_loss", final_loss)

            evaluate_and_promote_model(model_path=model_path)

            # Log the model artifact
            mlflow.tensorflow.log_model(
                tf_saved_model_dir=model_path,
                tf_meta_graph_tags=None,
                tf_signature_def_key=None,
                artifact_path="model"
            )

            print(f"[SUCCESS] [Job {job_id}] Training completed. Run ID: {run_id}, Final Loss: {final_loss}")

    except Exception as e:
        print(f"[ERROR] [Job {job_id}] {str(e)}")


@app.route("/train", methods=["POST"])
def train_model_api():
    try:
        payload = request.get_json()
        ticker, period, epochs = validate_training_payload(payload)

        job_id = str(uuid.uuid4())

        # Kick off background thread
        training_thread = threading.Thread(
            target=background_training,
            args=(job_id, ticker, period, epochs)
        )
        training_thread.start()

        print(f"[INFO] Job {job_id} dispatched.")

        return jsonify({
            "status": "started",
            "job_id": job_id,
            "message": "Training started in background."
        }), 202

    except ValueError as ve:
        return jsonify({"status": "failed", "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, threaded=True)
