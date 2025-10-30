import netCDF4 as nc
import pandas as pd
import numpy as np
import os

# Function to extract data from NetCDF and save as CSV
def netcdf_to_csv(netcdf_file, csv_file):
    
    # Open the NetCDF file for reading
    nc_data = nc.Dataset(netcdf_file, 'r')

    # Extract variables
    hcho_data = nc_data.variables['HCHO'][:]
    x_data = nc_data.variables['x'][:]
    y_data = nc_data.variables['y'][:]
    t_data = nc_data.variables['t'][:]

    # Close the NetCDF file
    nc_data.close()

    # Create a pandas DataFrame with extracted data
    df = pd.DataFrame({
        'HCHO': hcho_data.flatten(),
        'x': x_data.tolist() * len(y_data) * len(t_data),
        'y': np.tile(y_data.repeat(len(x_data)), len(t_data)),
        't': t_data.repeat(len(x_data) * len(y_data)),
    })
    
    # Convert time variable to YYYY-MM-DD format
    start_date = pd.to_datetime('1990-01-01')
    df['t'] = start_date + pd.to_timedelta(df['t'], unit='D')

    # Save the DataFrame to a CSV file
    df.to_csv(csv_file, index=False)

# Check if output directory exists and create it if necessary
csv_directory = "D:/Results/CSV_Files/FR/HCHO"
if not os.path.exists(csv_directory):
    os.makedirs(csv_directory)

# Path to the directory containing NetCDF files
netcdf_directory = "D:/Data/FR/HCHO"

# Recursively walk through subdirectories and process NetCDF files
for root, dirs, files in os.walk(netcdf_directory):
    for name in files:
        if name.endswith('.nc'):
            netcdf_file = os.path.join(root, name)
            netcdf_file_base = os.path.splitext(name)[0]
            csv_file = os.path.join(csv_directory, f"{netcdf_file_base}.csv")
            netcdf_to_csv(netcdf_file, csv_file)