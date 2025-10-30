import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline
from matplotlib import font_manager
import os

# Fonts
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path, size=18)
font_prop_black = font_manager.FontProperties(fname=font_path2, size=18)

# Conversion factor: mol/m² → molecules/cm²
conversion_factor = 6.02214e19

# CSV file
csv_path = 'D:/Results/Dataframes/FR/FR_HCHO.csv'
df = pd.read_csv(csv_path, parse_dates=['day'])
output_dir = os.path.dirname(csv_path)

# Convert units
areas = df.columns[1:]
df[areas] = df[areas] * conversion_factor

# Year, month, season
df['Year'] = df['day'].dt.year
df['Month'] = df['day'].dt.month

def get_season(month):
    if month in [1, 2, 3]: return 'Winter'
    elif month in [4, 5, 6]: return 'Spring'
    elif month in [7, 8, 9]: return 'Summer'
    else: return 'Autumn'

df['Season'] = df['Month'].apply(get_season)

# Grouping
season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
df['Season'] = pd.Categorical(df['Season'], categories=season_order, ordered=True)
seasonal = df.groupby('Season')[areas].agg(['mean', 'std']).reset_index()
seasonal.columns = ['Season'] + [f'{area}_{stat}' for area in areas for stat in ['mean', 'std']]

# Colors
color = '#1E40AF'
error_color = '#444444'

# Create figure
fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True)
axes = axes.flatten()

# Y-axis limits
y_min = 0
y_max = 27e15

# Function to plot each area
def plot_area(ax, area, show_y_ticks=True):
    x = np.arange(len(season_order))
    y = seasonal[f'{area}_mean'].values
    yerr = seasonal[f'{area}_std'].values

    mask = ~np.isnan(y) & ~np.isnan(yerr)
    x, y, yerr = x[mask], y[mask], yerr[mask]

    # Smoothed line
    if len(x) >= 4:
        x_smooth = np.linspace(x.min(), x.max(), 300)
        y_smooth = make_interp_spline(x, y)(x_smooth)
        ax.plot(x_smooth, y_smooth, linestyle='-', color=color, linewidth=3)

    # Points and error bars
    ax.errorbar(x, y, yerr=yerr, fmt='o', color=color, ecolor=error_color,
                capsize=0, markersize=8, zorder=3)

    # Shaded area for standard deviation
    if len(x) >= 4:
        upper_spline = make_interp_spline(x, y + yerr)(x_smooth)
        lower_spline = make_interp_spline(x, y - yerr)(x_smooth)
        ax.fill_between(x_smooth, lower_spline, upper_spline, color=color, alpha=0.2)

    # Statistics
    avg = np.nanmean(y) / 1e15
    sd = np.nanmean(yerr) / 1e15

    x_trend = df['day'].map(pd.Timestamp.toordinal)
    y_trend = df[area]
    mask_trend = ~np.isnan(y_trend)
    slope, _, _, _, _ = linregress(x_trend[mask_trend], y_trend[mask_trend])
    slope_per_year = slope * 365.25 / 1e15

    # Title and labels
    label_clean = area.replace('_', ' ')
    ax.text(0.04, 0.88, label_clean, transform=ax.transAxes, fontproperties=font_prop_black)
    ax.text(0.04, 0.78, rf'Average: {avg:.1f} ± {sd:.1f}',
            transform=ax.transAxes, fontsize=18, fontproperties=font_prop)
    ax.text(0.04, 0.68, rf'Annual trend: {slope_per_year:.3f}',
            transform=ax.transAxes, fontsize=18, fontproperties=font_prop)

    # Y-axis
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(np.arange(y_min, y_max, 7e15))
    if show_y_ticks:
        ax.tick_params(axis='y', labelsize=11, width=2)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y / 1e15:.0f}'))
        for label in ax.get_yticklabels():
            label.set_fontproperties(font_prop)
    else:
        ax.set_yticklabels([])
        ax.set_yticks([])

    # X-axis
    ax.set_xticks(np.arange(len(season_order)))
    ax.set_xticklabels(season_order, fontsize=11, fontproperties=font_prop)
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.set_xlim(-0.4, len(season_order) - 0.65)

    # Axes borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_linewidth(2)

# Plot all areas
for i, area in enumerate(areas):
    show_y = (i % 3 == 0)  # Show Y ticks only in the first column
    plot_area(axes[i], area, show_y_ticks=show_y)

# Common Y-axis label
fig.text(0.04, 0.5, 'HCHO (10$^{15}$ molec cm$^{-2}$)', va='center', rotation='vertical',
         fontsize=22, fontproperties=font_prop)

# Adjust spacing between subplots
fig.subplots_adjust(left=0.095, right=0.98, top=0.98, bottom=0.08, wspace=0.04, hspace=0.05)

# Paths to save figure
svg_path = os.path.join(output_dir, 'FR_HCHO_SeasonalAvg_Grid.svg')
png_path = os.path.join(output_dir, 'FR_HCHO_SeasonalAvg_Grid.png')

# Save figure
plt.savefig(svg_path, format='svg', bbox_inches='tight', dpi=300)
plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

# Show plot
plt.show()