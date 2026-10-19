"""Streamlit SPPG Simulator — Task 1: Travelling Salesman Problem."""
import math
import time
import streamlit as st
import folium
from streamlit_folium import st_folium

from graph_loader import load_road_graph, SURABAYA_PLACE
from school_loader import load_schools, select_schools
from routing import (
    snap_points_to_nodes,
    build_distance_matrix,
    expand_tour_to_nodes,
    road_nodes_to_latlon,
)
from tsp_solver import solve_tsp

st.set_page_config(page_title="SPPG TSP Simulator", layout="wide")
st.title("SPPG Simulator — Travelling Salesman Problem")
st.caption("OpenStreetMap data • Directed road network • Shortest-road-distance TSP")

st.info(
    "Choose an SPPG by clicking the map, set the radius, then calculate a round-trip "
    "route visiting every OSM school in that radius. First-time OSM downloads need internet."
)

with st.sidebar:
    st.header("Simulation settings")
    radius_km = st.slider("School radius x (km)", min_value=1, max_value=20, value=5, step=1)
    st.caption("Radius is straight-line distance from the selected SPPG. Route costs use road distances.")
    place = st.text_input("OSM area", value=SURABAYA_PLACE)
    max_exact_points = st.number_input(
        "Maximum points for exact Held–Karp (including SPPG)",
        min_value=3, max_value=17, value=16, step=1,
        help="Held–Karp grows exponentially. Larger instances use the heuristic."
    )

if "sppg_location" not in st.session_state:
    st.session_state.sppg_location = (-7.2575, 112.7521)  # central Surabaya default

def load_with_retry(loader, place_name, label, attempts=4):
    """Retry transient OSM/Overpass failures with exponential backoff."""
    last_error = None
    for attempt in range(attempts):
        try:
            return loader(place_name)
        except Exception as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            wait_seconds = 2 ** (attempt + 1)  # 2, 4, then 8 seconds
            st.warning(
                f"{label} gagal dimuat (percobaan {attempt + 1}/{attempts}). "
                f"Mencoba lagi dalam {wait_seconds} detik."
            )
            time.sleep(wait_seconds)
    raise RuntimeError(
        f"{label} tidak berhasil dimuat setelah {attempts} percobaan. "
        "Server Overpass mungkin sedang penuh (misalnya HTTP 502). "
        "Tunggu beberapa menit lalu klik Rerun; hindari refresh berulang kali."
    ) from last_error


try:
    with st.spinner("Loading road network from OpenStreetMap. First load may take a while..."):
        graph = load_with_retry(load_road_graph, place, "Jaringan jalan OSM")
    with st.spinner("Loading school locations from OpenStreetMap..."):
        schools = load_with_retry(load_schools, place, "Data sekolah OSM")
except Exception as exc:
    st.error(str(exc))
    st.info(
        "Ini biasanya gangguan sementara pada server data OSM, bukan kesalahan algoritma TSP. "
        "Coba lagi nanti. Data yang berhasil dimuat akan di-cache oleh aplikasi."
    )
    with st.expander("Detail teknis error"):
        st.exception(exc)
    st.stop()

base_lat, base_lon = st.session_state.sppg_location
filtered = select_schools(schools, base_lat, base_lon, float(radius_km))

