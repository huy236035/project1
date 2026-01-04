from graph import Graph
from dijkstra import dijkstra

g = Graph()

g.add_edge('A', 'B', 1)
g.add_edge('A', 'C', 4)
g.add_edge('B', 'C', 2)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 1)

result = dijkstra(g, 'A', 'D')

print("Path:", result['path'])
print("Distance:", result['distance'])
