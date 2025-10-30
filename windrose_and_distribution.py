import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from matplotlib import font_manager
from matplotlib.patches import Patch

# Read Excel file
df = pd.read_excel('windrose_clermont.xlsx')

# Custom colors for wind speed bins
custom_colors = ['#cce5ff', '#66b3ff', '#0073e6', '#003366']

# Font configuration
font_path_1 = 'D:/SF-Pro-Display-Regular.ttf'
font_path_2 = 'D:/SF-Pro-Display-Black.ttf'
sf_pro = font_manager.FontProperties(fname=font_path_1, size=15)
sf_pro_black = font_manager.FontProperties(fname=font_path_2, size=14)


# === WIND ROSE ===

ax = WindroseAxes.from_ax()
ax.bar(df.DIRECTION, df.SPEED, normed=True, opening=0.9, bins=np.arange(0, 4, 1), nsector=16, colors=custom_colors)

# Reverse colors and labels to show highest first
inv_colors = custom_colors[::-1]
new_labels = ['> 3.0', '2.0 - 3.0', '1.0 - 2.0', '0.0 - 1.0']
patches = [Patch(facecolor=color, edgecolor='black') for color in inv_colors]

# Create a custom legend (outside the plot area)
legend = ax.figure.legend(
    patches, new_labels, loc='center left', bbox_to_anchor=(0.85, 0.15),
    title='Wind Speed (m/s)', frameon=False
)

for text in legend.get_texts():
    text.set_fontproperties(sf_pro)
legend.get_title().set_fontproperties(sf_pro)

# Remove default radial labels
ax.set_yticklabels([])

# Thicker outer circle
circle = ax.spines['polar']
circle.set_linewidth(3)

# Dashed inner gridlines
ax.grid(True, linestyle='--', linewidth=1)

# Adjust drawing order (bars above grid)
for line in ax.yaxis.get_gridlines():
    line.set_zorder(0)
for patch in ax.patches:
    patch.set_zorder(5)
    patch.set_edgecolor('black')
    patch.set_linewidth(0.7)

# Direction labels
ax.set_xticklabels(['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'])
for label in ax.get_xticklabels():
    label.set_fontproperties(sf_pro_black)

# Add custom percentage labels on top of bars
for r in ax.get_yticks():
    ax.text(np.radians(67), r, f"{r:.1f}%",
            ha='left', va='center', fontsize=15, fontproperties=sf_pro,
            zorder=10, color='black', fontweight='normal',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', alpha=0.7))

# Save figure
plt.savefig('windrose.png', format='png', dpi=300, bbox_inches='tight', transparent=True)
plt.savefig('windrose.svg', format='svg', bbox_inches='tight', transparent=True)


# === WIND SPEED DISTRIBUTION ===

velocities = df.SPEED

# Reload fonts for smaller text
sf_pro = font_manager.FontProperties(fname=font_path_1, size=12)
sf_pro_black = font_manager.FontProperties(fname=font_path_2, size=9)

# Define bins and labels
bins = [0, 1, 2, 3, 4, 5, 6, 7, 8]
labels = ['< 1.0', '1.0 - 1.5', '1.5 - 2.0', '2.0 - 2.5',
          '2.5 - 3.0', '3.0 - 3.5', '3.5 - 4.0', '> 4.0']

# Compute histogram and convert to percentage
counts, edges = np.histogram(velocities, bins=bins)
percent = counts / counts.sum() * 100

# Colors for histogram bars
custom_colors = ['#e6f0ff', '#cce5ff', '#99ccff', '#66b3ff', '#3380ff', '#0073e6', '#004080', '#003366']

fig, ax = plt.subplots(figsize=(8, 4))

# Plot histogram
bars = ax.bar(range(len(percent)), percent, color=custom_colors, edgecolor='black', linewidth=0.7, zorder=5)

# Set axes styles
for side in ['top', 'right', 'left', 'bottom']:
    ax.spines[side].set_visible(True)
    ax.spines[side].set_linewidth(1.5)

ax.spines['bottom'].set_zorder(10)
ax.grid(axis='y', linestyle='--', linewidth=1, alpha=0.7, zorder=0)

# Axis labels and ticks
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)
for label in ax.get_xticklabels():
    label.set_fontproperties(sf_pro_black)
for label in ax.get_yticklabels():
    label.set_fontproperties(sf_pro_black)

ax.set_xlabel('Wind Class (m/s)', fontproperties=sf_pro)
ax.set_ylabel('Frequency (%)', fontproperties=sf_pro)
ax.set_ylim(0, max(percent) * 1.2)
ax.set_yticks(np.arange(0, max(percent) * 1.2 + 5, 10))

ax.xaxis.set_tick_params(width=1.5)
ax.yaxis.set_tick_params(width=1.5)

# Add percentage labels above bars
for i, p in enumerate(percent):
    ax.text(i, p + max(percent) * 0.05, f'{p:.1f}%', ha='center',
            fontproperties=sf_pro, fontsize=10,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', alpha=0.7))

# Save figure
plt.savefig('histogram.png', format='png', dpi=300, bbox_inches='tight', transparent=True)
plt.savefig('histogram.svg', format='svg', bbox_inches='tight', transparent=True)