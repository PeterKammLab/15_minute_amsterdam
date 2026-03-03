# =========================
# Imports
# =========================

import os
import time
import json

import osmnx as ox
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import plotly.express as px
import openrouteservice as ors


# =========================
# Configuration
# =========================

ORS_API_KEY = os.getenv("ORS_API_KEY")  # set this in your system
client = ors.Client(key=ORS_API_KEY)

PLACE = "Amsterdam"
AMENITY = "ice_cream"

TOTAL_TIME = 900  # seconds

TRANSPORT_MODE = "foot-walking"
# TRANSPORT_MODE = "cycling-regular"
# TRANSPORT_MODE = "driving-car"


# =========================
# Time Adjustment Logic
# =========================

def compute_moving_time(mode, total_time):
    slow_foot = 225
    slow_cycle = 180
    prep_foot = 0
    prep_cycle = 180
    prep_drive = 300

    if mode == "foot-walking":
        return total_time - slow_foot - prep_foot

    elif mode == "cycling-regular":
        return total_time - slow_cycle - prep_cycle

    elif mode == "driving-car":
        return total_time - prep_drive

    else:
        raise ValueError("Unsupported transport mode")


MOVING_TIME = compute_moving_time(TRANSPORT_MODE, TOTAL_TIME)


# =========================
# Amenity Extraction
# =========================

def get_coordinates_of_amenities(place, amenity):
    tags = {"amenity": amenity}
    gdf = ox.geometries_from_place(place, tags)

    gdf = gdf[gdf.geometry.type == "Point"]
    coords = [(geom.x, geom.y) for geom in gdf.geometry]

    return coords


# =========================
# Isochrone Calculation
# =========================

def get_isochrones_for_points(coordinates):
    features = []

    for start_index in range(0, len(coordinates), 5):

        # Rate limit protection
        if start_index > 0 and start_index % 20 == 0:
            print("Waiting 61 seconds (rate limit protection)...")
            time.sleep(61)

        print(f"Processing coordinates {start_index} to {start_index + 5}")

        batch = coordinates[start_index:start_index + 5]

        iso = client.isochrones(
            locations=batch,
            profile=TRANSPORT_MODE,
            range=[MOVING_TIME],
            location_type="start",
            smoothing=1,
            validate=False
        )

        features.extend(iso["features"])

    return features


# =========================
# Folium Map Creation
# =========================

def get_map_with_isochrones(features):
    gdf = gpd.GeoDataFrame.from_features(features)

    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    folium.GeoJson(
        gdf,
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "blue",
            "weight": 2,
            "fillOpacity": 0.3,
        },
    ).add_to(m)

    return m


# =========================
# Main Execution
# =========================

def main():
    coordinates = get_coordinates_of_amenities(PLACE, AMENITY)
    isochrone_features = get_isochrones_for_points(coordinates)
    iso_map = get_map_with_isochrones(isochrone_features)

    return iso_map


if __name__ == "__main__":
    iso_map = main()
    iso_map.save("isochrones_map.html")