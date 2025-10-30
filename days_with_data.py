import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

# Font configuration
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path, size=12)
font_prop_black = font_manager.FontProperties(fname=font_path2, size=13)

# Color palette
colors = [
    '#005f73', '#0a9396', '#94d2bd', '#e9d8a6',
    '#ee9b00', '#ca6702', '#bb3e03', '#9d0208',
    '#6a040f'
]

# List of CSV files and pollutant labels
csv_files = [
    'D:/Results/Dataframes/SP/SP_HCHO.csv',
    'D:/Results/Dataframes/SP/SP_NO2.csv',
    'D:/Results/Dataframes/SP/SP_O3.csv',
    'D:/Results/Dataframes/SP/SP_SO2.csv',
    'D:/Results/Dataframes/SP/SP_CO.csv',
]
pollutant_labels = ['HCHO', 'NO$_2$', 'O$_3$', 'SO$_2$', 'CO']

# Create figure with vertical subplots
fig, axes = plt.subplots(len(csv_files), 1, figsize=(9, 9), sharex=True)
axes = axes.flatten()

# Initialize containers for legend handles and labels
legend_handles = []
legend_labels = []

# Loop through each CSV file
for idx, (csv_path, label) in enumerate(zip(csv_files, pollutant_labels)):
    df = pd.read_csv(csv_path, parse_dates=['day'])

    # Create 'year' column if not present
    if 'year' not in df.columns:
        df['year'] = df['day'].dt.year

    # Identify area columns dynamically (ignore 'day' and 'year')
    areas = [col for col in df.columns if col not in ['day', 'year']]

    # Group by year and count valid (non-NaN) data points
    counts = df.groupby('year')[areas].apply(lambda g: g.notna().sum()).reset_index()

    # Plotting parameters
    years = counts['year'].astype(str)
    n_areas = len(areas)
    bar_width = 0.9 / n_areas
    x = np.arange(len(years))
    ax = axes[idx]

    # Plot grouped bars
    for i, area in enumerate(areas):
        bar = ax.bar(
            x + i * bar_width,
            counts[area],
            width=bar_width,
            label=area.replace('_', ' '),
            edgecolor='black',
            color=colors[i % len(colors)],
            zorder=2
        )

        # Save legend handles only for the first plot
        if idx == 0:
            legend_handles.append(bar)
            legend_labels.append(area.replace('_', ' '))

    # Y-axis configuration
    ax.set_ylabel(f'{label}\ndays with data', fontproperties=font_prop)
    ax.tick_params(axis='y', width=2)
    ax.set_ylim(0, 400)
    ax.set_yticks(np.arange(0, 401, 120))

    # Apply custom font to Y tick labels
    for label_y in ax.get_yticklabels():
        label_y.set_fontproperties(font_prop)

    # X-axis configuration
    # Only the last subplot shows X-axis labels
    if idx == len(csv_files) - 1:
        ax.set_xticks(x + bar_width * (n_areas - 1) / 2)
        ax.set_xticklabels(years, fontproperties=font_prop)
        ax.tick_params(axis='x', width=2)
    else:
        ax.tick_params(axis='x', bottom=False, top=False, labelbottom=False)

    # Add horizontal grid
    ax.grid(axis='y', linestyle='--', linewidth=0.8, alpha=0.5, zorder=0)

    # Reinforce borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_linewidth(2)

# Global legend below all subplots
fig.legend(
    handles=legend_handles,
    labels=legend_labels,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.04),
    ncol=3,
    frameon=False,
    prop=font_prop
)

# Layout adjustments
plt.tight_layout()
plt.subplots_adjust(hspace=0.1, bottom=0.09)

# Save figure
output_dir = os.path.dirname(csv_files[0])
plt.savefig(os.path.join(output_dir, 'SP_valid_days_all_pollutants.svg'),
            format='svg', bbox_inches='tight', dpi=300)
plt.savefig(os.path.join(output_dir, 'SP_valid_days_all_pollutants.png'),
            format='png', bbox_inches='tight', dpi=300)

# Show plot
plt.show()
