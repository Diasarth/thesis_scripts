import netCDF4 as nc
import pandas as pd
import numpy as np
import os

# Function to process a NetCDF file and return a dataframe
def process_file(file_path, lat_range, lon_range):
    # Open the NetCDF file
    dataset = nc.Dataset(file_path, 'r')

    # Extract HCHO and coordinates
    hcho = dataset.variables["HCHO"][:]
    x_data = dataset.variables["x"][:]
    y_data = dataset.variables["y"][:]
    t_data = dataset.variables["t"][:]

    # Create the dataframe
    hcho_df = pd.DataFrame({
        'hcho': hcho.flatten(),
        'lon': x_data.tolist() * len(y_data) * len(t_data),
        'lat': np.tile(y_data.repeat(len(x_data)), len(t_data)),
        'day': t_data.repeat(len(x_data) * len(y_data)),
    })

    # Filter the region of interest
    hcho_df = hcho_df[
        (hcho_df['lon'] >= lon_range[0]) & (hcho_df['lon'] <= lon_range[1]) &
        (hcho_df['lat'] >= lat_range[0]) & (hcho_df['lat'] <= lat_range[1])
    ]

    # Close the NetCDF file
    dataset.close()

    return hcho_df


# List of regions of interest (latitude and longitude bounds)
regions = [
    {'lat_range': (-24.08, -23.38), 'lon_range': (-46.88, -46.18)},  # MASP
    {'lat_range': (-21.93, -21.23), 'lon_range': (-49.63, -48.93)},  # COUNTRYSIDE
    {'lat_range': (-24.60, -23.90), 'lon_range': (-48.73, -48.03)},  # PETAR
    {'lat_range': (-23.59, -23.49), 'lon_range': (-46.67, -46.57)},  # PARQUE_DOM_PEDRO_II
    {'lat_range': (-24.03, -23.93), 'lon_range': (-46.35, -46.25)},  # SANTOS
    {'lat_range': (-21.52, -21.42), 'lon_range': (-49.26, -49.16)},  # NOVO_HORIZONTE
    {'lat_range': (-23.78, -23.68), 'lon_range': (-47.01, -46.91)},  # MORRO_GRANDE
    {'lat_range': (-24.41, -24.31), 'lon_range': (-48.48, -48.38)},  # CENTRAL_PETAR
    {'lat_range': (-21.77, -21.67), 'lon_range': (-49.46, -49.36)}   # SP_AGRICULTURE
]


# Process each region and calculate daily HCHO averages
daily_mean_by_region = []

for region in regions:
    combined_df = pd.DataFrame()
    directories = [
        "D:/Data/SP/HCHO"  # Folder with HCHO NetCDF files
    ]

    files = []
    for directory in directories:
        files.extend([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.nc')])
    
    for file in files:
        temp_df = process_file(file, lat_range=region['lat_range'], lon_range=region['lon_range'])
        combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

    # Ignore negative values when calculating the mean
    combined_df = combined_df[combined_df['hcho'] >= 0]

    if not combined_df.empty:
        start_date = pd.to_datetime('1990-01-01')
        combined_df['day'] = start_date + pd.to_timedelta(combined_df['day'], unit='D')
        daily_mean = combined_df.groupby('day')['hcho'].mean().reset_index()
        daily_mean_by_region.append(daily_mean)


# Define region names
region_names = [
    "MASP", "COUNTRYSIDE", "PETAR", "PARQUE_DOM_PEDRO_II", "SANTOS",
    "NOVO_HORIZONTE", "MORRO_GRANDE", "CENTRAL_PETAR", "SP_AGRICULTURE"
]


# Combine results into a single dataframe
final_result = daily_mean_by_region[0]
for i in range(1, len(daily_mean_by_region)):
    final_result = pd.merge(
        final_result,
        daily_mean_by_region[i],
        on='day',
        suffixes=('', f'_{region_names[i]}'),
        how='outer'
    )

# Rename columns to indicate regions
final_result.columns = ['day'] + region_names

# Sort dataframe by day
final_result = final_result.sort_values(by='day')

# Identify first and last date
start_date = final_result['day'].iloc[0]
end_date = final_result['day'].iloc[-1]

# Create dataframe with all dates in the interval
date_range_df = pd.DataFrame({'day': pd.date_range(start=start_date, end=end_date)})

# Merge interval dataframe with final results
final_result = pd.merge(date_range_df, final_result, on='day', how='outer')

# Export the dataframe to CSV
final_result.to_csv("D:/OpenEO_Results/Dataframes/SP/SP_HCHO.csv", index=False)
