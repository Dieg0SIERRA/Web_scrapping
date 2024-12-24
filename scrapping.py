import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import time

# Function to get historical data from Binance
def fetch_binance_klines(symbol, interval, start_time, end_time, limit):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": limit
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
        limit = 980  # The limit of points you can apply for is 1000 points
        klines = fetch_binance_klines(symbol, interval, start_time, end_time, limit)

        # If the number of points obtained is less than <limit>, it is the last data block.
        if len(klines) < limit:
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

    # Convert data to a DataFrame suitable for mplfinance
    df = pd.DataFrame(klines,
                      columns=["Time", "Open", "High", "Low", "Close", "Volume"] + [f"Extra{i}" for i in range(6)])
    df = df[["Time", "Open", "High", "Low", "Close", "Volume"]]
    df["Time"] = pd.to_datetime(df["Time"], unit="ms")
    df.set_index("Time", inplace=True)
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    # Limiting the amount of data to selected days
    end_time = df.index[-1]
    start_time = end_time - timedelta(days=days_to_plot)
    df = df.loc[df.index >= start_time]

    # Creating the candlestick chart
    mpf.plot(df, type='candle', style='charles', title=title, ylabel='Precio', ylabel_lower='Volumen', volume=True)

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
        plot_candlestick_chart(klines, f"candlestick chart {pair_input} (las {days_to_plot} days, interval: {interval})")
    except requests.exceptions.RequestException as e:
        print(f"Error getting data for the pair {pair_input}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
