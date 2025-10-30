import os
from netCDF4 import Dataset

# Directories
input_dir = r'D:\Data\FR\HCHO_MEAN'
output_dir = r'D:\Data\FR\HCHO_MEAN_ALL_YEARS'

# Function to load variables from a NetCDF file
def load_netcdf(file, var_names):
    with Dataset(file, 'r') as ds:
        data = {var: ds.variables[var][:] for var in var_names}
    return data

# Names of required variables
vars_hcho = ['HCHO_mean', 'x', 'y']

# Iterate over months (01 to 12)
for month in range(1, 13):
    
    month_str = f"_{month:02d}_MEAN.nc"
    monthly_files = [f for f in os.listdir(input_dir) if f.endswith(month_str)]

    if not monthly_files:
        print(f"No files found for month {month:02d}.")
        continue

    # Initialize variables
    all_hcho = []
    x_data = None
    y_data = None

    # Load all files for the current month
    for hcho_file in monthly_files:
        input_file = os.path.join(input_dir, hcho_file)

        # Load data from file
        hcho_data = load_netcdf(input_file, vars_hcho)

        # Initialize x and y if this is the first file
        if x_data is None:
            x_data = hcho_data['x']
            y_data = hcho_data['y']

        # Append HCHO_mean data (do not average here since they are already monthly means)
        all_hcho.append(hcho_data['HCHO_mean'])

    # Calculate mean across all files
    hcho_sum = None
    for hcho in all_hcho:
        if hcho_sum is None:
            hcho_sum = hcho
        else:
            hcho_sum += hcho
    hcho_mean = hcho_sum / len(all_hcho)

    # Create new NetCDF file with the monthly mean
    output_file = os.path.join(output_dir, f'HCHO_MEAN_ALL_YEARS_{month:02d}.nc')
    with Dataset(output_file, 'w', format='NETCDF4') as ds_out:
        
        # Create dimensions
        ds_out.createDimension('x', len(x_data))
        ds_out.createDimension('y', len(y_data))

        # Create variables
        x_out = ds_out.createVariable('x', 'f4', ('x',))
        y_out = ds_out.createVariable('y', 'f4', ('y',))
        hcho_mean_out = ds_out.createVariable('HCHO_mean', 'f4', ('y', 'x'))

        # Set attributes
        x_out.standard_name = "longitude"
        x_out.units = "degrees_east"
        x_out.long_name = "Longitude"

        y_out.standard_name = "latitude"
        y_out.units = "degrees_north"
        y_out.long_name = "Latitude"

        hcho_mean_out.standard_name = "mean_concentration_of_formaldehyde_in_air"
        hcho_mean_out.units = "mol m-2"
        hcho_mean_out.long_name = "Mean Formaldehyde concentration"

        # Save data
        x_out[:] = x_data
        y_out[:] = y_data
        hcho_mean_out[:] = hcho_mean

    print(f"Monthly mean for month {month:02d} processed and saved to: {output_file}")
