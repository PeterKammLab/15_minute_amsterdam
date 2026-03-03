# =========================
# Imports
# =========================

import osmnx as ox
import geopandas as gpd


# =========================
# Bounding Box Definition
# =========================

# lon, lat
upper_left = [4.7852, 52.5058]
lower_right = [5.0237, 52.3602]


# =========================
# Load Leisure Data from OSM
# =========================

north = upper_left[1]
south = lower_right[1]
east = lower_right[0]
west = upper_left[0]

tags = {"leisure": True}

leisure_data = ox.features_from_bbox(
    north=north,
    south=south,
    east=east,
    west=west,
    tags=tags
)

leisure_data.reset_index(inplace=True)


# =========================
# Inspect Available Leisure Types
# =========================

print(leisure_data["leisure"].dropna().unique())


# =========================
# Filter: Only Parks
# =========================

parks = leisure_data[leisure_data["leisure"] == "park"]


# =========================
# Separate Geometry Types
# =========================

parks_polygon = parks[parks.geometry.type == "Polygon"]
parks_point = parks[parks.geometry.type == "Point"]


# =========================
# Export to Shapefiles
# =========================

parks_polygon[["osmid", "geometry"]].to_file(
    "parks_polygon.shp",
    driver="ESRI Shapefile"
)

parks_point[["osmid", "geometry"]].to_file(
    "parks_point.shp",
    driver="ESRI Shapefile"
)

print("Export complete.")