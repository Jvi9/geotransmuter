
import os

"""
#	name	type	labels	resolution	reference system
1	x	spatial	466380, 466580, 466780, 466980, 467180, 467380	200m	EPSG:32627(opens new window)
2	y	spatial	7167130, 7166930, 7166730, 7166530, 7166330, 7166130, 7165930	200m	EPSG:32627(opens new window)
3	bands	bands	blue, green, red, nir	4 bands	-
4	t	temporal	2020-10-01, 2020-10-13, 2020-10-25	12 days	Gregorian calendar / UTC
geometry	vector	POLYGON((-122.4 37.6,-122.35 37.6,-122.35 37.64,-122.4 37.64,-122.4 37.6)), POLYGON((-122.51 37.5,-122.48 37.5,-122.48 37.52,-122.51 37.52,-122.51 37.5))	EPSG:4326

https://openeo.org/documentation/1.0/processes.html#save_result

"""

class connector:
    def __init__(self, crs:str, max_cloud_cover:int, start_time:str, last_time:str,bbox="",bands:list=""):
      
        self.bbox = bbox
        self.crs = crs
        self.max_cloud_cover = max_cloud_cover
        self.start_time = start_time
        self.last_time = last_time
        self.bands = bands
        self.bbox = bbox
        if not self.bands:
            self.default_bands()            
        
        if self.bbox:
            self.set_datacube_limits()
        else:
            raise("Datacube limits bbox missing!")
        
    def set_datacube_limits(self):
        """
        Converts a flat list of coordinates bbox format into a spatial extent dictionary.
        Returns:
            self: keys 'west', 'south', 'east', and 'north'.
        """
        self.west = self.bbox[0]
        self.south = self.bbox[1]
        self.east = self.bbox[2]
        self.north = self.bbox[3]

    def default_bands(self):
        bands_default = ["B02", "B03", "B04", "B08", "SCL"]
        self.bands = bands_default
        
    def sentinel2_download(self, connection, data_name):
        s2_cube = connection.load_collection(
            "SENTINEL2_L2A",
            temporal_extent=(self.start_time, self.last_time),
            spatial_extent={
                "west": self.west,
                "south": self.south,
                "east": self.east,
                "north": self.north,
                "crs": str(f"EPSG:{self.crs}"),
            },
            # bands=["B04"],
            bands=self.bands,
            max_cloud_cover=self.max_cloud_cover,
        )
        
        path_name = os.path.join(os.getcwd(),"data",data_name)
        
        s2_cube.download(path_name)
        print(f"The dataset has been downloaded in {path_name}")

class Collection():

    def __init__(self, file_path:str):
        self.file_path = file_path
        self.ini_xarray()
        
    def ini_xarray(self):
        import xarray
        self.ds=xarray.load_dataset(self.file_path)
    
    def calculate_ndwi(self):
        #Creating NDWI
        ds = self.ds
        green = ds["B03"]  # Green band
        nir = ds["B08"]    # Near-infrared band
        ds['ndwi'] = (green - nir) / (green + nir)
        ds['ndwi'] =  ds['ndwi'].where((green + nir) != 0)
    
    def plot_ndwi(self, vmin=-1, vmax=1):
        import math
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        
        cmap = LinearSegmentedColormap.from_list("GreenToBlue", ["green", "blue"])

        
        time_steps = self.ds.t.values  # Get all time steps
        num_time_steps = len(time_steps)
        
        # Determine the grid size (e.g., 4 columns)
        cols = 4  # Number of columns in the subplot grid
        rows = math.ceil(num_time_steps / cols)  # Number of rows needed
        
        # Create the subplots
        fig, axes = plt.subplots(
            nrows=rows, ncols=cols, figsize=(cols * 5, rows * 5), dpi=150
        )
        
        # Flatten the axes array for easy iteration
        axes = axes.flatten()

        # Loop through each time step
        for i, t in enumerate(time_steps):
            ndwi_t = self.ds["ndwi"].sel(t=t)  # Select NDWI at this time step
            ndwi_t.plot(ax=axes[i], cmap=cmap, vmin=vmin, vmax=vmax)
            axes[i].set_title(f"NDWI: {str(t)[:10]}")  # Add date as the title
        
        # Hide unused subplots
        for j in range(num_time_steps, len(axes)):
            axes[j].axis("off")

        # Adjust layout
        plt.tight_layout()
        plt.show()
        

# =============================================================================
# Playground
# =============================================================================


