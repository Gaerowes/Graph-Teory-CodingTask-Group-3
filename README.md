# Graph-Teory-CodingTask-Group-3

## 1. Identity
**Informatics ITS Graph Theory class Group 3**

* Padhang Abiyu Fikri - 5025251014
* Dzulfiqar Rafi'ussunnah - 5025251011
* Aditya Lingga Mardika - 5025251158
* Muhammad Faris Alfarrel - 5025251002



## Project Overview

This project implements solutions for the following problems:

### 1. Travelling Salesman Problem (TSP)

Find a minimum-cost tour that starts at a selected location, visits every location exactly once, and returns to the starting location.

### 2. Chinese Postman Problem (CPP)

Find an efficient route for a dump truck that starts and ends at its base and traverses the required road segments within a specified radius. Road segments may be revisited when necessary.

### 3. Knight's Tour

Find a sequence of legal knight moves that visits every square on a chessboard exactly once.

## Algorithms

The algorithms used for each problem are documented below.

| Problem | Algorithm | Main Objective |
|---|---|---|
| TSP | [Algorithm to be determined] | Minimize the total tour cost |
| CPP | Minimum-cost flow and Eulerian circuit | Traverse the required roads and return to the base |
| Knight's Tour | Iterative depth-first backtracking with Warnsdorff's rule | Visit every chessboard square exactly once |

### TSP

[To be filled in]

### CPP

- **Road selection:** load Surabaya roads from OpenStreetMap and select trunk,
  primary, secondary and tertiary roads within the chosen radius.
- **Road directions:** use a directed graph, so one-way roads are followed correctly.
- **Connecting roads:** add shortest road paths where necessary to connect the
  selected roads to the base.
- **Graph balancing:** repeat the cheapest directed roads until every vertex has
  the same number of incoming and outgoing traversals.
- **Eulerian circuit:** visit every selected road and return to the base.

The app shows the route, street order, total distance, estimated travel time and
CPP solver time. Connecting paths can leave the radius. The route is optimal for
the connected graph used by the solver; the connector choice is a heuristic.


### Knight's Tour

- **Warnsdorff's rule:** from the current square, try the unvisited neighbour with the fewest onward moves first. Ties are broken by preferring squares farther from the board centre. Neighbour degrees are updated incrementally, so each step costs O(1).
- **Backtracking:** if a dead end is reached, the last move is undone and the next candidate is tried, so the search is exhaustive and `path not found` is exact.
- **Early rejection:** no tour exists when one board side is 2 or less (and the board has more than one square), or when the board has an odd number of squares and the starting square has an odd `column + row`.
- **Search limit:** the search stops after 20,000,000 nodes and prints `path not found` (only relevant for very large boards).
- **Iterative search:** an explicit stack is used instead of recursion, so large boards do not hit Python's recursion limit.

Coordinates are `(column, row)`, 0-indexed, matching the assignment grid (`0,0` is the top-left square).

## Prerequisites

- Python 3.8 or newer
- Git

Dependencies per problem:

| Problem | Additional dependencies |
|---|---|
| TSP | [To be filled in] |
| CPP | OSMnx, NetworkX, Streamlit, streamlit-folium, Folium |
| Knight's Tour | None (standard library only) |

## Repository Structure

```text
Graph-Teory-CodingTask-Group-3/
├── tsp/
│   └── main.py
├── cpp/
│   ├── main.py
│   └── requirements.txt
├── knights_tour/
│   ├── main.py
│   ├── verify.py
│   └── input.txt
└── README.md
```

The directory and file names may be adjusted to match the final implementation.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Gaerowes/Graph-Teory-CodingTask-Group-3.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Graph-Teory-CodingTask-Group-3
   ```

3. Install the required dependencies, if any:

   - TSP: [To be filled in]
   - CPP: `pip install -r cpp/requirements.txt`
   - Knight's Tour: nothing to install

## How to Run

### TSP

```bash
python tsp/main.py
```

[To be filled in]

### CPP

```bash
streamlit run cpp/main.py
```

Open the local URL, click the map to choose the base, set the radius and average
speed, then click **Calculate route**. An internet connection is needed to load
OpenStreetMap roads.

### Knight's Tour

Input format (two lines):

```text
<cols> <rows>
<start_col> <start_row>
```

**Windows (PowerShell)**

```powershell
cd knights_tour
"5 5`n2 2" | python main.py
```

or from a file:

```powershell
Get-Content input.txt | python main.py
```

**Linux / macOS / Git Bash**

```bash
cd knights_tour
printf "5 5\n2 2\n" | python3 main.py
```

or from a file:

```bash
python3 main.py < input.txt
```

Run the self-checks (validates each tour and tests cases with no solution):

```bash
python verify.py
```

## Sample Cases

### TSP

- **Input:** A set of locations and the travel cost between each pair.
- **Expected output:** A minimum-cost tour and its total cost.

[Sample input and output to be filled in]

### CPP

- **Input:** a Surabaya base, `1 km` radius and `25 km/h` average speed.
- **Output:** a closed route, street traversal order, total distance, estimated
  travel time and CPP solver time. Exact values depend on OpenStreetMap data.

### Knight's Tour

- **Input:** Chessboard dimensions and a starting square.
- **Expected output:** A sequence of legal knight moves that visits each square exactly once, if a solution exists.

**Sample 1: tour found**

Input:

```text
5 5
2 2
```

Output (25 squares, in visiting order):

```text
2,2
3,4
4,2
3,0
1,1
0,3
2,4
4,3
3,1
1,0
0,2
1,4
3,3
4,1
2,0
0,1
1,3
3,2
4,4
2,3
0,4
1,2
0,0
2,1
4,0
```

**Sample 2: no tour exists**

Input:

```text
5 5
1 0
```

Output:

```text
path not found
```

The board has 25 squares (odd) and the start square has `1 + 0` odd, so no tour exists.

**Other tested cases**

| Input (cols rows / start) | Result |
|---|---|
| 8 8 / 0 0 | tour found |
| 6 6 / 3 3 | tour found |
| 3 4 / 0 0 | tour found |
| 20 20 / 5 7 | tour found |
| 30 30 / 0 0 | tour found |
| 3 3 / 0 0 | path not found |
| 4 4 / 0 0 | path not found |

## Computational Complexity

The computational complexity of each algorithm is discussed in the final report, together with its implementation details and performance analysis.

| Problem | Time | Space |
|---|---|---|
| TSP | [To be filled in] | [To be filled in] |
| CPP | Shortest paths and minimum-cost flow dominate; Eulerian circuit O(E) | O(V+E+A) |
| Knight's Tour | O(N) typical with Warnsdorff, O(8^N) worst case (N = cols x rows) | O(N) |

For CPP, V is the number of nodes, E is the number of roads, and A is the
number of repeated roads. Minimum-cost flow has no simple fixed runtime bound
for this implementation.

## Project Deliverables

- Source code for all three problems.
- README documentation.
- A PDF report explaining the algorithmic approaches, implementations, and computational complexities.
- A live demonstration of the programs.

## Acknowledgment

Prepared as part of the Graph Theory course at Institut Teknologi Sepuluh Nopember (ITS).
