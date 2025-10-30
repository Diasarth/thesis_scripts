import openeo

# Connect to the openEO backend and authenticate via OIDC
connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

# List of months
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

# Loop over months to process monthly data
for i in range(len(months) - 1):
    # Define the temporal extent for the current month
    temporal_extent = ["2023-" + months[i] + "-01", "2023-" + months[i + 1] + "-01"]

    # Load the Sentinel-5P collection for the specified month and spatial region
    s5p_data = connection.load_collection(
        "SENTINEL_5P_L2",
        temporal_extent=temporal_extent,
        spatial_extent={
            "west": -53.371582,
            "south": -25.363882,
            "east": -43.813477,
            "north": -19.580493
        },
        bands=["O3"],  # Ozone band
    )

    # Execute the batch job and save the monthly output as NetCDF
    job = s5p_data.execute_batch(
        title="O3",
        outputfile="SP_O3_2023_" + months[i] + ".nc"
    )