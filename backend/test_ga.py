# Test Genetic Algorithm
from utils.graph import Graph
from algorithms.genetic_algorithm import genetic_algorithm

# Tạo graph
g = Graph()
g.add_edge('A', 'B', 1)
g.add_edge('A', 'C', 4)
g.add_edge('B', 'C', 2)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 1)
g.add_edge('D', 'E', 3)
g.add_edge('E', 'A', 6)

# Test với nhiều điểm
points = ['A', 'B', 'C', 'D', 'E']

print("=== Test Genetic Algorithm ===")
print(f"Points: {points}")
print()

result = genetic_algorithm(g, points, population_size=30, generations=50)

print(f"Best Route: {result['route']}")
print(f"Distance: {result['distance']}")


