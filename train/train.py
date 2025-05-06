import numpy as np
import mlflow
import mlflow.tensorflow
from mlflow.models import infer_signature
from datetime import datetime
import uuid

from sklearn.linear_model import LogisticRegression
import mlflow.sklearn

from data_utils import create_stock_price_prediction_dataset
from model_utils import create_lstm_dataset, train_lstm_model

def main(): 


    ticker = "AAPL"
    period = "6mo"
    epochs = 100


    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_tag("Stocks", f"{ticker}")
    mlflow.set_experiment(f"{ticker}")


    unique_id = uuid.uuid4().hex[:6]  # short random suffix
    run_name = f"LSTM-{ticker}-{unique_id}"

    # DONE : Start MLFlow run
    try: 
        with mlflow.start_run(run_name=run_name, nested = True) as run:
            # TODO : log parameters and metrics
            mlflow.log_param("ticker", ticker)
            mlflow.log_param("period", period)
            mlflow.log_param("epochs", epochs)
            mlflow.log_param("model_type", "LSTM")


            # TODO : Pull data from the data_utils.py file
            stock_data, label_series = create_stock_price_prediction_dataset(ticker=ticker, 
                                                                             days_to_predict=5, 
                                                                             period=period)

            # TODO : Create model via the model_utils.py file
            dataset, input_shape, output_shape = create_lstm_dataset(stock_data, label_series)

            run_id, model, final_loss = train_lstm_model(
                    dataset=dataset,
                    input_shape=input_shape,
                    output_shape=output_shape,
                    ticker=ticker,
                    epochs=epochs
                )

            # TODO : Log the model using mlflow.tensorflow.log_model
            mlflow.log_metric("final_loss", final_loss)
            mlflow.log_param("input_shape", input_shape)


            # TODO : Log the model signature using mlflow.models.infer_signature
            for x_batch, y_batch in dataset.take(1):
                x_example = x_batch.numpy()
                y_example = y_batch.numpy()
                break

            signature = infer_signature(x_example, y_example)

            mlflow.tensorflow.log_model(
                model=model,
                artifact_path="model",
                signature=signature,
                input_example=stock_data[:1]
            )

        print(f"✅ Dummy model logged with loss: {final_loss}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Shut down gracefully
        if mlflow.active_run():
            mlflow.end_run()

#def main():
#    X = np.random.randn(100, 2)
#    y = (X[:, 0] + X[:, 1] > 0).astype(int)
#    
#    model = LogisticRegression()
#    model.fit(X, y)
#    acc = model.score(X, y)
#    
#    with mlflow.start_run():
#        mlflow.log_param("model_type", "LogisticRegression")
#        mlflow.log_metric("accuracy", acc)
#        signature = infer_signature(X, model.predict(X))
#        mlflow.sklearn.log_model(model, "model", signature=signature)
#        print(f"✅ Dummy model logged with accuracy: {acc}")

if __name__ == "__main__":
    main()
