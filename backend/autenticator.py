# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 23:47:46 2025

@author: jvila
"""

# import openeo

# connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
# connection.authenticate_oidc()

import getpass
import openeo
import configparser
connection = openeo.connect(url="openeo.dataspace.copernicus.eu")

# Initialize a parser
config = configparser.ConfigParser()

# Read the credentials file
config.read(r"C:\Users\jvila\Documents\credentials_copernicus.txt")

# Access the stored values
username = config["DEFAULT"]["client_id"]
password = config["DEFAULT"]["client_secret"]
connection.authenticate_oidc_client_credentials(
    client_id=username,
    client_secret=password,
)

client_sub_id = connection.describe_account()["user_id"]
print(client_sub_id)