left, right = st.columns([1.5, 1])
with left:
    st.subheader("Select SPPG location")
    base_map = folium.Map(location=[base_lat, base_lon], zoom_start=12, control_scale=True)
    folium.Marker(
        [base_lat, base_lon],
        tooltip="Selected SPPG",
        popup="SPPG",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(base_map)

    # Show candidate schools in radius.
    for _, school in filtered.iterrows():
        folium.CircleMarker(
            [school["lat"], school["lon"]],
            radius=4,
            tooltip=school["name"],
            color="#2471A3",
            fill=True,
            fill_opacity=0.8,
        ).add_to(base_map)

    map_result = st_folium(
        base_map,
        height=520,
        width=None,
        returned_objects=["last_clicked"],
        key="sppg_picker_map",
    )

    if map_result and map_result.get("last_clicked"):
        clicked = map_result["last_clicked"]
        if clicked.get("lat") is not None and clicked.get("lng") is not None:
            new_loc = (float(clicked["lat"]), float(clicked["lng"]))
            if new_loc != st.session_state.sppg_location:
                st.session_state.sppg_location = new_loc
                st.rerun()

with right:
    st.subheader("Current selection")
    st.metric("Schools within radius", len(filtered))
    st.write(f"SPPG coordinates: `{base_lat:.5f}, {base_lon:.5f}`")
    st.write(f"Search radius: **{radius_km} km**")
    st.caption("Click anywhere on the map to move the SPPG marker.")

    calculate = st.button("Calculate route", type="primary", use_container_width=True)

if calculate:
    if filtered.empty:
        st.warning("No OSM schools were found within this radius. Increase the radius or move the SPPG.")
        st.stop()

    # Build points: SPPG at index 0, then each school.
    points = [{"name": "SPPG", "lat": base_lat, "lon": base_lon}]
    for _, school in filtered.iterrows():
        points.append({
            "name": str(school["name"]),
            "lat": float(school["lat"]),
            "lon": float(school["lon"]),
        })

    # Avoid huge exact instances; keep selected schools with unique snapped road nodes.
    with st.spinner("Snapping SPPG and schools to road nodes and running Dijkstra..."):
        node_ids = snap_points_to_nodes(graph, points)

        # If multiple points snap to the same road node, they are still distinct visits,
        # but the solver can handle zero-cost legs. No deduplication is done.
        distances, leg_paths = build_distance_matrix(graph, node_ids)

    # Detect schools unreachable from/to the SPPG.
    reachable_indices = [
        0
    ] + [
        i for i in range(1, len(points))
        if math.isfinite(distances[0][i]) and math.isfinite(distances[i][0])
    ]
    omitted = len(points) - len(reachable_indices)

    if omitted:
        st.warning(
            f"{omitted} school(s) have no directed road path both from and back to the SPPG "
            "and were excluded from this route."
        )

    if len(reachable_indices) <= 1:
        st.error("No schools have a valid directed road round trip from the selected SPPG.")
        st.stop()

    # Rebuild a compact matrix for only reachable points.
    compact_distances = [
        [distances[i][j] for j in reachable_indices]
        for i in reachable_indices
    ]
    solver_limit = int(max_exact_points)

    with st.spinner("Optimizing school visit order..."):
        result = solve_tsp(compact_distances, exact_limit=solver_limit)

    if result["tour"] is None or not math.isfinite(result["distance_m"]):
        st.error("No complete round-trip TSP route could be found for the selected schools.")
        st.stop()

    # Map compact indices back to original points and expand shortest-road legs.
    original_tour = [reachable_indices[i] for i in result["tour"]]
    expanded_nodes = expand_tour_to_nodes(original_tour, leg_paths)

    if not expanded_nodes:
        st.error("The solver returned a tour, but a road path could not be expanded.")
        st.stop()

    route_coords = road_nodes_to_latlon(graph, expanded_nodes)
    total_km = result["distance_m"] / 1000.0

    # Estimate driving time using a simple configurable average; this is not live traffic.
    average_speed_kmh = 25.0
    estimated_minutes = total_km / average_speed_kmh * 60.0

    st.divider()
    st.subheader("Route results")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total road distance", f"{total_km:.2f} km")
    m2.metric("Estimated travel time", f"{estimated_minutes:.0f} min", help="Estimate using 25 km/h average; not live traffic.")
    m3.metric("Solver execution time", f"{result['solver_seconds']:.6f} s")
    st.caption(f"Solver: {result['algorithm']} • OSM school features: amenity=school")

    visit_names = [points[i]["name"] for i in original_tour]
    closed_names = visit_names + ["SPPG"]
    st.markdown("**School visiting order**")
    st.write(" → ".join(closed_names))

    result_map = folium.Map(
        location=[base_lat, base_lon],
        zoom_start=12,
        control_scale=True,
    )
    folium.PolyLine(
        route_coords,
        color="blue",
        weight=5,
        opacity=0.85,
        tooltip="Optimized road route",
    ).add_to(result_map)

    for order, idx in enumerate(original_tour):
        point = points[idx]
        if idx == 0:
            folium.Marker(
                [point["lat"], point["lon"]],
                tooltip="SPPG (start/end)",
                icon=folium.Icon(color="red", icon="home"),
            ).add_to(result_map)
        else:
            folium.Marker(
                [point["lat"], point["lon"]],
                tooltip=f"{order}. {point['name']}",
                popup=f"Visit {order}: {point['name']}",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(result_map)

    st_folium(
    result_map,
    height=600,
    width=None,
    key="route_result_map",
    returned_objects=[],
)
    with st.expander("Technical details"):
        st.write(f"Total points in solver: {len(reachable_indices)} including SPPG")
        st.write(f"Road graph: {len(graph.nodes):,} nodes, {len(graph.edges):,} directed edges")
        st.write("Distance matrix: shortest directed road distance in metres, computed before solver timing.")
        st.write("The route can reuse road segments between school stops, as permitted by the assignment.")
