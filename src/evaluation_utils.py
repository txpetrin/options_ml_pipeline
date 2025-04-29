import mlflow

def evaluate_and_promote_model(model_path):
    client = mlflow.tracking.MlflowClient()
    current_run = mlflow.active_run()
    current_run_id = current_run.info.run_id
    current_loss = mlflow.active_run().data.metrics.get('final_loss')
    ticker = mlflow.active_run().data.params.get('ticker')
    experiment_id = current_run.info.experiment_id

    print(f"[INFO] Evaluating promotion for {ticker} run {current_run_id} with loss {current_loss}")

    if not ticker:
        raise ValueError("Ticker not found in MLflow params. Cannot stratify evaluation.")

    # Find all previous runs for the same ticker
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"params.ticker = '{ticker}'",   # <-- Only same ticker
        order_by=["metrics.final_loss ASC"],
        max_results=1
    )

    if runs:
        best_previous_run = runs[0]
        best_previous_loss = best_previous_run.data.metrics.get('final_loss')
        best_previous_run_id = best_previous_run.info.run_id

        print(f"[INFO] Best previous {ticker} run: {best_previous_run_id} with loss {best_previous_loss}")

        if best_previous_run_id != current_run_id:
            if current_loss is not None and (best_previous_loss is None or current_loss < best_previous_loss):
                print(f"[PROMOTION] New {ticker} model is better! Updating best model tag.")

                # Set best_model_<ticker>=true on current run
                client.set_tag(current_run_id, f"best_model_{ticker}", "true")

                # Unset the tag on old best run
                client.set_tag(best_previous_run_id, f"best_model_{ticker}", "false")
            else:
                print(f"[NO PROMOTION] Current model not better for {ticker}.")
        else:
            print(f"[INFO] Current run already best for {ticker}.")
    else:
        # No previous runs, so by default it's the best
        print(f"[PROMOTION] First {ticker} model logged, marking as best.")
        client.set_tag(current_run_id, f"best_model_{ticker}", "true")
