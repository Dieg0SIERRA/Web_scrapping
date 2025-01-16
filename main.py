import yfinance as yf
import pandas as pd
import mplfinance as mpf
import Indicators
import Tools

def get_stock_data(stock_name):
    ticker = yf.Ticker(stock_name)

    # Getting basic information of ticker (name, stock exchange, currency)
    info = ticker.info

    # Print additional ticker information
    print("\nAdditional ticker information:")
    print(f"Sector: {info.get('sector', 'N/A')}")
    print(f"Short Name: {info.get('shortName', 'N/A')}")
    print(f"Industry: {info.get('industry', 'N/A')}")
    print(f"Country: {info.get('country', 'N/A')}")
    print(f"Market Capitalization: {info.get('marketCap', 'N/A'):,}")
    print(f"Beta: {info.get('beta', 'N/A')}")
    print(f"PE Ratio (Trailing): {info.get('trailingPE', 'N/A')}")
    print(f"52-Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"52-Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}")
    print(f"200-Day Moving Average: {info.get('twoHundredDayAverage', 'N/A')}")

    df = ticker.history(period="1mo", interval="15m")

    return df, info

def plot_data_with_indicators(df, info, days_to_plot=15):
    # Set columns names in lowercase
    df.columns = df.columns.str.lower()

    # Convert the data into a pandas DataFrame,
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    df_filtered = Tools.getting_some_days_data(df, days_to_plot)

    macd, signal, histogram = Indicators.calculate_macd(df_filtered)  # Calculate MACD
    hist_colors = ['#eb4d5c' if v < 0 else '#53b987' for v in histogram]

    # Calculate SMA
    df_filtered['MA20'] = df_filtered['close'].rolling(window=20).mean()
    df_filtered['MA50'] = df_filtered['close'].rolling(window=50).mean()

    # Calculate Bollinger Bands
    df_filtered['BB_middle'] = df_filtered['close'].rolling(window=20).mean()
    bb_std = df_filtered['close'].rolling(window=20).std()
    df_filtered['BB_upper'] = df_filtered['BB_middle'] + (bb_std * 2)
    df_filtered['BB_lower'] = df_filtered['BB_middle'] - (bb_std * 2)

    # Create additional object for indicators
    addplot = [
        mpf.make_addplot(df_filtered['MA20'], color='blue', width=0.8, label='MA20'),
        mpf.make_addplot(df_filtered['MA50'], color='red', width=0.8, label='MA50'),
        mpf.make_addplot(df_filtered['BB_upper'], color='gray', width=0.8, linestyle='--'),
        mpf.make_addplot(df_filtered['BB_lower'], color='gray', width=0.8, linestyle='--'),
        # MACD panel below volume
        mpf.make_addplot(macd, panel=2, color='#f6b900', width=0.8, ylabel='MACD'),
        mpf.make_addplot(signal, panel=2, color='#fb00ff', width=0.8),
        mpf.make_addplot(histogram, type='bar', panel=2, color=hist_colors),
    ]
    Tools.plot_data(df_filtered, info, "indicators_", addplot)


# Ejecutar el script
if __name__ == "__main__":
    stock_name = input("Enter the stock name : ").strip().lower()
    df, info = get_stock_data(stock_name)

    print("\nGenerating charts...")
    Tools.plot_data(df, info, "", None, 15)
    plot_data_with_indicators(df, info, 15)