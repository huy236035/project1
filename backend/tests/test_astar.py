# Test A* Algorithm
from thuat_toan.utils.graph import Graph
from thuat_toan.algorithms.astar import astar

g = Graph()

g.add_edge('A', 'B', 1)
g.add_edge('A', 'C', 4)
g.add_edge('B', 'C', 2)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 1)

result = astar(g, 'A', 'D')

print("Path:", result['path'])
print("Distance:", result['distance'])

from thuat_toan.utils.path_converter import nodes_to_coordinates

path = result['path']
print("Coordinates:", nodes_to_coordinates(path))

