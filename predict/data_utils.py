import pandas as pd
import numpy as np
import yfinance as yf

def pull_stock_data(ticker, period='6mo', interval='1d'):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    print(f"Pulling data for {ticker}...")
    df = df[['Close']].rename(columns={'Close': 'close'})
    df.index = pd.to_datetime(df.index)
    print(f"Data head (Pull Stock Data): {df.head()}")
    print(f"Data shape: {df.shape}")
    print(f"Data columns: {df.columns}")
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
def create_stock_price_prediction_dataset(ticker, days_to_predict=5, period='6mo'):
    df = pull_stock_data(ticker, period=period, interval='1d')
    vix_df = pull_vix_data(period=period, interval='1d')
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

    print(f"Feature DataFrame shape: {feature_df.shape}")
    print(f"Label Series shape: {label_series.shape}")
    print(f"Feature Dataframe: {feature_df.head()}")

    return feature_df, label_series


def prepare_latest_input(ticker, lookback_days=10):
    # Pull last month of data to ensure sufficient window
    df = pull_stock_data(ticker, period='1mo', interval='1d')
    vix_df = pull_vix_data(period='1mo', interval='1d')

    # Calculate volatility
    df = calculate_realized_volatility(df, window=lookback_days)

    # Remove timezones for merging
    df.index = df.index.tz_localize(None)
    vix_df.index = vix_df.index.tz_localize(None)

    # Merge with VIX and drop missing values
    vix_df = vix_df[['vix_close']]
    df = df.merge(vix_df, left_index=True, right_index=True, how='inner')
    df = df.dropna()

    # Sanity check
    if len(df) < lookback_days:
        raise ValueError(f"Not enough data: need at least {lookback_days} rows, got {len(df)}")

    # Take the most recent date
    latest_row = df.iloc[-1]
    buy_date = df.index[-1]
    S_buy = latest_row['close']
    realized_vol = latest_row['realized_volatility']
    vix_value = latest_row['vix_close']

    # Get past closes (excluding today’s close)
    past_closes = df['close'].iloc[-lookback_days:-1].values

    feature_row = {
        'buy_date': buy_date,
        'current_stock_price': S_buy,
        'realized_volatility': realized_vol,
        'vix_value': vix_value,
    }

    # Add lagged close features
    for j in range(lookback_days - 1):
        feature_row[f'close_lag_{lookback_days - j}'] = past_closes[j]

    feature_df = pd.DataFrame([feature_row])
    return feature_df
