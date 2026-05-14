# Description: Short example for Visualization and Interpretation of Time Series Data in Econometric Analysis.


# Required Libraries

# Set Global Matplotlib Style

from matplotlib.ticker import FuncFormatter
from pandas_datareader import data as web
import signalplot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

signalplot.apply(font_family='serif')

# Function to Set Plot Style
def set_plot_style(ax, df, time_column, value_columns):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("outward", 5))
    ax.spines["bottom"].set_position(("outward", 5))

    # X-Axis: Use 50-year intervals
    years = pd.to_datetime(df[time_column]).dt.year
    x_min, x_max = years.min(), years.max()
    x_start = (x_min // 50) * 50
    x_ticks = np.arange(x_start, x_max + 1, 50)
    if x_max not in x_ticks:
        x_ticks = np.append(x_ticks, x_max)

    ax.set_xticks(x_ticks)
    ax.set_xlim(x_start, x_max)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x)}"))

    # Y-Axis: Compute mean, 20%, and 80% dynamically
    all_values = np.concatenate([df[col].dropna().values for col in value_columns])
    y_20, y_mean, y_80 = np.percentile(all_values, [20, 50, 80])
    ax.set_yticks([y_20, y_mean, y_80])
    ax.set_yticklabels([f"{y_20:.2e}", f"{y_mean:.2e}", f"{y_80:.2e}"])

# Function to Plot Time Series
def plot_time_series(df, time_column=None, value_columns=None, title=None, filename=None, plot: bool = False):
    if time_column is None:
        time_column = next((col for col in df.columns if df[col].dtype == "datetime64[ns]"), None)
    if time_column is None:
        raise ValueError("No datetime column found.")

    if isinstance(value_columns, str):
        value_columns = [value_columns]
    if value_columns is None:
        value_columns = df.select_dtypes(include="number").columns.tolist()
    if not value_columns:
        raise ValueError("No numeric columns found to plot.")

    if plot:
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Greys(np.linspace(0.2, 0.8, len(value_columns)))
        for i, col in enumerate(value_columns):
            ax.plot(df[time_column].dt.year, df[col], linewidth=2, color=colors[i])
            last_x = df[time_column].dt.year.iloc[-1] + (df[time_column].dt.year.max() - df[time_column].dt.year.min()) * 0.02
            last_y = df[col].iloc[-1]
            ax.text(last_x, last_y, col, fontsize=12, color=colors[i], verticalalignment="center")

        set_plot_style(ax, df, time_column, value_columns)

        ax.set_xlabel("Year")
        ax.set_ylabel("GDP (Billions of Dollars)")
        if title:
            ax.set_title(title)

        if filename:
            plt.savefig(filename, dpi=300, bbox_inches="tight")

        plt.show()

# Load GDP Data from FRED
start = '2000-01-01'
end = '2025-02-20'
gdp = web.DataReader('GDP', 'fred', start, end)

# Combine Data into a Single DataFrame
df = pd.DataFrame({
    'Date': gdp.index,
    'GDP': gdp['GDP']
})
df['Date'] = pd.to_datetime(df['Date'])

# Calculate the Moving Average (12-Quarter Rolling Average)
df['Moving_Avg'] = df['GDP'].rolling(window=12).mean()

# Plot Time Series with Moving Average
plot_time_series(df, 
                 time_column='Date', 
                 value_columns=['GDP', 'Moving_Avg'], 
                 title='GDP with 12-Quarter Moving Average', 
                 filename='gdp_moving_average.png')
