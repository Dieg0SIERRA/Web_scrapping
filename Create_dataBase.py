import sqlite3
from datetime import datetime, timedelta
import requests
import time
from datetime import datetime
import mplfinance as mpf
import pandas as pd

# Create the SQLite database
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_data (
            time INTEGER PRIMARY KEY,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL
        )
    """)
    conn.commit()
    conn.close()

# Saving data in the database
def save_to_database(db_name, klines):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for kline in klines:
        cursor.execute("""
            INSERT OR IGNORE INTO historical_data (time, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(kline[0]),
            float(kline[1]),
            float(kline[2]),
            float(kline[3]),
            float(kline[4]),
            float(kline[5])
        ))
    conn.commit()
    conn.close()

"""
    Retrieves klines from the SQLite database within the specified range.

    Parameters:
        db_name (str): Name of the SQLite database file.
        par (str): Cryptocurrency pair (example: BTCUSDT).
        temporality (str): Temporality of the interval (example: ‘1m’, ‘5m’, ‘1h’, etc.).
        time_start (str): Start date in ‘dd/mm/yyyy’ format.
        time_end (str): End date in ‘dd/mm/yyyy’ format.

    Return:
        list: List of klines in the format [(time, open, high, low, close, volume), ...].
"""
def get_klines_from_db(db_name, time_start, time_end):
    # Convertir las fechas al formato timestamp en milisegundos
    start_timestamp = int(datetime.strptime(time_start, "%d/%m/%Y").timestamp() * 1000)
    end_timestamp = int(datetime.strptime(time_end, "%d/%m/%Y").timestamp() * 1000)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Recuperar los datos dentro del rango de tiempo
    cursor.execute("""
        SELECT time, open, high, low, close, volume
        FROM historical_data
        WHERE time >= ? AND time <= ?
        ORDER BY time ASC
    """, (start_timestamp, end_timestamp))

    # Obtener los resultados
    klines = cursor.fetchall()

    conn.close()
    return klines

"""
Muestra un gráfico de velas a partir de los datos proporcionados.

Parámetros:
    klines (list): Lista de klines en formato [(time, open, high, low, close, volume), ...].
    titulo (str): Título para el gráfico.
    limite_puntos (int): Número máximo de puntos a graficar. Si es 0, se grafican todos los puntos.
"""
def show_graphic_candles(klines, titleName, pointLimit=0):
    # Converting the data into a pandas DataFrame
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

    # Limit the points if the limit is defined and is greater than 0
    if pointLimit > 0:
        df = df.iloc[-pointLimit:]

    # Configuring the chart with mplfinance
    mpf.plot(df, type="candle", style="binance", title=titleName, ylabel="Precio", ylabel_lower="Volumen", volume=True)
    print(f"{len(df)} points were plotted.")

# Get the last stored timestamp
def get_last_timestamp(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(time) FROM historical_data
    """)
    result = cursor.fetchone()[0]
    conn.close()
    return result

# Function to retrieve Binance history
def fetch_binance_data(symbol, interval, start_time, end_time, limit=980):
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

# Function to synchronise historical data
def sync_data(db_name, symbol, interval, limitDate):
    pointLimit = 980  # The limit of points you can apply for is 1000 points
    end_date = datetime.strptime(limitDate, "%d/%m/%Y")
    create_database(db_name)
    last_timestamp = get_last_timestamp(db_name)

    if last_timestamp is None:
        start_time = datetime(2017, 1, 1)  # Default date for old pairs
    else:
        start_time = datetime.utcfromtimestamp(last_timestamp / 1000) + timedelta(milliseconds=1)

    while start_time < end_date:
        klines = fetch_binance_data(symbol, interval, start_time, end_date, pointLimit)
        save_to_database(db_name, klines)

        last_timestamp = klines[-1][0]
        start_time = datetime.utcfromtimestamp(last_timestamp / 1000) + timedelta(milliseconds=1)

        if len(klines) < pointLimit:
            break
        time.sleep(2)

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

    db_name = "ronin-usdt.db"
    interval = "1m"
    time_start = "8/02/2024"
    time_end = "9/02/2024"
    numbPointsChart = 500
    days_to_plot = 1
    try:
        sync_data(db_name, symbol, interval, "10/02/2024")
        klines = get_klines_from_db(db_name, time_start, time_end)

        show_graphic_candles(klines, f"candlestick chart for {symbol} ({time_start} a {time_end})", numbPointsChart)

    except requests.exceptions.RequestException as e:
        print(f"Error getting data for the pair {pair_input}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
