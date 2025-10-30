# PhD Data Processing and Analysis Scripts

This repository contains the Python scripts developed for **data acquisition**, **processing**, **analysis** and **visualization** throughout my PhD research.  
They provide a **reproducible workflow** for handling atmospheric and environmental datasets, including:

- Automated retrieval of **TROPOMI** satellite and **MERRA-2** reanalysis products  
- Transformation of raw data into **analysis-ready formats**  
- Calculation of **derived variables** such as tropospheric ozone columns and boundary-layer mixing ratios  
- Generation of **figures and plots** to interpret temporal and spatial patterns  

By sharing these tools, the repository enables other researchers to **replicate, validate and extend** the analyses presented in the thesis.

<br>

## 1. Data Acquisition (APIs)

Scripts in this group automate the retrieval of remote sensing and reanalysis datasets:

- **`openeo_tropomi_download.py`** – Downloads TROPOMI satellite products through the OpenEO platform.

- **`earthdata_merra2_download.py`** – Downloads MERRA-2 atmospheric variables from NASA Earthdata.

<br>

## 2. Data Processing and Conversion

These scripts prepare the raw datasets for subsequent analysis:

- **`dataframes_selected_sites.py`** – Extracts data for custom selected sites and organizes it into structured dataframes.

- **`vcds_monthly_means.py`** – Calculates multi-year monthly mean VCDs from individual monthly NetCDF files, producing one NetCDF per month with averaged values and metadata for seasonal and long-term analysis.

- **`netcdf_to_csv.py`** – Converts NetCDF datasets to CSV format for general use or external analysis.

- **`csv_to_netcdf.py`** – Converts CSV-formatted data into NetCDF files suitable for plotting.

<br>

## 3. Derived Variable Calculation

These scripts combine TROPOMI and MERRA-2 data to derive new atmospheric variables:

- **`pbl_hcho_and_no2.py`** – Computes planetary boundary layer (PBL) mixing ratios of HCHO and NO₂ by integrating TROPOMI vertical column densities with interpolated MERRA-2 PBL heights.
 
- **`tropospheric_ozone_estimation.py`** – Estimates tropospheric ozone columns by scaling TROPOMI total ozone using the troposphere-to-total ozone ratio derived from MERRA-2 reanalysis data.

<br>

## 4. Visualization and Statistical Analysis

Scripts in this group generate figures and summary plots used for analysis and interpretation:

- **`seasonal_meteorology_plot.py`** – Generates seasonal and daily time series plots of meteorological parameters (temperature, humidity, pressure, precipitation). *Example output:*

<div align="center">
<figure>
  <img src="example_images/seasonal_meteorology_plot.svg" alt="seasonal_meteorology_plot" width="500">
</figure>
</div>
<br>

- **`monthly_meteorology_plot.py`** – Produces monthly averaged bar plots of meteorological parameters.

<div align="center">
<figure>
  <img src="example_images/monthly_meteorology_plot.svg" alt="monthly_meteorology_plot" width="500">
</figure>
</div>
<br>

- **`windrose_and_distribution.py`** – Creates wind rose diagrams and wind speed distribution histograms.

<div align="center">
<figure>
  <img src="example_images/windrose_and_distribution_1.svg" alt="windrose_and_distribution_1" width="400">
</figure>
<figure>
  <img src="example_images/windrose_and_distribution_2.svg" alt="windrose_and_distribution_2" width="400">
</figure>
</div>
<br>

- **`days_with_data.py`** – Calculates and plots the annual number of valid TROPOMI data days for multiple trace gases.

<div align="center">
<figure>
  <img src="example_images/days_with_data.svg" alt="days_with_data" width="500">
</figure>
</div>
<br>

- **`seasonal_average_grid.py`** – Generates 3×3 grids of seasonal averages with error bars and smoothed splines, including annual trends.

<div align="center">
<figure>
  <img src="example_images/seasonal_average_grid.svg" alt="seasonal_average_grid" width="500">
</figure>
</div>
<br>

- **`hcho_x_no2_x_o3.py`** – Creates scatter plots of HCHO vs NO₂, colored by O₃, with reference lines representing FNR thresholds.

<div align="center">
<figure>
  <img src="example_images/hcho_x_no2_x_o3.svg" alt="hcho_x_no2_x_o3" width="300">
</figure>
</div>
<br>

- **`fnr_x_prob_o3.py`** – Plots FNR against ozone exceedance probability with polynomial fits and confidence intervals.

<div align="center">
<figure>
  <img src="example_images/fnr_x_prob_o3.svg" alt="fnr_x_prob_o3" width="300">
</figure>
</div>
<br>

- **`fnr_trends_plot.py`** – Produces multi-panel seasonal trends of HCHO and NO₂ across different land-use categories with regression lines.

<div align="center">
<figure>
  <img src="example_images/fnr_trends_plot.svg" alt="fnr_trends_plot" width="500">
</figure>
</div>
<br>

## Citation

If you use these scripts, please cite my PhD thesis:
> **FREITAS, A. D.**, *Satellite observations of trace gases vertical columns: exploring temporal and spatial complexities*. Thesis (Ph.D. in Meteorology). Institute of Astronomy, Geophysics and Atmospheric Sciences, University of São Paulo, São Paulo, 2026.

<br>

## License

This repository is released under the **MIT License**, allowing free use, modification and distribution with attribution.

