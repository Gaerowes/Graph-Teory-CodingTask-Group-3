"""Surabaya dump truck route (Chinese Postman Problem)."""
from time import perf_counter

import folium
import networkx as nx
import osmnx as ox
import streamlit as st
from shapely.geometry import LineString, Point
from streamlit_folium import st_folium

ROAD_TYPES = {"trunk", "primary", "secondary", "tertiary"}


@st.cache_resource
def load_city():
    """Download Surabaya once and reuse it when the base or radius changes."""
    ox.settings.use_cache = True
    roads = ox.graph_from_place("Surabaya, East Java, Indonesia",
                                network_type="drive", retain_all=True)
    return ox.project_graph(roads)


def get_roads(lat, lon, radius_km):
    """Select major roads near the base and connect them by drivable roads."""
    city = load_city()
    point, _ = ox.projection.project_geometry(
        Point(lon, lat), to_crs=city.graph["crs"])
    circle = point.buffer(radius_km * 1000)
    base = min(city, key=lambda n: point.distance(
        Point(city.nodes[n]["x"], city.nodes[n]["y"])))

    component = next(c for c in nx.strongly_connected_components(city) if base in c)
    city = city.subgraph(component)
    required = []
    for u, v, key, data in city.edges(keys=True, data=True):
        highway = data.get("highway", "")
        highway = highway if isinstance(highway, list) else [highway]
        if not any(h.replace("_link", "") in ROAD_TYPES for h in highway):
            continue
        shape = data.get("geometry")
        if shape is None:
            shape = LineString([(city.nodes[u]["x"], city.nodes[u]["y"]),
                                (city.nodes[v]["x"], city.nodes[v]["y"])])
        if shape.intersects(circle):
            required.append((u, v, key))

    if not required:
        raise ValueError("No reachable major roads in this radius.")
    route_graph = city.edge_subgraph(required).copy()
    route_graph.add_node(base, **city.nodes[base])

    # Join each disconnected group to the base using real one-way roads.
    for nodes in list(nx.strongly_connected_components(route_graph)):
        node = next(iter(nodes))
        for path in (nx.shortest_path(city, base, node, weight="length"),
                     nx.shortest_path(city, node, base, weight="length")):
            for u, v in zip(path, path[1:]):
                key = min(city[u][v], key=lambda k: city[u][v][k]["length"])
                route_graph.add_node(u, **city.nodes[u])
                route_graph.add_node(v, **city.nodes[v])
                if not route_graph.has_edge(u, v, key):
                    route_graph.add_edge(u, v, key=key, **city[u][v][key])
    return route_graph, base, len(required)


def solve_cpp(graph, base):
    """Repeat the cheapest directed arcs and follow an Eulerian circuit."""
    started = perf_counter()
    flow = nx.DiGraph()
    tour = nx.MultiDiGraph(graph)
    for node in graph:
        flow.add_node(node, demand=graph.out_degree(node) - graph.in_degree(node))
    for u, v, key, data in graph.edges(keys=True, data=True):
        cost = max(1, round(data["length"] * 1000))
        if not flow.has_edge(u, v) or cost < flow[u][v]["weight"]:
            flow.add_edge(u, v, weight=cost, key=key)
    for u, targets in nx.min_cost_flow(flow).items():
        for v, count in targets.items():
            for _ in range(count):
                key = flow[u][v]["key"]
                tour.add_edge(u, v, **graph[u][v][key])
    order = list(nx.eulerian_circuit(tour, source=base, keys=True))
    distance = sum(tour[u][v][key]["length"] for u, v, key in order)
    return tour, order, distance, perf_counter() - started


def show_route(graph, order):
    """Turn a route into map points and numbered street names."""
    graph = ox.project_graph(graph, to_crs="EPSG:4326")
    points, streets = [], []
    for number, (u, v, key) in enumerate(order, 1):
        data = graph[u][v][key]
        shape = data.get("geometry")
        segment = ([(y, x) for x, y in shape.coords] if shape is not None else
                   [(graph.nodes[n]["y"], graph.nodes[n]["x"]) for n in (u, v)])
        if segment[-1] == (graph.nodes[u]["y"], graph.nodes[u]["x"]):
            segment.reverse()
        points.extend(segment)
        streets.append({"Order": number, "Street": str(data.get("name", "Unnamed")),
                        "Distance (m)": round(data["length"], 1)})
    return points, streets


st.set_page_config(page_title="CPP Surabaya", layout="wide")
st.title("Surabaya Dump Truck Route")
st.write("Click the map to choose a base, select a radius, then calculate.")

if "base" not in st.session_state:
    st.session_state.base = (-7.2575, 112.7521)
with st.sidebar:
    radius = st.slider("Radius (km)", 0.5, 5.0, 1.0, 0.5)
    speed = st.number_input("Average speed (km/h)", 1, 100, 25)
    calculate = st.button("Calculate route")

if st.session_state.get("settings") != (st.session_state.base, radius):
    st.session_state.pop("result", None)
if calculate:
    try:
        with st.spinner("Downloading roads and calculating..."):
            lat, lon = st.session_state.base
            roads, base, required = get_roads(lat, lon, radius)
            tour, order, distance, seconds = solve_cpp(roads, base)
            points, streets = show_route(tour, order)
            st.session_state.result = (points, streets, distance, seconds, required)
            st.session_state.settings = (st.session_state.base, radius)
    except Exception as error:
        st.error(f"Could not calculate route: {error}")

result = st.session_state.get("result")
route_map = folium.Map(location=st.session_state.base, zoom_start=13)
folium.Marker(st.session_state.base, tooltip="Selected base").add_to(route_map)
folium.Circle(st.session_state.base, radius=radius * 1000).add_to(route_map)
if result:
    folium.PolyLine(result[0], color="red", weight=5).add_to(route_map)
clicked = st_folium(route_map, height=550, use_container_width=True,
                    returned_objects=["last_clicked"]).get("last_clicked")
if clicked:
    new_base = (clicked["lat"], clicked["lng"])
    if new_base != st.session_state.base:
        st.session_state.base = new_base
        st.session_state.pop("result", None)
        st.rerun()

if result:
    points, streets, distance, seconds, required = result
    a, b, c = st.columns(3)
    a.metric("Total distance", f"{distance / 1000:.2f} km")
    b.metric("Estimated travel time", f"{distance / 1000 / speed * 60:.1f} min")
    c.metric("CPP solver time", f"{seconds:.4f} s")
    st.write(f"Required directed road segments: {required}")
    st.dataframe(streets, hide_index=True, use_container_width=True)
