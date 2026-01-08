# Thuật toán Dijkstra - Tìm đường đi ngắn nhất
def dijkstra(graph, start_node, end_node):
    distances = {}
    previous = {}
    visited = set()
    unvisited = set()

    all_nodes = graph.get_all_nodes()
    for node in all_nodes:
        distances[node] = float('inf')
        previous[node] = None
        unvisited.add(node)

    distances[start_node] = 0

    while unvisited:        # lặp chính
        current_node = None
        min_distance = float('inf')

        # chọn node chưa thăm có qđ min
        for node in unvisited:
            if distances[node] < min_distance:
                min_distance = distances[node]
                current_node = node

        if current_node is None:
            break
        if current_node == end_node:
            break

        unvisited.remove(current_node)
        visited.add(current_node)

        # Relax các đỉnh kề
        for neighbor, weight in graph.get_neighbors(current_node):
            if neighbor in visited:
                continue

            new_distance = distances[current_node] + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node

    # đường đi ngược 
    path = []
    current = end_node

    while current is not None:
        path.insert(0, current)
        current = previous[current]

    # 0 có đường
    if distances[end_node] == float('inf'):
        return {
            'path': [],
            'distance': float('inf')
        }

    return {
        'path': path,
        'distance': distances[end_node]
    }

