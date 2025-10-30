import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

# Load data from CSV
df = pd.read_csv('D:/Data/FR/FNR/HCHOxNO2xO3.csv', sep=';', encoding='utf-8')

# Font configuration
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path, size=18)
font_prop_title = font_manager.FontProperties(fname=font_path, size=25)

# Create figure and axes
fig, ax = plt.subplots(figsize=(8, 5))

# Add subplot title "(a)"
ax.set_title('( a )', fontproperties=font_prop_title, loc='left', pad=20)

# Scatter plot with color based on O3 values
sc = ax.scatter(
    df['HCHO'], df['NO2'], 
    c=df['O3'], cmap='Spectral_r', edgecolors='none', s=50, vmin=50, vmax=130
)
# Alternative: hexbin plot
# sc = ax.hexbin(df['HCHO'], df['NO2'], C=df['O3'], gridsize=100, cmap='Spectral_r', 
#                edgecolors='none', reduce_C_function=np.mean, vmin=20, vmax=130)

# Add colorbar
cbar = plt.colorbar(sc, ax=ax, label=r'O$_3$ ($\mathrm{\mu}$g m$^{-3}$)')
cbar.ax.yaxis.label.set_fontproperties(font_prop)
cbar.outline.set_linewidth(1.5)
cbar.ax.tick_params(labelsize=16, width=1.5)

# Apply font to colorbar ticks
for label in cbar.ax.get_yticklabels():
    label.set_fontproperties(font_prop)

# Axis labels
ax.set_xlabel('HCHO ($10^{15}$ molecules cm$^{-2}$)', fontproperties=font_prop)
ax.set_ylabel('NO$_2$ ($10^{15}$ molecules cm$^{-2}$)', fontproperties=font_prop)

# Set axis limits
ax.set_xlim(0, 30e15)
ax.set_ylim(0, 20e15)
ax.tick_params(axis='both', labelsize=16, width=1.5)

# Adjust axis ticks to avoid scientific notation
ax.set_xticks(np.arange(0, 31e15, 10e15))  # 0 to 30e15, step 10e15
ax.set_yticks(np.arange(0, 21e15, 5e15))   # 0 to 20e15, step 5e15

# Set font for axis tick labels
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)

# Remove "e15" from axis tick labels
ax.set_xticklabels([str(int(x / 1e15)) for x in ax.get_xticks()])
ax.set_yticklabels([str(int(y / 1e15)) for y in ax.get_yticks()])

# Add reference lines
x = np.linspace(0, df['HCHO'].max(), 100)
ax.plot(x, x/1.5, color='black', linestyle='-', linewidth=1)
ax.plot(x, x/2.5, color='black', linestyle='-', linewidth=1)

# Grid styling
ax.grid(True, linestyle='-', linewidth=0.7, color='gray', alpha=0.7)

# Set border thickness
for spine in ax.spines.values():
    spine.set_linewidth(1.5)

# Show top and right borders
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Save figure
plt.savefig("D:/Data/FR/FNR/HCHOxNO2xO3.svg", format='svg', bbox_inches='tight', dpi=300)
plt.savefig("D:/Data/FR/FNR/HCHOxNO2xO3.png", format='png', bbox_inches='tight', dpi=300)

# Show plot
plt.show()