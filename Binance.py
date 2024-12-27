import requests
import time
from datetime import datetime, timedelta

# Constants

# The limit of points you can apply for is 1000 points
POINT_LIMIT = 990

# Function to retrieve Binance history
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

# Function to get range data
def get_data_from_binance(symbol, interval, start_time, end_time):
    all_klines = []

    while True:
        klines = fetch_binance_data(symbol, interval, start_time, end_time)

        # If the number of points obtained is less than <limit>, it is the last data block.
        if len(klines) < POINT_LIMIT:
            all_klines.extend(klines)
            break

        # If we get the full number of points, we set the startTime
        all_klines.extend(klines)
        start_time = datetime.utcfromtimestamp(klines[-1][0] / 1000) + timedelta(milliseconds=1)

        time.sleep(2)       # pause to avoid overloading the server.
    return all_klines


def calculate_macd(df):
    fast_ema = 8
    slow_ema = 12
    signal_period = 5
    exp1 = df['close'].ewm(span=fast_ema, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow_ema, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram