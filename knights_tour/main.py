import sys

MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
NODE_LIMIT = 20_000_000


def build_adjacency(cols, rows):
    adj = {}
    for x in range(cols):
        for y in range(rows):
            adj[(x, y)] = [(x + dx, y + dy) for dx, dy in MOVES
                           if 0 <= x + dx < cols and 0 <= y + dy < rows]
    return adj


def impossible(cols, rows, sx, sy):
    n = cols * rows
    if n == 1:
        return False
    if min(cols, rows) <= 2:
        return True
    if n % 2 == 1 and (sx + sy) % 2 == 1:
        return True
    return False


def knights_tour(cols, rows, sx, sy):
    if impossible(cols, rows, sx, sy):
        return None
    adj = build_adjacency(cols, rows)
    n = cols * rows
    cx, cy = (cols - 1) / 2, (rows - 1) / 2
    start = (sx, sy)
    visited = {start}
    path = [start]
    degree = {k: len(v) for k, v in adj.items()}
    for nb in adj[start]:
        degree[nb] -= 1

    def candidates(pos):
        c = [q for q in adj[pos] if q not in visited]
        c.sort(key=lambda q: (degree[q], -((q[0] - cx) ** 2 + (q[1] - cy) ** 2)))
        return c

    stack = [iter(candidates(start))]
    nodes = 0
    while stack:
        if len(path) == n:
            return path
        nxt = next(stack[-1], None)
        if nxt is None:
            stack.pop()
            last = path.pop()
            visited.discard(last)
            for nb in adj[last]:
                degree[nb] += 1
            continue
        nodes += 1
        if nodes > NODE_LIMIT:
            return None
        visited.add(nxt)
        path.append(nxt)
        for nb in adj[nxt]:
            degree[nb] -= 1
        stack.append(iter(candidates(nxt)))
    return None


def main():
    data = sys.stdin.read().split()
    if len(data) < 4:
        print("usage: input 'cols rows' then 'startx starty'")
        sys.exit(1)
    cols, rows, sx, sy = map(int, data[:4])
    if cols < 1 or rows < 1 or not (0 <= sx < cols and 0 <= sy < rows):
        print("path not found")
        return
    path = knights_tour(cols, rows, sx, sy)
    if path is None:
        print("path not found")
        return
    for x, y in path:
        print(f"{x},{y}")


if __name__ == "__main__":
    main()
