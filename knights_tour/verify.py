from knights_tour import knights_tour
import time

def valid(path, c, r):
    if len(path) != c * r or len(set(path)) != c * r:
        return False
    return all(sorted((abs(a[0]-b[0]), abs(a[1]-b[1]))) == [1, 2] for a, b in zip(path, path[1:]))

for c, r, sx, sy in [(5,5,2,2),(5,5,1,0),(8,8,0,0),(3,3,0,0),(4,4,0,0),(1,1,0,0),(3,4,0,0),(6,6,3,3),(20,20,5,7),(30,30,0,0)]:
    t = time.time()
    p = knights_tour(c, r, sx, sy)
    print(c, r, sx, sy, "NOT FOUND" if p is None else valid(p, c, r), f"{time.time()-t:.3f}s")
