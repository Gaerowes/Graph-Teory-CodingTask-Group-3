# Graph Theory Coding Task — Group 3
## Task 1: Travelling Salesman Problem (SPPG Simulator)

This application prototypes an SPPG mealbox-delivery route planner for schools in Surabaya using OpenStreetMap road and school data.

### Features
- Interactive Streamlit map to select an SPPG location.
- Radius slider to select schools within `x` km of the SPPG.
- Directed road graph from OpenStreetMap.
- Dijkstra shortest-road distances between the SPPG and selected schools.
- Held–Karp exact TSP solver for smaller instances.
- Nearest Neighbour + Or-opt heuristic for larger instances.
- Route overlay, school visiting order, total distance, estimated travel time, and solver execution time.

### Requirements
- Python 3.10 or newer recommended
- Internet connection for the initial OpenStreetMap data download
- OSMnx, NetworkX, Streamlit, Folium, and streamlit-folium

### Setup
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install the required packages directly:
```bash
pip install streamlit streamlit-folium folium osmnx networkx pandas
```

### Run
From the repository root:
```bash
streamlit run tsp/main.py
```

### How to use
1. Wait for the road graph and school locations to load.
2. Click the map to choose an SPPG location.
3. Adjust the delivery radius.
4. Click **Calculate route**.
5. Review the route, visiting order, distance, estimated travel time, and solver time.

### Important notes
- The radius selects schools by straight-line geographic distance from the selected SPPG; route optimization uses directed road-network distances.
- Schools are sourced from OSM features tagged `amenity=school`. OSM coverage and tagging may be incomplete.
- The road graph and school data are cached locally by Streamlit during a running session. The first data download may take time and requires internet access.
- Solver execution time measures the TSP solver only, not OSM download or Dijkstra matrix construction.
- Held–Karp is exact but exponential. The heuristic does not guarantee an optimal solution.
- This is an academic prototype. Verify the OSM data and route before using any route for real-world operations.

### Project structure
```text
Graph-Teory-CodingTask-Group-3/
├── tsp/
│   ├── main.py
│   ├── graph_loader.py
│   ├── school_loader.py
│   ├── routing.py
│   └── tsp_solver.py
└── README.md
```
