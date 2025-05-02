# -*- coding: utf-8 -*-
"""
Created on Fri May  2 18:56:55 2025

@author: jvila
"""
import os
import glob
import re
import geopandas as gpd
from shapely.geometry import box

"""
dict_keys(['gis_osm_buildings', 'gis_osm_landuse', 'gis_osm_natural',
           'gis_osm_places', 'gis_osm_pofw', 'gis_osm_pois', 'gis_osm_railways',
           'gis_osm_roads', 'gis_osm_traffic', 'gis_osm_transport',
           'gis_osm_waterways', 'gis_osm_water'])

"""

class oms_bucket:
    def __init__(self, data_location):
        self.data_location = data_location
        self.dictionary = None
        self.output = r'C:\Users\jvila\Desktop\geotransmuter\backend\endpoint'
        self.start()
        
    def start(self):
        data_folder = self.data_location

        list_of_shapes = glob.glob(os.path.join(data_folder, "*.shp"))

        # Create a dictionary linking key names to shapefile paths
        self.dictionary = {
            re.match(r"gis_osm_[^_]+", os.path.basename(path)).group(): path
            for path in list_of_shapes if re.match(r"gis_osm_[^_]+", os.path.basename(path))
        }

    def clip_bbox(self, keyname, bbox):
        if keyname not in self.dictionary:
            raise ValueError(f"{keyname} is not found in the dictionary")
        shp_path = self.dictionary[keyname]
        gdf =  gpd.read_file(shp_path)
        
        bbox_polygon = box(*bbox)
        
        clipped_gdf = gdf.clip(bbox_polygon)
        
        # Saved shapefile
        clipped_gdf.to_file(os.path.join(self.output,f"{keyname}.shp"))
    
    def all_clip(self, bbox):
        for key in self.dictionary:
            shp_path = self.dictionary[key]
            gdf = gpd.read_file(shp_path)
            bbox_polygon = box(*bbox)
            clipped_gdf = gdf.clip(bbox_polygon)
            clipped_gdf.to_file(os.path.join(self.output,f"{key}.shp"))
            
            
data_folder = r'C:\Users\jvila\Desktop\geotransmuter\backend\basemap\peru-latest-free.shp'
oms_bucket1 = oms_bucket(data_folder)

ayacucho = (-74.237126,-13.168467,-74.199188,-13.138713)
# oms_bucket1.clip_bbox('gis_osm_waterways', ayacucho)
oms_bucket1.all_clip(ayacucho)

import pyproj
print(pyproj.datadir.get_data_dir())