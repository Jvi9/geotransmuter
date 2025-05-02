
"""Study area Caychihue in Peru"""
# lat, lon = -13.17, -70.52
# lat, lon = -12.95, -70.48 

from pathlib import Path
import openeo
from openeo import processes as eop
from shapely.geometry import box
import matplotlib.pyplot as plt
import xarray as xr
import os
from numpy import datetime_as_string
# Your client credentials


backend_url = "openeo.dataspace.copernicus.eu/"

eoconn = openeo.connect(backend_url)
eoconn.authenticate_oidc()

# bbox = [5.0, 51.2, 5.1, 51.3]
bbox = [-72.0339427207,-16.0174594097,-72.0269689773,-16.0112925486]
year = 2019

startdate = f"{year}-01-01"
enddate = f"{year}-12-30"

s2_bands = eoconn.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=[startdate, enddate],
    spatial_extent=dict(zip(["west", "south", "east", "north"], bbox)),
    bands=["B02", "B03" ,"B04", "B07", "B08"], #, "SCL"
    max_cloud_cover=5,
)

nb_of_timesteps = 12

## We use the SCL band to create a mask where clouded pixels are set to 1
## and other pixels are set to 0
scl_band = s2_bands.band("SCL")
s2_cloudmask = ((scl_band == 8) | (scl_band == 9) | (scl_band == 3)) * 1.0

## Reduce the spacial dimension using the reducer "mean" to calculate the average cloud coverage
# TODO: replace aggregate_spacial with reduce_spacial in a future openeo client version
bbox_poly = box(*bbox)
avg_cloudmask = s2_cloudmask.aggregate_spatial(geometries=bbox_poly, reducer="mean")

## Download the result for local sorting
avg_cloudmask.download(r"C:\Users\jvila\Desktop\geotransmuter\backend\data/avg_cloudmask2.nc", format="NetCDF")

## Open the calculated cloudmask aggregation
avg_array = xr.open_dataset(r"C:\Users\jvila\Desktop\geotransmuter\backend\data/avg_cloudmask2.nc")

## Sort the timesteps by their cloud coverage and select the best ones
best_timesteps_dt64 = (
    avg_array.squeeze("feature")
    .sortby("band_0", ascending=True)
    .coords["t"]
    .values[:nb_of_timesteps]
)

## Close the dataset
avg_array.close()

## Convert the timestep labels to iso format
best_timesteps = [
    datetime_as_string(t, unit="s", timezone="UTC") for t in best_timesteps_dt64
]

## Create a condition that checks if a date is one of the best timesteps
condition = lambda x: eop.any(
    [
        eop.date_between(
            x=x, min=timestep, max=eop.date_shift(date=timestep, value=1, unit="day")
        )
        for timestep in best_timesteps
    ]
)
## Filter the bands using the condition
s2_bands_reduced = s2_bands.filter_labels(condition=condition, dimension="t")

ndviband = s2_bands_reduced.ndvi(red="B04", nir="B08")

ndviband.download(r"C:\Users\jvila\Desktop\geotransmuter\backend\data/ndvi.nc")

## Load your dataset
ndvi_data = xr.open_dataset(r"C:\Users\jvila\Desktop\geotransmuter\backend\data/ndvi.nc")

## Access the "var" variable
var = ndvi_data["var"]

## Select the top 3 time steps
three_steps = var["t"][-3:]

## Create a 1x3 horizontal plot for the top 3 time steps
plt.figure(figsize=(16, 10))  # Adjust the figure size as needed
for i, t in enumerate(three_steps):
    plt.subplot(1, 3, i + 1)
    data_slice = var.sel(t=t)
    dt = t.values.astype("M8[D]").astype("O")  # Convert to Python datetime object
    formatted_date = dt.strftime("%Y-%m-%d")  # Format the date
    plt.imshow(data_slice, cmap="viridis", origin="lower", vmin=0, vmax=1)
    plt.title(f"Date: {formatted_date}")
    # Hide both horizontal and vertical ticks and labels
    plt.xticks([])
    plt.yticks([])
plt.tight_layout()  # Ensures proper spacing between subplots
plt.show()

## Close the dataset
ndvi_data.close()



# =============================================================================
# drafts
# =============================================================================
# import openeo        
# connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
# connection.authenticate_oidc()
# # Example usage
# coords = [-70.544881, -13.036431, -70.506269, -13.009962]
# spatial_extent = create_spatial_extent(coords)
# print(spatial_extent)

connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()
s2_cube = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=("2019-01-01", "2019-12-30"),
    spatial_extent={
        "west": -70.5448809103,
        "south": -13.0364308189,
        "east": -70.5062687748,
        "north": -13.0099624388,
        "crs": "EPSG:4326",
    },
    # bands=["B04"],
    bands=["B02", "B03" ,"B04", "B07", "B08"],
    max_cloud_cover=5,
)

#download
path= r"C:\Users\jvila\Desktop\geotransmuter\backend\data"
data_name = "huasamayo.nc"
full_path = os.path.join(path,data_name)
s2_cube.download(full_path)
