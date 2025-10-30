import os
import numpy as np
import netCDF4 as nc
import xarray as xr
from scipy.interpolate import griddata

# Paths
HCHO_DIR = r"D:\Data\FR\HCHO"
PBLH_DIR = r"D:\Data\FR\MERRA2\PBLH"
OUT_DIR = r"D:\Data\FR\PBL\HCHO"
os.makedirs(OUT_DIR, exist_ok=True)

YEARS = range(2019, 2024)  # inclusive

# Constants
NA = 6.022e23        # molecules/mol
R = 8.314            # J/(mol·K)
Ts = 12.38 + 273.15  # K
ps = 99587.0         # Pa
n_air_surf = ps * NA / (R * Ts)  # molecules/m³

# Function to find file by date
def find_file_by_date(folder, date_str):
    suffix = f"{date_str}.SUB.nc"
    for file in os.listdir(folder):
        if file.endswith(suffix):
            return os.path.join(folder, file)
    return None

# Function to load MERRA-2 PBLH data
def load_merra2_pblh(date):
    date_str = np.datetime_as_string(date, unit='D').replace('-', '')
    path = find_file_by_date(PBLH_DIR, date_str)
    if path is None:
        return None
    with nc.Dataset(path) as ds:
        lat = ds['lat'][:]
        lon = ds['lon'][:]
        pblh_var = 'PBLH' if 'PBLH' in ds.variables else list(ds.variables.keys())[-1]
        pblh = ds[pblh_var][:]
        if pblh.ndim == 3:
            pblh = np.nanmean(pblh, axis=0)
    return lat, lon, pblh

# Function to interpolate 2D data to target grid
def interpolate_to_grid(src_lat, src_lon, src_data, tgt_lat, tgt_lon, method='linear'):
    lon2d, lat2d = np.meshgrid(src_lon, src_lat)
    points = np.column_stack((lon2d.ravel(), lat2d.ravel()))
    values = src_data.ravel()
    tgt_lon2d, tgt_lat2d = np.meshgrid(tgt_lon, tgt_lat)
    tgt_points = np.column_stack((tgt_lon2d.ravel(), tgt_lat2d.ravel()))
    interp_vals = griddata(points, values, tgt_points, method=method)
    return interp_vals.reshape(len(tgt_lat), len(tgt_lon))

# Loop over years and months
for year in YEARS:
    for month in range(1, 13):
        
        tropomi_file = f"FR_HCHO_{year}_{month:02d}.nc"
        tropomi_path = os.path.join(HCHO_DIR, tropomi_file)
        if not os.path.exists(tropomi_path):
            continue

        ds_tropomi = xr.open_dataset(tropomi_path)
        lat_tropomi = ds_tropomi['y'].values
        lon_tropomi = ds_tropomi['x'].values
        dates = ds_tropomi['t'].values
        hcho_vcd_mol_m2 = ds_tropomi['HCHO'].values  # mol/m²

        hcho_pbl_month = []

        for idx, date in enumerate(dates):
            merra2_data = load_merra2_pblh(date)
            if merra2_data is None:
                continue
            pblh_lat, pblh_lon, pblh_vals = merra2_data

            # Interpolate PBLH to TROPOMI grid
            pblh_interp = interpolate_to_grid(pblh_lat, pblh_lon, pblh_vals, lat_tropomi, lon_tropomi)

            # N_air,PBL in molecules/cm²
            N_air_PBL = pblh_interp * n_air_surf * 1e-4
            
            # Convert VCD to molecules/cm²
            hcho_vcd_mol_cm2 = hcho_vcd_mol_m2[idx, :, :] * NA * 1e-4
            
            # Compute XPBL in ppbv
            with np.errstate(divide='ignore', invalid='ignore'):
                hcho_pbl = hcho_vcd_mol_cm2 / N_air_PBL * 1e9

            hcho_pbl_month.append(hcho_pbl)

        if len(hcho_pbl_month) == 0:
            continue

        hcho_pbl_month = np.array(hcho_pbl_month)

        # Save NetCDF
        nc_out = os.path.join(OUT_DIR, f"FR_HCHO_PBL_{year}_{month:02d}.nc")
        with nc.Dataset(nc_out, 'w', format='NETCDF4') as ds_out:
            ds_out.createDimension('t', None)
            ds_out.createDimension('y', len(lat_tropomi))
            ds_out.createDimension('x', len(lon_tropomi))

            t_var = ds_out.createVariable('t', 'i4', ('t',))
            y_var = ds_out.createVariable('y', 'f8', ('y',))
            x_var = ds_out.createVariable('x', 'f8', ('x',))
            hcho_var = ds_out.createVariable('HCHO_PBL', 'f4', ('t', 'y', 'x'), fill_value=np.nan, zlib=True)

            t_var.units = "days since 1990-01-01"
            t_var.long_name = "time"
            t_var.axis = "T"
            y_var.units = "degrees_north"
            y_var.long_name = "latitude"
            x_var.units = "degrees_east"
            x_var.long_name = "longitude"

            hcho_var.long_name = "PBL-mean Formaldehyde mixing ratio"
            hcho_var.units = "ppbv"
            hcho_var.description = (
                "Computed from TROPOMI Formaldehyde VCD and MERRA-2 PBLH without capping."
            )

            t_var[:] = np.arange(len(hcho_pbl_month))
            y_var[:] = lat_tropomi
            x_var[:] = lon_tropomi
            hcho_var[:, :, :] = hcho_pbl_month

        print(f" >> Saved monthly file: {nc_out}")

print("Done.")