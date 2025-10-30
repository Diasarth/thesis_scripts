import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from scipy.stats import t

# Load data from CSV
df = pd.read_csv('D:/Data/SP/FNR/FNRxProbO3.csv', sep=';', encoding='utf-8')

# Font configuration
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path, size=18)
font_prop_title = font_manager.FontProperties(fname=font_path, size=25)

# Variables
x = df.iloc[:, 0].values  # FNR (HCHO/NO2)
y = df.iloc[:, 1].values  # Ozone exceedance probability (%)

# Fit a third-degree polynomial
coef = np.polyfit(x, y, 3)  # Polynomial coefficients
poly = np.poly1d(coef)      # Create polynomial function

# Generate smoothed curve values
x_fit = np.linspace(min(x), max(x), 200)
y_fit = poly(x_fit)

# Find the peak of the curve
x_peak = x_fit[np.argmax(y_fit)]
y_peak = max(y_fit)

# Compute predicted (fitted) y values for the original x
y_pred = poly(x)

# Compute correlation coefficient (R) between fitted and real y values
r_value = np.corrcoef(y, y_pred)[0, 1]

# Compute standard error of prediction
n = len(x)
p = len(coef)
residuals = y - poly(x)
stderr = np.std(residuals)       # Standard deviation of residuals
t_value = t.ppf(0.975, df=n - p) # t-value for 95% confidence interval

# Compute confidence interval
delta_y = t_value * stderr * np.sqrt(1/n + (x_fit - np.mean(x))**2 / np.sum((x - np.mean(x))**2))
y_upper = y_fit + delta_y
y_lower = y_fit - delta_y

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 5))

# Add title "(b)"
ax.set_title('( b )', fontproperties=font_prop_title, loc='left', pad=20)

# Scatter plot
ax.scatter(x, y, color='black', s=30)

# Polynomial curve
ax.plot(x_fit, y_fit, color='red', linewidth=3)

# 95% confidence interval shading
ax.fill_between(x_fit, y_lower, y_upper, color='black', edgecolor='none', alpha=0.1)

# Vertical line at the curve peak
ax.axvline(x_peak, color='darkred', linestyle='-', linewidth=2)

# Highlight uncertainty region
ax.fill_betweenx([0, 0.4], x_peak - 0.4, x_peak + 0.4, color='red', edgecolor='none', alpha=0.2)

# Axis labels
ax.set_xlabel('TROPOMI FNR (HCHO/NO$_2$)', fontsize=16, fontproperties=font_prop)
ax.set_ylabel('Ozone exceedance probability', fontsize=16, fontproperties=font_prop)

# Add text box in the upper-right corner
text_str = f'1.98 ( 1.6 ~ 2.4 )\nR = {r_value:.2f}'
ax.text(
    0.95, 0.92, text_str,
    transform=ax.transAxes,
    ha='right', va='top',
    fontsize=20,
    fontproperties=font_prop,
    linespacing=1.5,
    bbox=dict(facecolor='white', edgecolor='white', boxstyle='round, pad=0.5')
)

# Axis limits
ax.set_xlim(0, 6)
ax.set_ylim(0, 0.4)

# Set font for axis tick labels
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)

# Define tick locations
ax.set_xticks(np.arange(0, 7, 1))
ax.set_yticks(np.arange(0, 0.5, 0.1))

# Format Y-axis as percentages
formatter = FuncFormatter(lambda y, _: f'{int(y * 100)}%')
ax.yaxis.set_major_formatter(formatter)

# Adjust tick appearance
ax.tick_params(axis='both', labelsize=16, width=1.5)

# Improve layout and borders
for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Save figure
plt.savefig("D:/Data/SP/FNR/FNRxProbO3.svg", format='svg', bbox_inches='tight', dpi=300)
plt.savefig("D:/Data/SP/FNR/FNRxProbO3.png", format='png', bbox_inches='tight', dpi=300)

# Show plot
plt.show()
