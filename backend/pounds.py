import os
import openeo
from main_classes import connector,Collection
import matplotlib.pyplot as plt
import xarray as xr

connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()

bbox = [-72.0324448244,-16.0159580619,-72.0295051234,-16.0131530708]
bands = ["B02", "B03" ,"B04", "B07", "B08"]
first_request = connector("4326", 5, "2018-11-01", "2020-02-28",bbox,bands)

first_request.sentinel2_download(connection, "huasamayo.nc")

full_path = os.path.join(os.getcwd(),"data","huasamayo.nc")

huasamayo = Collection(full_path)
huasamayo.calculate_ndwi()
huasamayo.plot_ndwi(-1,1)
huasamayo.plot_water()

huasamayo.calculate_tss()

huasamayo.plot_tss(point_coords=(817768,8227184))
huasamayo.plot_rgb_time_steps()
# =============================================================================
# test
import pandas as pd

data_tss = [20.1,20.3,8403,198.3,679.5,679.5,
            646,661,78.78,105.33,81.13,79.5,154.25,97.98,
            52.93,56.05,143.5,168,34.75,35.7,
            27.9,31.9,21.98,133.0,312.50,556.75]

levels = [64,64,74,65,65,70,65,30,60,64,64,70,64,66,68,66,
          64,63,64,64,70,65,69,68,64,67]

times = ['11-12-2018','12-12-2018','01-22-2019','01-23-2019',
         '02-14-2019','02-15-2019','02-28-2019',
        '03-01-2019','03-27-2019','03-28-2019','04-16-2019',
        '04-17-2019','05-15-2019','05-16-2019','06-14-2019',
        '06-15-2019','08-26-2019','08-27-2019','09-30-2019',
        '10-01-2019','11-07-2019','11-08-2019','12-26-2019',
        '12-27-2019','02-06-2020','02-07-2020']
times = pd.to_datetime(times)
dff = pd.DataFrame(data_tss)
dff.index = times

dlevel = pd.DataFrame(levels)
dlevel.index = times

# selected_data = huasamayo.ds['tss'].sel(x=817768, y=8227184, method='nearest').values
selected_data = huasamayo.ds['tss'].sel(x=817765, y=8227175, method='nearest').values
times = huasamayo.ds['tss'].t.values
times = pd.to_datetime(times)
df = pd.DataFrame(selected_data)
df.index = times


selected_tests = huasamayo.ds['ndwi'].sel(x=817768, y=8227184, method='nearest').values
# Extract NDWI values greater than zero
# Mask where NDWI is greater than zero
ndwi_positive = huasamayo.ds['ndwi'] > 0

# Drop coordinates where NDWI is not greater than zero
positive_coords = ndwi_positive.where(ndwi_positive, drop=True).coords

# Combine x and y coordinate arrays into pairs
x_values = positive_coords['x'].values
y_values = positive_coords['y'].values

# Generate the coordinate pairs
coordinate_pairs = [(x, y) for x in x_values for y in y_values]
print(coordinate_pairs)



# Find common indices
common_indices = df.index.intersection(dff.index)
print(f"Common indices: {common_indices}")



# Plot both DataFrames on the same plot
plt.figure(figsize=(10, 6))
plt.plot(df.index, df, label='Sentinel', marker='o')
plt.plot(dff.index, dff, label='Obs', marker='s')
plt.plot(dlevel.index, dlevel, label='WaterLevel', marker='.')

# Add title, labels, and legend
plt.title('Comparison of Two DataFrames')
plt.xlabel('Date')
plt.ylabel('TSS (mg/L)')
plt.legend()
plt.ylim(0,300)
# Show plot
plt.grid()
plt.show()


# =============================================================================

pounds = Collection(os.path.join(os.getcwd(),"data","pounds.nc"))
pounds.calculate_ndwi()
pounds.plot_ndwi(-1,1)


###############################################################

ds = xr.load_dataset(full_path)
ds.crs
a=ds.crs.crs_wkt
authority_part = a.split('AUTHORITY')[6].strip("[]").replace('"','').replace(',',':')
authority_part = a.split('AUTHORITY')[6].translate(str.maketrans('', '', '[]"')).replace(',', ':')
# Convert xarray DataSet to a (bands, t, x, y) DataArray
data = ds[["B04", "B03", "B02"]].to_array(dim="bands")

fig, axes = plt.subplots(ncols=2, figsize=(8, 3), dpi=600, sharey=True)
data[{"t": 0}].plot.imshow(vmin=0, vmax=2000, ax=axes[0])
data[{"t": 1}].plot.imshow(vmin=0, vmax=2000, ax=axes[1])


def export_geotiff(ds, bands, time_index=0, output_path="exported_t0.tif"):
    """
    Automates the process of assigning CRS and exporting a GeoTIFF for a specific time step.

    Args:
        ds (xarray.Dataset): The input dataset with bands and CRS metadata.
        bands (list): A list of bands to include in the export (e.g., ["B04", "B03", "B02"]).
        time_index (int): The index of the time step to export (default is 0).
        output_path (str): The file path to save the GeoTIFF.

    Returns:
        None: Saves the GeoTIFF to the specified path.
    """
    # Select bands and time slice
    data_t = ds[bands].sel(t=ds.t.values[time_index]).to_array(dim="bands")

    # Extract CRS dynamically
    crs_wkt = ds.crs.attrs.get("crs_wkt")  # CRS in WKT format
    epsg_code = None  # Correct variable name

    # Parse EPSG code from crs_wkt or spatial_ref
    if "AUTHORITY" in crs_wkt:
        epsg_code = crs_wkt.split('AUTHORITY')[6].translate(str.maketrans('', '', '[]"')).replace(',', ':')  # Correctly use crs_wkt
        # Write CRS to data if available
        if epsg_code:
            data_t = data_t.rio.write_crs(str(epsg_code))
        else:
            raise ValueError("CRS information is missing or could not be parsed.")

    # Export to GeoTIFF
    data_t.rio.to_raster(output_path)
    print(f"GeoTIFF successfully exported to: {output_path}")

# Example usage
if __name__ == "__main__":
    # Load the dataset
    full_path = os.path.join(os.getcwd(),"data","pounds.nc")
    ds = xr.load_dataset(full_path)

    # Define the bands to include
    bands = ["B04", "B03", "B02"]  # Red, Green, Blue for true-color

    # Define the output path
    output_path = r"C:\Users\jvila\Desktop\geotransmuter\backend\exportedpounds_t0.tif"

    # Call the function
    export_geotiff(ds, bands, time_index=0, output_path=output_path)
