import Binance
import Tools
import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Function to get the data of the last selected month or number of days
def get_last_data(symbol, interval, days_to_plot=10):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_to_plot)

    return Binance.get_data_from_binance(symbol, interval, start_time, end_time)

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

    macd, signal, histogram = Binance.calculate_macd(df) # Calculate MACD
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

    # Creating the candlestick chart, with MACD
    image_path = "C:/Users/diego.sierra/Documents/Varios/lukencios-py/chart.png"
    fig, axlist = mpf.plot(df, type='candle', style='binance', title=title, ylabel='Price', ylabel_lower='Volume',
                           volume=True, returnfig=True, addplot=apds, panel_ratios=(2, 0.5, 1), figsize=(12, 10),
                           volume_panel=1)
    fig.set_dpi(300)  # Increase DPI to improve quality
    plt.savefig("chart.png", dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)

def main():
    # Request user input
    pair_input = input("Enter the elements of the pair (for example, btc-usdt or ronin/usdt): ").strip().lower()
    symbol = Tools.Verify_input(pair_input)

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
