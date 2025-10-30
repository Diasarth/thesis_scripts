import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from matplotlib import font_manager
from scipy.interpolate import make_interp_spline

# Load CSV file
data = pd.read_csv('D:/Data/FR/FNR/Trends_2019_2023.csv', sep=';', encoding='utf-8')

# Font configuration
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path, size=14)
font_prop_large = font_manager.FontProperties(fname=font_path, size=16)
font_prop_title = font_manager.FontProperties(fname=font_path2, size=15)

# Create separate columns for year and season
data[['Year', 'Season_Name']] = data['Season'].str.split(' ', expand=True)

# Convert year to integer
data['Year'] = data['Year'].astype(int)

# Map seasons to x-axis offsets (small shifts to separate them visually)
season_to_offset = {'Summer': 0, 'Autumn': 0.25, 'Winter': 0.5, 'Spring': 0.75}
data['x_index'] = data['Year'] + data['Season_Name'].map(season_to_offset)

# Convert numeric columns and handle errors
numeric_cols = [
    'Urban_HCHO_Mean', 'Urban_HCHO_SD', 
    'Transition_HCHO_Mean', 'Transition_HCHO_SD', 
    'Forest_HCHO_Mean', 'Forest_HCHO_SD',
    'Urban_NO2_Mean', 'Urban_NO2_SD', 
    'Transition_NO2_Mean', 'Transition_NO2_SD',
    'Forest_NO2_Mean', 'Forest_NO2_SD'
]

for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Function to plot trend for each category
def plot_trend(ax, x, y, yerr, label, color, ylabel):
    ax.errorbar(x, y, yerr=yerr, fmt='o', color=color, ecolor=color, capsize=0, markersize=5)
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    trend_line = slope * np.array(x) + intercept
    ax.plot(x, trend_line, color='black', linestyle='-', linewidth=2)
    slope_per_year = slope * 1e-15
    
    # Compute average value
    avg_value = np.nanmean(y) * 1e-15  # Convert to units of 10^15 molec cm^-2
    
    # Add text labels
    ax.text(0.015, 0.75, f"{label.upper()}",
            transform=ax.transAxes,
            fontproperties=font_prop_title)
    
    ax.text(0.015 + 0.31, 0.75,
            f"Average: {avg_value:.1f}  |  Linear trend: {slope_per_year:.3f} "
            "(10$^{15}$ molec cm$^{-2}$ year$^{-1}$)",
            transform=ax.transAxes,
            fontproperties=font_prop)
    
    ax.set_ylabel(ylabel, fontproperties=font_prop_large)
    ax.ticklabel_format(axis='y', style='plain')
    
    # Create smooth shading between error bounds
    x_smooth = np.linspace(min(x), max(x), 300)
    spline_upper = make_interp_spline(x, y + yerr)(x_smooth)
    spline_lower = make_interp_spline(x, y - yerr)(x_smooth)
    ax.fill_between(x_smooth, spline_lower, spline_upper, facecolor=color, alpha=0.2, edgecolor='none')
    
    # Style axis spines
    for spine in ['left', 'right', 'top', 'bottom']:
        ax.spines[spine].set_linewidth(1.5)
    
    # Style tick parameters
    ax.tick_params(axis='y', labelsize=15, width=1.5)

# Create figure and axes
fig, axes = plt.subplots(6, 1, figsize=(10, 9), sharex=True)
axes = axes.flatten()

# Data categories to plot (order adjusted)
categories = [
    ('Urban_HCHO_Mean', 'Urban_HCHO_SD', 'Urban', 'red', ' '),
    ('Transition_HCHO_Mean', 'Transition_HCHO_SD', 'Transition', 'dodgerblue', 'HCHO (10$^{15}$ molec cm$^{-2}$)'),
    ('Forest_HCHO_Mean', 'Forest_HCHO_SD', 'Forest', 'goldenrod', ' '),
    ('Urban_NO2_Mean', 'Urban_NO2_SD', 'Urban', 'red', ' '),
    ('Transition_NO2_Mean', 'Transition_NO2_SD', 'Transition', 'dodgerblue', 'NO$_{2}$ (10$^{15}$ molec cm$^{-2}$)'),
    ('Forest_NO2_Mean', 'Forest_NO2_SD', 'Forest', 'goldenrod', ' ')
]

# Plot each category
for i, (mean_col, sd_col, label, color, ylabel) in enumerate(categories):
    ax = axes[i]
    plot_trend(ax, data['x_index'], data[mean_col], data[sd_col], label, color, ylabel)
    
    # Add vertical lines to separate specific years
    for year in [2020, 2021, 2022, 2023]:
        ax.axvline(year - 0.125, color='#D3D3D3', linewidth=1, linestyle='--', zorder=0)

# Adjust y-axis limits
y_min_1 = 4e15
y_max_1 = 13e15
for ax in axes[:3]:
    ax.set_ylim(y_min_1, y_max_1)
    ax.yaxis.set_ticks(np.arange(y_min_1 + 1e15, y_max_1 + 1e15, 3e15))

y_min_2 = 0
y_max_2 = 16e15
for ax in axes[3:]:
    ax.set_ylim(y_min_2, y_max_2)
    ax.yaxis.set_ticks(np.arange(y_min_2, y_max_2 + 1e15, 6e15))
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_prop)

# Customize x-axis to show centered year labels
unique_years = sorted(data['Year'].unique())
x_ticks_positions = [year + 0.375 for year in unique_years]

for ax in axes:
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', labelsize=13)
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_prop)

plt.xticks(x_ticks_positions, unique_years, fontsize=14)

# Format y-axis labels (convert to 10^15)
def format_y_ticks(y, pos):
    if y >= 1e15:
        return f'{y/1e15:.0f}'
    return f'{y:.0f}'

for ax in axes:
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y_ticks))
    
plt.subplots_adjust(hspace=0.07)

# Save figure
plt.savefig("D:/Data/FR/FNR/Trends_2019_2023.svg", format='svg', bbox_inches='tight', dpi=300)
plt.savefig("D:/Data/FR/FNR/Trends_2019_2023.png", format='png', bbox_inches='tight', dpi=300)

# Show plot
plt.show()
