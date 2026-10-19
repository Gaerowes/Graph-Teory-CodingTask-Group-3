# Graph Theory Coding Task — Group 3

## Task 1: Travelling Salesman Problem (SPPG Simulator)

This application prototypes an SPPG mealbox-delivery route planner for schools in Surabaya using OpenStreetMap (OSM) road and school data.

### Features

- Interactive Streamlit map to select an SPPG location.
- Radius slider to select schools within `x` km of the SPPG.
- Directed road graph from OpenStreetMap.
- Dijkstra's algorithm to calculate shortest-road distances between the SPPG and selected schools.
- Held–Karp exact TSP solver for smaller instances.
- Nearest Neighbour + Or-opt heuristic for larger instances.
- Route visualization, school visiting order, total road distance, estimated travel time, and solver execution time.

### Requirements

- Python 3.10 or newer.
- Internet connection for the initial OpenStreetMap data download.
- Required Python packages: Streamlit, OSMnx, NetworkX, Folium, streamlit-folium, pandas, and scikit-learn.

### Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
python -m pip install streamlit streamlit-folium folium osmnx networkx pandas scikit-learn
```

### Run

From the repository root, run:

```bash
python -m streamlit run tsp/main.py
```

### How to Use

1. Wait for the road graph and school locations to load.
2. Click the map to select an SPPG location.
3. Adjust the delivery radius.
4. Click **Calculate route**.
5. Review the route visualization, school visiting order, total road distance, estimated travel time, and solver execution time.

### Important Notes

- The radius selects schools based on straight-line geographic distance from the selected SPPG. Route optimization uses directed road-network distances.
- School locations are sourced from OSM features tagged `amenity=school`. OSM coverage and tagging may be incomplete.
- Road and school data are cached by Streamlit. Initial downloads may take time and require an internet connection.
- OpenStreetMap data requests may occasionally fail because of server availability or request limits.
- Estimated travel time uses an average speed of 25 km/h. It does not account for live traffic conditions.
- Solver execution time measures the TSP solver only, excluding OSM data downloads and distance-matrix construction.
- Held–Karp finds an optimal solution for the modeled instance but has exponential time complexity. The Nearest Neighbour + Or-opt heuristic is intended for larger instances but does not guarantee an optimal solution.
- This is an academic prototype. Verify the OSM data and route before using them for real-world operations.

### Project Structure

```text
Graph-Teory-CodingTask-Group-3/
├── tsp/
│   ├── main.py
│   ├── graph_loader.py
│   ├── school_loader.py
│   ├── routing.py
│   └── tsp_solver.py
├── .gitignore
└── README.md
```

