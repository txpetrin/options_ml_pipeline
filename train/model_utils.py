import tensorflow as tf
import numpy as np
import datetime
import os

def create_lstm_dataset(features_df, labels_array, batch_size=32, shuffle_buffer=1000):
    """
    Create a TensorFlow Dataset for LSTM input.
    
    Args:
        features_df (pd.DataFrame): Feature dataframe (n_samples, n_features).
        labels_array (np.ndarray): Label array (n_samples, 5).
        batch_size (int): Batch size for training.
        shuffle_buffer (int): Buffer size for shuffling.

    Returns:
        tf.data.Dataset: A TensorFlow Dataset object.
        int: Input shape for the LSTM model.
        int: Output shape for the LSTM model.
    """
    if len(features_df) != len(labels_array):
        raise ValueError("Features and labels must have the same number of samples.")
    
    # Take list of non-numeric columns
    non_numeric_columns = features_df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Drop non-numeric columns
    features_df = features_df.drop(columns=non_numeric_columns)

    features = features_df.to_numpy().astype('float32')
    features = features.reshape((features.shape[0], 1, features.shape[1]))  # Add time step dim
    labels = labels_array.astype('float32')

    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.shuffle(buffer_size=shuffle_buffer)
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return dataset, features.shape[1:], labels.shape[1]



def create_lstm_model(input_shape, output_shape):
    """ Create a simple LSTM model for time series prediction. """

    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(output_shape)
    ])

    model.compile(optimizer='adam', loss='mse')
    return model



def train_lstm_model(dataset, input_shape, output_shape, epochs=100, ticker="AAPL", save_dir="models"):	
    model = create_lstm_model(input_shape, output_shape)

    history = model.fit(dataset, epochs=epochs, verbose=1)
    final_loss = float(history.history['loss'][-1])

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime(f"{ticker}_%Y%m%dT%H%M%S")

    # Return metadata
    return run_id, model, final_loss