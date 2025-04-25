import yfinance as yf
from datetime import datetime
import pandas as pd

def get_current_date():
    """
    Returns the current date in 'YYYY-MM-DD' format.
    
    Returns:
    str: Current date as a string.
    """
    return datetime.now().strftime('%Y-%m-%d')



def get_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock data from Yahoo Finance.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    start_date (str): Start date in 'YYYY-MM-DD' format.
    end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
    pd.DataFrame: DataFrame containing stock data with columns: Date, Open, High, Low, Close, Volume.
    """
    # Fetch data
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    # Reset index to have Date as a column
    stock_data.reset_index(inplace=True)
    
    # Rename columns for consistency
    stock_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    
    return stock_data



def get_stock_options_data(ticker, start_expiry_date, end_expiry_date):
    """
    Fetches detailed stock options chain data (calls & puts) from Yahoo Finance for expirations in a specific range.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    start_expiry_date (str): Start expiry date in 'YYYY-MM-DD' format.
    end_expiry_date (str): End expiry date in 'YYYY-MM-DD' format.
    
    Returns:
    pd.DataFrame: DataFrame containing combined options data (calls & puts) with relevant fields.
    """
    stock = yf.Ticker(ticker)
    all_expiries = stock.options
    
    # Filter to dates within range
    filtered_expiries = [date for date in all_expiries if start_expiry_date <= date <= end_expiry_date]
    
    options_data_list = []
    
    for expiry in filtered_expiries:
        opt_chain = stock.option_chain(expiry)
        for option_type, df in [('call', opt_chain.calls), ('put', opt_chain.puts)]:
            df = df.copy()
            df['option_type'] = option_type
            df['expiry'] = expiry
            options_data_list.append(df)
    
    if options_data_list:
        options_df = pd.concat(options_data_list, ignore_index=True)
    else:
        options_df = pd.DataFrame()
    
    return options_df


# --- Evaluation Function ---
def evaluate_option_profit(option_row, stock_close_price):
    """
    Evaluates profit for a single option contract given stock close price on expiry.
    """
    if option_row['option_type'] == 'call':
        intrinsic_value = max(stock_close_price - option_row['strike'], 0)
    else:
        intrinsic_value = max(option_row['strike'] - stock_close_price, 0)
    
    return intrinsic_value - option_row['lastPrice']


# --- Test Case Runner ---
def test_options_profit_evaluation():
    ticker = "AAPL"
    start_date = "2023-09-01"
    end_date = "2023-10-15"
    option_start = "2023-09-08"
    option_end = "2023-10-13"

    print("Fetching stock data...")
    stock_df = get_stock_data(ticker, start_date, end_date)
    
    print("Fetching options data...")
    options_df = get_stock_options_data(ticker, option_start, option_end)
    
    if stock_df.empty or options_df.empty:
        print("One of the dataframes is empty. Abort.")
        return

    # Choose a small sample of options (e.g., first 3) to display
    sample_options = options_df.head(3).copy()

    # Match stock close price on option expiry
    results = []
    for idx, row in sample_options.iterrows():
        expiry = row['expiry']
        stock_close = stock_df.loc[stock_df['Date'] == pd.to_datetime(expiry), 'Close']
        if stock_close.empty:
            print(f"No stock data for expiry {expiry}")
            continue
        stock_close_price = stock_close.values[0]
        profit = evaluate_option_profit(row, stock_close_price)
        result = {
            "expiry": expiry,
            "option_type": row['option_type'],
            "strike": row['strike'],
            "lastPrice": row['lastPrice'],
            "stock_close_price": stock_close_price,
            "profit": round(profit, 2)
        }
        results.append(result)

    result_df = pd.DataFrame(results)
    print("\nSample Option Profit Evaluation Results:")
    print(result_df)

# Run test
test_options_profit_evaluation()
