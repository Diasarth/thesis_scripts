import os
import numpy as np
import netCDF4 as nc
import xarray as xr
from scipy.interpolate import griddata

# Paths
merra_o3_delp_dir = r"D:\Data\FR\MERRA2\O3_AND_DELP"
merra_troppb_dir = r"D:\Data\FR\MERRA2\TROPPB"
tropomi_dir = r"D:\Data\FR\O3"
output_dir = r"D:\Data\FR\O3_TROP"

# Create output folder if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def find_file_by_date(folder, date_str):
    # Searches for a file that ends with the given date string inside the folder
    suffix = f"{date_str}.SUB.nc"
    for f in os.listdir(folder):
        if f.endswith(suffix):
            return os.path.join(folder, f)
    return None

def compute_mid_pressure(delp):
    # Computes mid-level pressures by integrating DELP (Dry Layer Pressure Thickness)
    nlev = delp.shape[0]
    p_interface = np.zeros((nlev + 1, delp.shape[1], delp.shape[2]), dtype=delp.dtype)
    for k in range(1, nlev + 1):
        p_interface[k, :, :] = p_interface[k - 1, :, :] + delp[k - 1, :, :]
    p_mid = 0.5 * (p_interface[:-1, :, :] + p_interface[1:, :, :])
    return p_mid

def compute_tropospheric_ozone(o3, delp, troppb):
    # Computes the tropospheric and total ozone columns and their ratio
    if o3.shape != delp.shape:
        raise ValueError("o3 and delp must have the same shape (nlev, nlat, nlon)")

    # Calculate pressure at mid-levels
    p_mid = compute_mid_pressure(delp)

    # Select layers within the troposphere (pressure >= TROPPB)
    mask_trop = p_mid >= troppb[np.newaxis, :, :]

    # Integrate ozone using DELP as weight
    with np.errstate(invalid='ignore', divide='ignore'):
        o3_trop = np.nansum(np.where(mask_trop, o3 * delp, 0.0), axis=0)
        o3_total = np.nansum(o3 * delp, axis=0)
        ratio = np.where(o3_total != 0.0, o3_trop / o3_total, 0.0)

    return o3_trop, o3_total, ratio

# Loop over all years and months
for year in range(2019, 2024):
    for month in range(1, 13):
        # Build TROPOMI file path
        tropomi_name = f"FR_O3_{year}_{month:02d}.nc"
        tropomi_path = os.path.join(tropomi_dir, tropomi_name)

        # Skip if monthly TROPOMI file does not exist
        if not os.path.exists(tropomi_path):
            continue

        # Open TROPOMI dataset and extract coordinates
        ds_tropomi = xr.open_dataset(tropomi_path)
        lat_tropomi = ds_tropomi['y'].values
        lon_tropomi = ds_tropomi['x'].values
        lons, lats = np.meshgrid(lon_tropomi, lat_tropomi)
        dates = ds_tropomi['t'].values

        o3_trop_month = []
        time_days = []

        # Loop through each daily observation in the month
        for idx, date in enumerate(dates):
            date_str = np.datetime_as_string(date, unit='D').replace('-', '')

            # Find corresponding MERRA-2 files for O3/DELP and TROPPB
            o3_delp_path = find_file_by_date(merra_o3_delp_dir, date_str)
            troppb_path = find_file_by_date(merra_troppb_dir, date_str)

            # Skip if one of the MERRA files is missing
            if o3_delp_path is None or troppb_path is None:
                continue

            # Load MERRA-2 O3 and DELP
            with nc.Dataset(o3_delp_path) as ds_o3:
                o3 = ds_o3.variables['O3'][0, :, :, :]
                delp = ds_o3.variables['DELP'][0, :, :, :]
                lats_merra = ds_o3.variables['lat'][:]
                lons_merra = ds_o3.variables['lon'][:]

            # Load MERRA-2 TROPPB
            with nc.Dataset(troppb_path) as ds_tr:
                troppb = ds_tr.variables['TROPPB'][0, :, :]

            # Compute tropospheric-to-total ozone ratio from MERRA-2
            o3_trop, o3_total, ratio = compute_tropospheric_ozone(o3, delp, troppb)
            print(f"{date_str} - Mean O3 trop/total ratio (MERRA2): {np.nanmean(ratio):.3f}")

            # Interpolate the MERRA-2 ratio to TROPOMI resolution
            lon_grid, lat_grid = np.meshgrid(lons_merra, lats_merra)
            points = np.column_stack((lon_grid.flatten(), lat_grid.flatten()))
            values_ratio = ratio.flatten()
            ratio_interp = griddata(points, values_ratio, (lons, lats), method='linear')

            # Scale TROPOMI total column using the MERRA-2 ratio
            o3_tropomi = ds_tropomi['O3'][idx].values
            o3_scaled = ratio_interp * o3_tropomi
            o3_trop_month.append(o3_scaled)

            # Convert time to "days since 1990-01-01"
            ref_date = np.datetime64('1990-01-01')
            delta_days = (date - ref_date).astype('timedelta64[D]').astype(int)
            time_days.append(delta_days)

        # Skip if no valid daily data were processed
        if len(o3_trop_month) == 0:
            continue

        o3_trop_month = np.array(o3_trop_month)
        time_days = np.array(time_days)

        # Create output NetCDF file
        nc_out = os.path.join(output_dir, f"FR_O3_TROP_{year}_{month:02d}.nc")
        with nc.Dataset(nc_out, 'w', format='NETCDF4') as ds_out:
            # Define dimensions
            ds_out.createDimension('t', None)
            ds_out.createDimension('y', len(lat_tropomi))
            ds_out.createDimension('x', len(lon_tropomi))

            # Create coordinate variables
            t_var = ds_out.createVariable('t', 'i4', ('t',))
            y_var = ds_out.createVariable('y', 'f8', ('y',))
            x_var = ds_out.createVariable('x', 'f8', ('x',))

            # Create data variable for tropospheric ozone
            o3_var = ds_out.createVariable('O3_TROP', 'f4', ('t', 'y', 'x'), fill_value=np.nan, zlib=True)
            crs_var = ds_out.createVariable('crs', 'c')

            # Assign metadata to variables
            t_var.standard_name = "time"
            t_var.long_name = "time"
            t_var.units = "days since 1990-01-01"
            t_var.axis = "T"

            y_var.standard_name = "latitude"
            y_var.long_name = "latitude"
            y_var.units = "degrees_north"

            x_var.standard_name = "longitude"
            x_var.long_name = "longitude"
            x_var.units = "degrees_east"

            o3_var.long_name = "Tropospheric ozone column estimated by scaling TROPOMI total column with MERRA2 ratio"
            o3_var.units = "mol m-2"

            # Write data to output file
            t_var[:] = time_days
            y_var[:] = lat_tropomi
            x_var[:] = lon_tropomi
            o3_var[:, :, :] = o3_trop_month

        print(f"Saved monthly file: {nc_out}")