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