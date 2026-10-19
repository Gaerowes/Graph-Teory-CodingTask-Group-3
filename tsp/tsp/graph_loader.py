"""Load and cache the directed Surabaya street network from OpenStreetMap."""
import osmnx as ox
import streamlit as st

SURABAYA_PLACE = "Surabaya, East Java, Indonesia"


@st.cache_data(show_spinner=False)
def load_road_graph(place: str = SURABAYA_PLACE):
    """Download a drivable directed MultiDiGraph and add edge lengths."""
    graph = ox.graph_from_place(
        place,
        network_type="drive",
        simplify=True,
        retain_all=False,
        truncate_by_edge=True,
    )
    graph = ox.distance.add_edge_lengths(graph)
    return graph
