import pandas as pd
import numpy as np
import yfinance as yf

def pull_stock_data(ticker, period='6mo', interval='1d'):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    df = df[['Close']].rename(columns={'Close': 'close'})
    df.index = pd.to_datetime(df.index)
    return df

def pull_vix_data(period='6mo', interval='1d'):
    vix = yf.Ticker('^VIX')
    df = vix.history(period=period, interval=interval)
    df = df[['Close']].rename(columns={'Close': 'vix_close'})
    df.index = pd.to_datetime(df.index)
    return df

def calculate_realized_volatility(df, window=20):
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['rolling_std'] = df['log_return'].rolling(window=window, min_periods=window).std()
    df['realized_volatility'] = df['rolling_std'] * np.sqrt(252)
    df = df.dropna(subset=['realized_volatility']).copy()
    return df

def generate_stock_price_prediction_dataset(
    df,
    vix_df,
    days_to_predict=5,
    lookback_days=10  # how many past closes you use
):
    features = []
    labels = []
    
    vix_df = vix_df[['vix_close']]  # Ensure only relevant column is used
    df = df.merge(vix_df, left_index=True, right_index=True, how='inner')
    df = df.dropna()  # Drop rows where VIX or volatility missing

    trading_days = df.index

    for i in range(lookback_days, len(df) - days_to_predict):
        buy_date = trading_days[i]
        S_buy = df.loc[buy_date, 'close']
        realized_vol = df.loc[buy_date, 'realized_volatility']
        vix_value = df.loc[buy_date, 'vix_close']

        # Get the next 5 closes
        S_predict_array = df.loc[trading_days[i+1:i+1+days_to_predict], 'close'].values

        # Skip if not enough future data
        if len(S_predict_array) < days_to_predict:
            continue

        if np.isnan(S_buy) or np.isnan(realized_vol) or np.isnan(vix_value) or np.any(np.isnan(S_predict_array)):
            continue

        past_closes = df.loc[trading_days[i - lookback_days:i - 1], 'close'].values

        feature_row = {
            'buy_date': buy_date,
            'current_stock_price': S_buy,
            'realized_volatility': realized_vol,
            'vix_value': vix_value,
        }

        # Add past close prices
        for j in range(lookback_days-1):
            feature_row[f'close_lag_{lookback_days-j}'] = past_closes[j]

        features.append(feature_row)
        labels.append(S_predict_array)  # target is now an array of 5 prices!

    feature_df = pd.DataFrame(features)
    label_array = np.array(labels)  # Numpy array: shape (n_samples, 5)

    return feature_df, label_array


# Full pipeline
def create_stock_price_prediction_dataset(ticker, days_to_predict=5):
    df = pull_stock_data(ticker, period='6mo', interval='1d')
    vix_df = pull_vix_data(period='6mo', interval='1d')
    df = calculate_realized_volatility(df)

    df.index = df.index.tz_localize(None)
    vix_df.index = vix_df.index.tz_localize(None)

    print(df.head())
    print(vix_df.head())
    feature_df, label_series = generate_stock_price_prediction_dataset(
        df,
        vix_df,
        days_to_predict=days_to_predict
    )
    return feature_df, label_series




import tensorflow as tf

def create_lstm_dataset(features_df, labels_array, batch_size=32, shuffle_buffer=1000):
    """
    Create a TensorFlow Dataset for LSTM input.
    
    Args:
        features_df (pd.DataFrame): Feature dataframe (n_samples, n_features).
        labels_array (np.ndarray): Label array (n_samples, 5).
        batch_size (int): Batch size for training.
        shuffle_buffer (int): Buffer size for shuffling.

    Returns:
        tf.data.Dataset: Dataset yielding (features, labels) tuples.
    """
    if len(features_df) != len(labels_array):
        raise ValueError("Features and labels must have the same number of samples.")
    
    # Take list of non-numeric columns
    non_numeric_columns = features_df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Drop non-numeric columns
    features_df = features_df.drop(columns=non_numeric_columns)

    features = features_df.to_numpy().astype('float32')
    labels = labels_array.astype('float32')

    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.shuffle(buffer_size=shuffle_buffer)
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return dataset


# Train LSTM Model:

def create_lstm_model(input_shape, output_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(output_shape)
    ])

    model.compile(optimizer='adam', loss='mse')
    return model

def train_lstm_model(dataset, input_shape, output_shape, epochs=100):
    model = create_lstm_model(input_shape, output_shape)
    model.fit(dataset, epochs=epochs)
    return model


ticker = 'AAPL'
features, labels = create_stock_price_prediction_dataset(ticker)
dataset = create_lstm_dataset(features, labels)



input_shape = (features.shape[1], 1)  # Number of features, 1 timestep
output_shape = labels.shape[1]  # Number of days to predict
lstm_model = train_lstm_model(dataset, input_shape, output_shape, epochs=120)
