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

# Seasons of the year
seasons = {
    'Winter': [(1, 1), (3, 20)],
    'Spring': [(3, 21), (6, 20)],
    'Summer': [(6, 21), (9, 22)],
    'Autumn': [(9, 23), (12, 20)]
}
season_order = ['Winter', 'Spring', 'Summer', 'Autumn']

# Path to the CSV file
csv_file = 'D:/Data/FR/METEOROLOGY/CLERMONT_FERRAND/Clermont_Ferrand_2019_2023.csv'
df = pd.read_csv(csv_file, delimiter=';', encoding='ANSI')

# Date validation
df = df[(df['mês'].between(1, 12)) & (df['dia'].between(1, 31))]
df['data'] = pd.to_datetime(df[['ano', 'mês', 'dia']].rename(columns={'ano': 'year', 'mês': 'month', 'dia': 'day'}), errors='coerce')
df = df.dropna(subset=['data'])

# Parameters and labels
parameters = ['temp', 'umid', 'pres', 'prec']
plot_titles = {
    'temp': 'Air Temperature (°C)',
    'umid': 'Relative Humidity (%)',
    'pres': 'Air Pressure (hPa)',
    'prec': 'Precipitation (mm)'
}
colors = {
    'temp': 'red',
    'umid': 'teal',
    'pres': 'orange',
    'prec': 'blue'
}

# Define the season of the year for each row
df['season'] = ''
for season, (start, end) in seasons.items():
    mask = ((df['mês'] > start[0]) | ((df['mês'] == start[0]) & (df['dia'] >= start[1]))) & \
           ((df['mês'] < end[0]) | ((df['mês'] == end[0]) & (df['dia'] <= end[1])))
    df.loc[mask, 'season'] = season + '/' + df['ano'].astype(str)

df['season'] = pd.Categorical(df['season'], categories=[
    f"{season}/{year}" for year in range(df['ano'].min(), df['ano'].max() + 1) for season in season_order
], ordered=True)

# Create figure
fig, axs = plt.subplots(len(parameters), 1, figsize=(12, 11), sharex=False, dpi=150)
fig.subplots_adjust(hspace=0.1)

# Generate plots
for idx, parameter in enumerate(parameters):
    ax = axs[idx]

    # Daily mean
    daily = df.groupby('data')[parameter].mean().reset_index()
    if parameter == 'prec':
        daily[parameter] = df.groupby('data')[parameter].sum().reset_index()[parameter]

    # Seasonal mean
    seasonal = df.groupby('season')[parameter].mean().reset_index()
    if parameter == 'prec':
        seasonal[parameter] = df.groupby('season')[parameter].sum().reset_index()[parameter]

    fake_dates = pd.date_range(start='2019-03-01', periods=len(seasonal), freq='90D')
    color = colors[parameter]

    # Title inside plot area
    ax.text(0.015, 0.85, plot_titles[parameter], transform=ax.transAxes, fontsize=17, font=font_prop)

    for spine in ax.spines.values():
        spine.set_linewidth(2)
                
    ax.tick_params(axis='both', width=2, colors='black')    

    if parameter == 'prec':
        ax2 = ax.twinx()
        ax2.plot(daily['data'], daily[parameter], label='Daily Mean', color=color, alpha=0.4)
        ax2.tick_params(axis='y', width=2, color='black')
        ax.plot(fake_dates, seasonal[parameter], color=color, marker='o', linewidth=2.5, markersize=8, label='Seasonal Mean')
        ax.tick_params(axis='y')
        ax.tick_params(axis='x')
        for label in ax.get_yticklabels():
            label.set_color(color)
            label.set_fontproperties(font_prop_black)
        for label in ax2.get_yticklabels():
            label.set_color((0.0, 0.0, 1.0, 0.5))   
            label.set_fontproperties(font_prop_black)
        for label in ax.get_xticklabels():
            label.set_color('black')
            label.set_fontproperties(font_prop_black)
        
    else:
        ax.plot(daily['data'], daily[parameter], label='Daily Mean', color=color, alpha=0.4)
        ax.plot(fake_dates, seasonal[parameter], color=color, marker='o', linewidth=2.5, markersize=8, label='Seasonal Mean')
        ax.tick_params(axis='y')
        for label in ax.get_yticklabels():
            label.set_color(color)
            label.set_fontproperties(font_prop_black)
    
    if parameter != 'prec':
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    
    if parameter == 'temp':
        ax.set_ylim(-5, 37)
        ax.set_yticks(np.arange(-5, 37, 8))
        
    if parameter == 'umid':
        ax.set_ylim(30, 110)
        ax.set_yticks(np.arange(30, 110, 20))
    
    if parameter == 'pres':
        ax.set_ylim(945, 1010)
        ax.set_yticks(np.arange(945, 1010, 15))
        
    if parameter == 'prec':
        ax.set_ylim(0, 350)
        ax.set_yticks(np.arange(0, 350, 75))
        ax2.set_ylim(0, 40)
        ax2.set_yticks(np.arange(0, 41, 10))

    ax.grid(axis='x', color='silver', linestyle='-')
    ax.grid(axis='y', color='lightgray', linestyle='--')

# Save figure
base_name = os.path.splitext(os.path.basename(csv_file))[0]
output_dir = os.path.dirname(csv_file)
output_png = os.path.join(output_dir, f'{base_name}.png')
output_svg = os.path.join(output_dir, f'{base_name}.svg')

plt.savefig(output_png, bbox_inches='tight')
plt.savefig(output_svg, bbox_inches='tight')

# Show plot
plt.show()