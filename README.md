# Graph-Teory-CodingTask-Group-3
 
## 1. Identity
**Informatics ITS Graph Theory class Group 3**
 
* Dzulfiqar Rafi'ussunnah - 5025251011
* Padhang Abiyu Fikri - 5025251014
* Aditya Lingga Mardika - 5025251158
* Muhammad Faris Alfarrel - 5025251002
## 2. Task 3: Knight's Tour
 
Given a chessboard of `cols x rows` squares and a starting square, find a sequence of legal knight moves that visits every square exactly once. If no such sequence exists, the program prints `path not found`.
 
Coordinates are `(column, row)`, 0-indexed, matching the assignment grid (`0,0` is the top-left square).
 
## 3. Algorithm
 
| Problem | Algorithm | Main Objective |
|---|---|---|
| Knight's Tour | Iterative depth-first backtracking with Warnsdorff's rule | Visit every chessboard square exactly once |
 
- **Warnsdorff's rule:** from the current square, try the unvisited neighbour with the fewest onward moves first. Ties are broken by preferring squares farther from the board centre. Neighbour degrees are updated incrementally, so each step costs O(1).
- **Backtracking:** if a dead end is reached, the last move is undone and the next candidate is tried, so the search is exhaustive and `path not found` is exact.
- **Early rejection:** no tour exists when one board side is 2 or less (and the board has more than one square), or when the board has an odd number of squares and the starting square has an odd `column + row`.
- **Search limit:** the search stops after 20,000,000 nodes and prints `path not found` (only relevant for very large boards).
- **Iterative search:** an explicit stack is used instead of recursion, so large boards do not hit Python's recursion limit.
## 4. Prerequisites
 
- Python 3.8 or newer (no external packages)
- Git
## 5. Repository Structure
 
```text
Graph-Teory-CodingTask-Group-3/
├── tsp/
│   └── main.py
├── cpp/
│   └── main.py
├── knights_tour/
│   ├── main.py
│   ├── verify.py
│   └── input.txt
└── README.md
```
 
## 6. Installation
 
```bash
git clone https://github.com/Gaerowes/Graph-Teory-CodingTask-Group-3.git
cd Graph-Teory-CodingTask-Group-3/knights_tour
```
 
No dependencies need to be installed.
 
## 7. How to Run
 
Input format (two lines):
 
```text
<cols> <rows>
<start_col> <start_row>
```
 
**Windows (PowerShell)**
 
```powershell
"5 5`n2 2" | python main.py
```
 
or from a file:
 
```powershell
Get-Content input.txt | python main.py
```
 
**Linux / macOS / Git Bash**
 
```bash
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
 
## 8. Sample Cases
 
### Sample 1: tour found
 
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
 
### Sample 2: no tour exists
 
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
 
### Other tested cases
 
| Input (cols rows / start) | Result |
|---|---|
| 8 8 / 0 0 | tour found |
| 6 6 / 3 3 | tour found |
| 3 4 / 0 0 | tour found |
| 20 20 / 5 7 | tour found |
| 30 30 / 0 0 | tour found |
| 3 3 / 0 0 | path not found |
| 4 4 / 0 0 | path not found |
 
## 9. Computational Complexity
 
Let `N = cols x rows`.
 
| Case | Time | Space |
|---|---|---|
| Warnsdorff, no backtracking | O(N) | O(N) |
| Worst case with backtracking | O(8^N) | O(N) |
 
Each step inspects at most 8 moves, each with at most 8 degree checks, so a step is O(1). The exponential bound applies only when the search must be exhausted (no tour) or backtracks heavily. See the PDF report for the full analysis.
 
## 10. Acknowledgment
 
Prepared as part of the Graph Theory course at Institut Teknologi Sepuluh Nopember (ITS).
