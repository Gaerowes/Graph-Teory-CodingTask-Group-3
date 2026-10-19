
from math import inf
from time import perf_counter


def tour_cost(tour, distances):
    """Calculate total cycle cost, including the return to SPPG."""
    total = 0
    n = len(tour)

    for i in range(n):
        a = tour[i]
        b = tour[(i + 1) % n]
        cost = distances[a][b]

        if cost == inf:
            return inf

        total += cost

    return total


def held_karp(distances):
    """Find the optimal TSP cycle using dynamic programming."""
    n = len(distances)

    if n == 1:
        return [0], 0

    dp = {}
    parent = {}

    # Initialize paths from SPPG (node 0).
    for j in range(1, n):
        mask = 1 << (j - 1)
        dp[(mask, j)] = distances[0][j]
        parent[(mask, j)] = 0

    # Evaluate all subsets of schools.
    for mask in range(1, 1 << (n - 1)):
        for j in range(1, n):
            bit_j = 1 << (j - 1)

            if not mask & bit_j or mask == bit_j:
                continue

            previous_mask = mask ^ bit_j
            best_cost = inf
            best_previous = None

            for i in range(1, n):
                if not previous_mask & (1 << (i - 1)):
                    continue

                candidate = (
                    dp.get((previous_mask, i), inf)
                    + distances[i][j]
                )

                if candidate < best_cost:
                    best_cost = candidate
                    best_previous = i

            dp[(mask, j)] = best_cost
            parent[(mask, j)] = best_previous

    full_mask = (1 << (n - 1)) - 1
    best_cost = inf
    last = None

    for j in range(1, n):
        candidate = dp.get((full_mask, j), inf) + distances[j][0]

        if candidate < best_cost:
            best_cost = candidate
            last = j

    if last is None or best_cost == inf:
        return None, inf

    # Reconstruct the visiting order.
    order = []
    mask = full_mask
    current = last

    while current != 0:
        order.append(current)
        previous = parent[(mask, current)]
        mask ^= 1 << (current - 1)
        current = previous

    order.reverse()
    return [0] + order, best_cost


def nearest_neighbour(distances):
    """Build an initial tour using directed nearest neighbour."""
    n = len(distances)
    unvisited = set(range(1, n))
    tour = [0]
    current = 0

    while unvisited:
        reachable = [
            node for node in unvisited
            if distances[current][node] != inf
        ]

        if not reachable:
            return None

        next_node = min(
            reachable,
            key=lambda node: distances[current][node]
        )

        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    if distances[current][0] == inf:
        return None

    return tour


def or_opt(tour, distances, max_segment=3):
    """Improve the tour by relocating segments without reversing them."""
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
                    candidate = (
                        remainder[:insert_at]
                        + segment
                        + remainder[insert_at:]
                    )

                    cost = tour_cost(candidate, distances)

                    if cost < best_cost:
                        best = candidate
                        best_cost = cost
                        improved = True
                        break

                if improved:
                    break

            if improved:
                break

    return best, best_cost


def solve_tsp(distances, exact_limit=16):
    """Choose exact Held-Karp or heuristic based on problem size."""
    start_time = perf_counter()
    n = len(distances)

    if n == 0 or any(len(row) != n for row in distances):
        raise ValueError("Distance matrix must be square and non-empty.")

    if n <= exact_limit:
        tour, cost = held_karp(distances)
        algorithm = "Held-Karp"
    else:
        tour = nearest_neighbour(distances)

        if tour is None:
            cost = inf
        else:
            tour, cost = or_opt(tour, distances)

        algorithm = "Nearest Neighbour + Or-opt"

    elapsed = perf_counter() - start_time

    return {
        "algorithm": algorithm,
        "tour": tour,
        "distance": cost,
        "execution_time": elapsed,
    }


def get_distance_input(prompt):
    """Read a distance, allowing X for a missing road."""
    while True:
        value = input(prompt).strip().lower()

        if value in ("x", "inf", "-"):
            return inf

        try:
            distance = float(value)

            if distance < 0:
                print("Distance cannot be negative.")
                continue

            return distance

        except ValueError:
            print("Enter a non-negative number or X for no direct road.")


def main():
    print("=== SPPG TSP Simulator ===")
    print("Node 0 is the SPPG; other nodes are schools.")
    print("Enter X if there is no direct route between two nodes.\n")

    while True:
        try:
            school_count = int(input("Number of schools: "))

            if school_count < 0:
                print("Number of schools cannot be negative.")
                continue

            break

        except ValueError:
            print("Please enter a whole number.")

    n = school_count + 1

    if n > 17:
        print(
            "\nWarning: the distance matrix has more than 16 schools."
            "\nThe heuristic will be used, and its result may not be optimal."
        )

    names = ["SPPG"]

    for i in range(1, n):
        name = input(f"Name of school {i}: ").strip()
        names.append(name if name else f"School {i}")

    print("\nEnter the directed distance matrix in kilometres.")
    print("Each row represents the starting node; each column the destination.")
    print("Use 0 on the diagonal.")

    distances = []

    for i in range(n):
        row = []

        for j in range(n):
            if i == j:
                row.append(0)
            else:
                row.append(
                    get_distance_input(
                        f"Distance {names[i]} -> {names[j]}: "
                    )
                )

        distances.append(row)

    result = solve_tsp(distances)

    print("\n=== Result ===")
    print("Algorithm:", result["algorithm"])

    if result["tour"] is None or result["distance"] == inf:
        print("No valid round trip visiting every school was found.")
        return

    route = result["tour"] + [0]
    print("Visiting order:", " -> ".join(names[i] for i in route))
    print(f"Total distance: {result['distance']:.2f} km")
    print(f"Solver execution time: {result['execution_time']:.6f} seconds")


if __name__ == "__main__":
    main()
