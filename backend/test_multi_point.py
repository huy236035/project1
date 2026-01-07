# Test Multi-point Router
from utils.graph import Graph
from multi_point_router import find_optimal_route

# Create graph
g = Graph()
g.add_edge('A', 'B', 1)
g.add_edge('A', 'C', 4)
g.add_edge('B', 'C', 2)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 1)
g.add_edge('D', 'E', 3)
g.add_edge('E', 'A', 6)
g.add_edge('E', 'B', 4)

# Test with multiple points
points = ['A', 'B', 'C', 'D', 'E']

print("=" * 50)
print("TEST MULTI-POINT ROUTER")
print("=" * 50)
print(f"\nPoints to visit: {points}\n")

result = find_optimal_route(
    graph=g,
    points=points,
    ga_population_size=30,
    ga_generations=50
)

print("\n" + "=" * 50)
print("RESULTS")
print("=" * 50)
print(f"\nOptimal route: {' -> '.join(result['route'])}")
print(f"Total distance: {result['distance']}")
print(f"\nDistance matrix:")
for (p1, p2), dist in result['distance_matrix'].items():
    if p1 < p2:  # Only print one direction to avoid duplicates
        print(f"  {p1} <-> {p2}: {dist}")

print(f"\nDetailed paths:")
for (start, end), path_info in result['detailed_paths'].items():
    print(f"  {start} -> {end}: {' -> '.join(path_info['path'])} (distance: {path_info['distance']})")

