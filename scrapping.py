import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import time
import numpy as np

# The limit of points you can apply for is 1000 points
POINT_LIMIT = 990

# Function to calculate MACD indicator 
def calculate_macd(df):
    exp1 = df['close'].ewm(span=8, adjust=False).mean()
    exp2 = df['close'].ewm(span=21, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=5, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram
    
# Function to get historical data from Binance
def fetch_binance_data(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": POINT_LIMIT
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# Function to get the data of the last selected month or number of days
def get_last_data(symbol, interval, days_to_plot=10):
    all_klines = []
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_to_plot)

    while True:
        klines = fetch_binance_data(symbol, interval, start_time, end_time)

        # If the number of points obtained is less than <limit>, it is the last data block.
        if len(klines) < POINT_LIMIT:
            all_klines.extend(klines)
            break

        # If we get the full number of points, we set the start_time
        all_klines.extend(klines)
        start_time = datetime.utcfromtimestamp(klines[-1][0] / 1000) + timedelta(milliseconds=1)

        time.sleep(2)       # pause to avoid overloading the server.
    return all_klines

# Function for creating the candlestick chart with mplfinance
def plot_candlestick_chart(klines, title):
    days_to_plot = 10  # Modify this value to show more or less days on the graph.

    # Convert the data into a pandas DataFrame, but only use the first 6 columns
    klines = [kline[:6] for kline in klines]  # Keep only the first 6 columns

    # Converting the filtered data into a pandas DataFrame
    df = pd.DataFrame(klines, columns=["time", "open", "high", "low", "close", "volume"])

    # Convert timestamps into readable time format
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)

    # Ensure that the numerical columns are of the correct type.
    df = df.astype({
        "open": "float",
        "high": "float",
        "low": "float",
        "close": "float",
        "volume": "float"
    })

    # Limiting the amount of data to selected days
    end_time = df.index[-1]
    start_time = end_time - timedelta(days=days_to_plot)
    df = df.loc[df.index >= start_time]

    # Creating the candlestick chart
    macd, signal, histogram = calculate_macd(df)
    hist_colors = ['#eb4d5c' if v < 0 else '#53b987' for v in histogram]

    apds = [
        # MACD lines overlay on main chart
        mpf.make_addplot(macd, color='#f6b900', width=0.8),
        mpf.make_addplot(signal, color='#fb00ff', width=0.8),
        # MACD panel below volume
        mpf.make_addplot(macd, panel=2, color='#f6b900', width=0.8, ylabel='MACD'),
        mpf.make_addplot(signal, panel=2, color='#fb00ff', width=0.8),
        mpf.make_addplot(histogram, type='bar', panel=2, color=hist_colors)
    ]

    mpf.plot(df, type='candle', style='charles', title=title,
             ylabel='Price', volume=True, addplot=apds,
             panel_ratios=(2, 0.5, 1), figsize=(12, 10),
             volume_panel=1)

def Verifica_input(input):
    # Checks whether the first or last character is a letter
    if input[0].isalpha() or input[-1].isalpha():
        if "-" in input:
            output = input.replace("-", "").upper()
        elif "/" in input:
            output = input.replace("/", "").upper()
        else:
            raise ValueError("Invalid pair format. Use btc-usdt or btc/usdt format.")
    return output

def main():
    # Request user input
    pair_input = input("Enter the elements of the pair (for example, btc-usdt or ronin/usdt): ").strip().lower()
    symbol = Verifica_input(pair_input)

    interval = "1h"  # Interval for binance chart (1m, 5m, 15m, 1h, 4h, ....)
    days_to_plot = 30   # Number of days to be charted

    try:
        print(f"\nRecovering data for the pair {pair_input} (last {days_to_plot} days, interval: {interval})...\n")
        klines = get_last_data(symbol, interval, days_to_plot)
        
        # Display candlestick chart
        plot_candlestick_chart(klines,
                               f"Candlestick Chart with MACD - {pair_input} (last {days_to_plot} days, interval: {interval})")
    except requests.exceptions.RequestException as e:
        print(f"Error getting data for the pair {pair_input}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
