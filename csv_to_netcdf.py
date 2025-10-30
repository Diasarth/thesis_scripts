import pandas as pd
import numpy as np
import datetime
import os
from scipy.interpolate import griddata
from netCDF4 import Dataset

# Load CSV files
files = []
directory = 'D:/Results/CSV_Files/HCHO_SP'
files.extend([os.path.join(directory, name) for name in os.listdir(directory) if name.endswith('.csv')])

for file in files:

    df = pd.read_csv(file)
    
    # Extract the first date from the CSV file
    start_date = datetime.datetime.strptime(df['t'].min(), "%Y-%m-%d")
    start_date_str = start_date.strftime("%d/%m/%Y")
    
    # Extract the last date from the CSV file
    end_date = datetime.datetime.strptime(df['t'].max(), "%Y-%m-%d")
    end_date_str = end_date.strftime("%d/%m/%Y")
    
    # Filter the data for the specified date range
    data_in_range = df[(df['t'] >= start_date.strftime("%Y-%m-%d")) & (df['t'] <= end_date.strftime("%Y-%m-%d"))]
    
    # Remove rows with NaN values in the 'HCHO' column
    data_in_range = data_in_range.dropna(subset=['HCHO'])
    
    # Convert HCHO data from mol/m² to molecules/cm² (example placeholder, commented)
    ##data_in_range['HCHO'] /= 4.4615E-04
    
    # Calculate monthly averages grouped by latitude and longitude
    monthly_means = data_in_range.groupby(['x', 'y'])['HCHO'].mean().reset_index()
        
    # Create a regular grid for interpolation
    lon_min, lon_max = monthly_means['x'].min(), monthly_means['x'].max()
    lat_min, lat_max = monthly_means['y'].min(), monthly_means['y'].max()
    
    lon_grid, lat_grid = np.meshgrid(np.linspace(lon_min, lon_max, 176), np.linspace(lat_min, lat_max, 167))
    
    points = np.array(monthly_means[['x', 'y']])
    values = np.array(monthly_means['HCHO'])
    
    # Interpolate HCHO data onto the grid
    hcho_interp = griddata(points, values, (lon_grid, lat_grid), method='linear')
    
    # Extract the CSV file name without extension
    file_name = os.path.splitext(os.path.basename(file))[0]
    
    # Save interpolated data to a NetCDF file
    with Dataset(f'D:/Results/Monthly_Means/NetCDF_Files/HCHO/{file_name}.nc', 'w') as ncfile:
        
        # Create dimensions
        ncfile.createDimension('lon', len(lon_grid[0]))
        ncfile.createDimension('lat', len(lat_grid))
        
        # Create variables
        lon_var = ncfile.createVariable('longitude', 'f4', ('lon',))
        lat_var = ncfile.createVariable('latitude', 'f4', ('lat',))
        hcho_var = ncfile.createVariable('HCHO', 'f4', ('lat', 'lon'))
        
        # Assign variable values
        lon_var[:] = np.linspace(lon_min, lon_max, len(lon_grid[0]))
        lat_var[:] = np.linspace(lat_min, lat_max, len(lat_grid))
        hcho_var[:, :] = hcho_interp
    
        # Add history attribute
        ncfile.history = f'Monthly mean HCHO data for {start_date_str} to {end_date_str}'