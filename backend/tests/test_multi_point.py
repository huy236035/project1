# Test Multi-point Router
from thuat_toan.utils.graph import Graph
from thuat_toan.solver import RouteSolver
from thong_tin.models.location import Location

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

# Test với nhiều điểm
locations = [
    Location(lat=21.0285, lng=105.8542, name="Point A"),
    Location(lat=21.0300, lng=105.8560, name="Point B"),
    Location(lat=21.0320, lng=105.8520, name="Point C"),
    Location(lat=21.0340, lng=105.8550, name="Point D"),
]

print("=" * 50)
print("TEST MULTI-POINT ROUTER")
print("=" * 50)
print(f"\nPoints to visit: {[loc.name for loc in locations]}\n")

solver = RouteSolver()
result = solver.solve(locations, ga_population_size=30, ga_generations=50)

print("\n" + "=" * 50)
print("RESULTS")
print("=" * 50)
print(f"\nOptimal route: {' -> '.join(result['route'])}")
print(f"Total distance: {result['distance']}")

if 'distance_matrix' in result:
    print(f"\nDistance matrix:")
    for (p1, p2), dist in result['distance_matrix'].items():
        if p1 < p2:  # Only print one direction to avoid duplicates
            print(f"  {p1} <-> {p2}: {dist}")

if 'detailed_paths' in result:
    print(f"\nDetailed paths:")
    for (start, end), path_info in result['detailed_paths'].items():
        print(f"  {start} -> {end}: {' -> '.join(path_info['path'])} (distance: {path_info['distance']})")

