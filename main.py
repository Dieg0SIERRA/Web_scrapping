import yfinance as yf
import pandas as pd
import mplfinance as mpf
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


def plot_stock_data(df, info):
    # Configuring the chart style
    style = mpf.make_mpf_style(base_mpf_style='binance',
                               gridstyle='',
                               figcolor='white',
                               facecolor='white',
                               edgecolor='black',
                               rc={'figure.figsize': (12, 8)})

    # Configuring the additional design
    kwargs = dict(
        type='candle',
        volume=True,
        title='\n'+info.get('longName', 'N/A') + ' - ' + info.get('exchange', 'N/A'),
        ylabel='price ('+ info.get('currency', 'N/A')+')',
        ylabel_lower='Volumen',
        style=style,
        panel_ratios=(3, 1)
    )

    # Plot chart
    mpf.plot(df, **kwargs, savefig='stm_paris_chart.png')


def plot_stock_data_with_indicators(df, info):
    # Set columns names in lowercase
    df.columns = df.columns.str.lower()

    # Convert the data into a pandas DataFrame,
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    macd, signal, histogram = Indicators.calculate_macd(df)  # Calculate MACD
    hist_colors = ['#eb4d5c' if v < 0 else '#53b987' for v in histogram]

    # Calculate SMA
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()

    # Calculate Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

    # Create additional object for indicators
    addplot = [
        mpf.make_addplot(df['MA20'], color='blue', width=0.8, label='MA20'),
        mpf.make_addplot(df['MA50'], color='red', width=0.8, label='MA50'),
        mpf.make_addplot(df['BB_upper'], color='gray', width=0.8, linestyle='--'),
        mpf.make_addplot(df['BB_lower'], color='gray', width=0.8, linestyle='--'),
        # MACD panel below volume
        mpf.make_addplot(macd, panel=2, color='#f6b900', width=0.8, ylabel='MACD'),
        mpf.make_addplot(signal, panel=2, color='#fb00ff', width=0.8),
        mpf.make_addplot(histogram, type='bar', panel=2, color=hist_colors),
    ]

    # Configuring the chart style
    style = mpf.make_mpf_style(base_mpf_style='charles',
                               gridstyle='',
                               figcolor='white',
                               facecolor='white',
                               edgecolor='black',
                               rc={'figure.figsize': (12, 8)})

    # Configuring the additional design
    kwargs = dict(
        type='candle',
        volume=True,
        title='\n' + info.get('longName', 'N/A') + ' - ' + info.get('exchange', 'N/A') + ' Indicators',
        ylabel='price (' + info.get('currency', 'N/A') + ')',
        ylabel_lower='Volumen',
        style=style,
        panel_ratios=(3, 1),
        addplot=addplot
    )
    mpf.plot(df, **kwargs, savefig='stm_paris_chart_with_indicators.png')


# Ejecutar el script
if __name__ == "__main__":
    stock_name = input("Enter the stock name : ").strip().lower()
    df, info = get_stock_data(stock_name)

    print("\nGenerating charts...")
    plot_stock_data(df, info)
    plot_stock_data_with_indicators(df, info)