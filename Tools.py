import mplfinance as mpf
from datetime import datetime, timedelta
import pytz

def Verify_input(input):
    # Checks whether the first or last character is a letter
    if input[0].isalpha() or input[-1].isalpha():
        if "-" in input:
            output = input.replace("-", "").upper()
        elif "/" in input:
            output = input.replace("/", "").upper()
        else:
            raise ValueError("Invalid pair format. Use btc-usdt or btc/usdt format.")
    return output

def getting_some_days_data(df, days_to_plot=15):
    # Getting time zone of index
    timezone = df.index.tz
    last_15_days = (datetime.now(pytz.utc) - timedelta(days=days_to_plot)).astimezone(timezone)
    return df[df.index >= last_15_days]

"""
This function plot data
"""
def plot_data(df, info, image_name='', add_graphs=None, days_to_plot=0):
    df_filtered = df
    if days_to_plot != 0:
        df_filtered = getting_some_days_data(df, days_to_plot)

    # Configuring the chart style
    style = mpf.make_mpf_style(base_mpf_style='binance',
                               gridstyle='',
                               figcolor='white',
                               facecolor='white',
                               edgecolor='black',
                               rc={'figure.figsize': (12, 8),
                                   'savefig.dpi': 500})

    # Configuring the additional design
    kwargs = dict(
        type='candle',
        volume=True,
        title='\n' + info.get('longName', 'N/A') + ' - ' + info.get('exchange', 'N/A'),
        ylabel='price (' + info.get('currency', 'N/A') + ')',
        ylabel_lower='Volumen',
        style=style,
        panel_ratios=(3, 1),

        # Handle default for additions graphics in the chart
        addplot=add_graphs if add_graphs is not None else []
    )

    # Plot chart
    name_chart = image_name + info.get('shortName', 'N/A') + ".png"
    mpf.plot(df_filtered, **kwargs, savefig=name_chart)