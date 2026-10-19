"""TSP solvers for directed/asymmetric distance matrices."""
from math import inf
from time import perf_counter


def tour_cost(tour, distances):
    total = 0.0
    for i in range(len(tour)):
        a, b = tour[i], tour[(i + 1) % len(tour)]
        cost = distances[a][b]
        if cost == inf:
            return inf
        total += cost
    return total


def held_karp(distances):
    """Exact Held–Karp solver. Node 0 is the SPPG."""
    n = len(distances)
    if n == 1:
        return [0], 0.0

    dp, parent = {}, {}
    for j in range(1, n):
        mask = 1 << (j - 1)
        dp[(mask, j)] = distances[0][j]
        parent[(mask, j)] = 0

    for mask in range(1, 1 << (n - 1)):
        for j in range(1, n):
            bit_j = 1 << (j - 1)
            if not mask & bit_j or mask == bit_j:
                continue
            prev_mask = mask ^ bit_j
            best, best_prev = inf, None
            for i in range(1, n):
                if prev_mask & (1 << (i - 1)):
                    candidate = dp.get((prev_mask, i), inf) + distances[i][j]
                    if candidate < best:
                        best, best_prev = candidate, i
            dp[(mask, j)] = best
            parent[(mask, j)] = best_prev

    full_mask = (1 << (n - 1)) - 1
    best_cost, last = inf, None
    for j in range(1, n):
        candidate = dp.get((full_mask, j), inf) + distances[j][0]
        if candidate < best_cost:
            best_cost, last = candidate, j

    if last is None or best_cost == inf:
        return None, inf

    order, mask, current = [], full_mask, last
    while current != 0:
        order.append(current)
        previous = parent[(mask, current)]
        mask ^= 1 << (current - 1)
        current = previous
    order.reverse()
    return [0] + order, best_cost


def nearest_neighbour(distances):
    n = len(distances)
    unvisited = set(range(1, n))
    tour, current = [0], 0
    while unvisited:
        reachable = [j for j in unvisited if distances[current][j] != inf]
        if not reachable:
            return None
        nxt = min(reachable, key=lambda j: distances[current][j])
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    if distances[current][0] == inf:
        return None
    return tour


def or_opt(tour, distances, max_segment=3):
    """Relocate short segments without reversing them (asymmetric-safe)."""
    best = tour[:]
    best_cost = tour_cost(best, distances)
    n = len(best)

    improved = True
    while improved:
        improved = False
        for length in range(1, min(max_segment, n - 1) + 1):
            for start in range(1, n - length + 1):
                segment = best[start:start + length]
                remainder = best[:start] + best[start + length:]
                for insert_at in range(1, len(remainder) + 1):
                    candidate = remainder[:insert_at] + segment + remainder[insert_at:]
                    cost = tour_cost(candidate, distances)
                    if cost < best_cost:
                        best, best_cost = candidate, cost
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
    return best, best_cost


def solve_tsp(distances, exact_limit=16):
    """Return tour, distance, selected algorithm, and solver-only elapsed time."""
    n = len(distances)
    if n == 0 or any(len(row) != n for row in distances):
        raise ValueError("Distance matrix must be non-empty and square.")

    started = perf_counter()
    if n <= exact_limit:
        tour, cost = held_karp(distances)
        algorithm = "Held–Karp (exact)"
    else:
        tour = nearest_neighbour(distances)
        if tour is None:
            cost = inf
        else:
            tour, cost = or_opt(tour, distances)
        algorithm = "Nearest Neighbour + Or-opt (heuristic)"
    elapsed = perf_counter() - started

    return {
        "tour": tour,
        "distance_m": cost,
        "algorithm": algorithm,
        "solver_seconds": elapsed,
    }
