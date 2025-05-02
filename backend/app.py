# -*- coding: utf-8 -*-
"""
Created on Fri May  2 20:26:32 2025

@author: jvila
"""

from flask import Flask, render_template, jsonify
import geopandas as gpd
import os

# Set the custom path to the frontend templates

TEMPLATE_DIR = os.path.abspath(os.path.join(os.getcwd(), '../frontend/templates'))
DATA_DIR = os.path.abspath(os.path.join(os.getcwd(), '../backend/endpoint'))
static_dir = os.path.abspath(os.path.join(os.getcwd(), '../frontend/static'))


app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=static_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/geojson/<layer_name>')
def geojson(layer_name):
    file_path = os.path.join(DATA_DIR, f"{layer_name}.shp")
    if not os.path.exists(file_path):
        return jsonify({"error": "Layer not found"}), 404
    
    gdf = gpd.read_file(file_path)
    return jsonify(gdf.__geo_interface__)

if __name__ == '__main__':
    app.run(debug=True)
