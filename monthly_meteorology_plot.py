import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

# Font configuration
font_path = 'D:/SF-Pro-Display-Regular.ttf'
font_path2 = 'D:/SF-Pro-Display-Black.ttf'
font_prop = font_manager.FontProperties(fname=font_path)
font_prop_black = font_manager.FontProperties(fname=font_path2, size=15)

# Parameters and plot titles
parameters = ['temp', 'hum', 'pres', 'prec']  # humidity renamed from 'umid'
plot_titles = {
    'temp': 'Air Temperature (°C)',
    'hum': 'Relative Humidity (%)',
    'pres': 'Air Pressure (hPa)',
    'prec': 'Precipitation (mm)'
}

# Colors for each parameter
colors = {
    'temp': 'red',
    'hum': 'teal',
    'pres': 'orange',
    'prec': 'blue'
}

# CSV file path
csv_file = 'D:/Data/SP/METEOROLOGY/SANTOS/Santos_Ponta_da_Praia_2019_2023.csv'
df = pd.read_csv(csv_file, delimiter=';', encoding='ANSI')

# Validate and create a datetime column
df = df[(df['month'].between(1, 12)) & (df['day'].between(1, 31))]
df['date'] = pd.to_datetime(
    df[['year', 'month', 'day']], errors='coerce'
)
df = df.dropna(subset=['date'])

# Calculate monthly averages for temperature, humidity, and pressure
monthly_avg = df.groupby('month')[['temp', 'hum', 'pres']].mean().reset_index()

# Correct calculation of average monthly precipitation:
# 1. Monthly sum per year
annual_prec = df.groupby(['year', 'month'])['prec'].sum().reset_index()

# 2. Average of monthly sums across years
avg_prec = annual_prec.groupby('month')['prec'].mean().reset_index()

# 3. Merge everything into a single DataFrame
monthly = monthly_avg.merge(avg_prec, on='month')

# Month labels
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Create figure and subplots
fig, axs = plt.subplots(len(parameters), 1, figsize=(12, 11), sharex=True, dpi=150)
fig.subplots_adjust(hspace=0.10)

# Generate bar plots for each parameter
for idx, parameter in enumerate(parameters):
    
    ax = axs[idx]
    color = colors[parameter]

    ax.bar(monthly['month'], monthly[parameter], color=color, alpha=0.8, width=0.6)
    ax.text(0.015, 0.85, plot_titles[parameter], transform=ax.transAxes, fontsize=17, font=font_prop)

    # Set spine width
    for spine in ax.spines.values():
        spine.set_linewidth(2)

    ax.tick_params(axis='both', width=2, colors='black')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    
    if parameter != 'prec':
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Customize tick label colors and fonts
    for label in ax.get_yticklabels():
        label.set_color(color)
        label.set_fontproperties(font_prop_black)
    for label in ax.get_xticklabels():
        label.set_color('black')
        label.set_fontproperties(font_prop_black)

    # Set y-limits and ticks based on parameter
    if parameter == 'temp':
        ax.set_ylim(15, 31)
        ax.set_yticks(np.arange(15, 31, 4))

    elif parameter == 'hum':
        ax.set_ylim(80, 95)
        ax.set_yticks(np.arange(80, 95, 4))

    elif parameter == 'pres':
        ax.set_ylim(1008, 1016)
        ax.set_yticks(np.arange(1008, 1016, 2))

    elif parameter == 'prec':
        ax.set_ylim(0, 160)
        ax.set_yticks(np.arange(0, 160, 40))

    # Display grid below bars
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='lightgray', linestyle='--', linewidth=1)

# Save figure
base_name = os.path.splitext(os.path.basename(csv_file))[0] + '_monthly'
output_dir = os.path.dirname(csv_file)
output_png = os.path.join(output_dir, f'{base_name}.png')
output_svg = os.path.join(output_dir, f'{base_name}.svg')

plt.savefig(output_png, bbox_inches='tight')
plt.savefig(output_svg, bbox_inches='tight')

# Show plot
plt.show()