"""Load school points from OpenStreetMap and select by radius."""
import osmnx as ox
import pandas as pd
import streamlit as st

# Give Overpass more time for a city-sized query. This does not guarantee
# availability if the public server is overloaded.
ox.settings.requests_timeout = 180
ox.settings.overpass_rate_limit = True


@st.cache_data(show_spinner=False, ttl=24 * 60 * 60)
def load_schools(place: str = "Surabaya, East Java, Indonesia") -> pd.DataFrame:
    """Return OSM school point features; cache successful results for 24 hours."""
    tags = {"amenity": "school"}
    gdf = ox.features_from_place(place, tags)

    if gdf.empty:
        return pd.DataFrame(columns=["name", "lat", "lon", "osm_id"])

    gdf = gdf[gdf.geometry.notna()].copy()
    gdf["geometry"] = gdf.geometry.representative_point()
    gdf = gdf[gdf.geometry.geom_type == "Point"].copy()

    rows = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        name = row.get("name")
        if not isinstance(name, str) or not name.strip():
            name = f"School {idx}"
        rows.append({
            "name": name.strip(),
            "lat": float(geom.y),
            "lon": float(geom.x),
            "osm_id": str(idx),
        })

    return pd.DataFrame(rows).drop_duplicates(subset=["osm_id"]).reset_index(drop=True)


def select_schools(schools: pd.DataFrame, base_lat: float, base_lon: float, radius_km: float):
    """Select schools within a straight-line radius from the SPPG point."""
    if schools.empty:
        return schools.copy()

    from math import radians, sin, cos, asin, sqrt

    def haversine(lat, lon):
        lat1, lat2 = radians(base_lat), radians(lat)
        dlat = lat2 - lat1
        dlon = radians(lon - base_lon)
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371.0088 * 2 * asin(sqrt(min(1.0, a)))

    result = schools.copy()
    result["radius_km"] = result.apply(
        lambda row: haversine(row["lat"], row["lon"]), axis=1
    )
    return result[result["radius_km"] <= radius_km].reset_index(drop=True)
