import os
import openeo
from main_classes import connector
import matplotlib.pyplot as plt
import xarray as xr

connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()

bbox = [-74.242004,-13.168119,-74.220889,-13.152783]
bands = ["B03","B04","B02"]
first_request = connector("4326", 5, "2024-01-01", "2024-12-30",bbox,bands)

first_request.sentinel2_download(connection, "ayacucho.nc")

full_path= os.path.join(os.getcwd(),"data","ayacucho.nc")

from main_classes import Collection

ayacucho = Collection(full_path)

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
