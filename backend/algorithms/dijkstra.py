"""
Thuật toán Dijkstra tìm đường đi ngắn nhất
"""
from typing import Dict, List, Tuple, Optional
import sys
from utils.graph import Graph


def dijkstra(graph: Graph, start_node: str, end_node: str) -> Dict:
    """
    Thuật toán Dijkstra tìm đường đi ngắn nhất
    
    Args:
        graph: Đồ thị cần tìm đường
        start_node: Node bắt đầu
        end_node: Node kết thúc
    
    Returns:
        Dict với keys:
            - path: List các node từ start đến end (ngắn nhất)
            - distance: Khoảng cách ngắn nhất
            - visited_nodes: List các node đã được duyệt (để visualize)
            - message: Thông báo (nếu có lỗi)
    """
    # Kiểm tra input
    if not graph.has_node(start_node) or not graph.has_node(end_node):
        raise ValueError('Start node hoặc end node không tồn tại trong đồ thị')

    # Nếu start = end
    if start_node == end_node:
        return {
            'path': [start_node],
            'distance': 0,
            'visited_nodes': [start_node],
        }

    # Khởi tạo
    distances: Dict[str, float] = {}  # Lưu khoảng cách ngắn nhất đến mỗi node
    previous: Dict[str, Optional[str]] = {}  # Lưu node trước đó trong đường đi ngắn nhất
    visited: set = set()  # Set các node đã được xét
    unvisited: set = set()  # Set các node chưa được xét
    visited_order: List[str] = []  # Thứ tự các node đã visit (để visualize)

    # Khởi tạo distances: start_node = 0, các node khác = Infinity
    all_nodes = graph.get_all_nodes()
    for node in all_nodes:
        distances[node] = 0 if node == start_node else float('inf')
        previous[node] = None
        unvisited.add(node)

    # Vòng lặp chính của thuật toán Dijkstra
    while len(unvisited) > 0:
        # Bước 1: Chọn node chưa visit có distance nhỏ nhất
        currentNode = None
        min_distance = float('inf')

        for node in unvisited:
            if distances[node] < min_distance:
                min_distance = distances[node]
                currentNode = node

        # Nếu không tìm thấy node nào (không có đường đi)
        if currentNode is None or min_distance == float('inf'):
            break

        # Đánh dấu currentNode đã được visit
        unvisited.remove(currentNode)
        visited.add(currentNode)
        visited_order.append(currentNode)

        # Nếu đã đến end_node, có thể dừng sớm (tùy chọn)
        if currentNode == end_node:
            break

        # Bước 2: Xét tất cả các neighbor của currentNode
        neighbors = graph.get_neighbors(currentNode)
        for neighbor, weight in neighbors:
            # Bỏ qua nếu neighbor đã được visit
            if neighbor in visited:
                continue

            # Tính khoảng cách mới qua currentNode
            new_distance = distances[currentNode] + weight

            # Nếu tìm thấy đường đi ngắn hơn
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = currentNode

    # Bước 3: Tái tạo đường đi từ end_node ngược về start_node
    path: List[str] = []
    current: Optional[str] = end_node

    # Trace ngược lại từ end_node về start_node
    while current is not None:
        path.insert(0, current)  # Thêm vào đầu list
        current = previous[current]

    # Kiểm tra có tìm thấy đường đi không
    if not path or path[0] != start_node:
        return {
            'path': [],
            'distance': float('inf'),
            'visited_nodes': visited_order,
            'message': 'Không tìm thấy đường đi',
        }

    return {
        'path': path,
        'distance': distances[end_node],
        'visited_nodes': visited_order,
    }


def create_sample_graph() -> Graph:
    """
    Hàm helper để tạo graph mẫu (để test)
    """
    graph = Graph()

    # Thêm các node
    graph.add_node('A')
    graph.add_node('B')
    graph.add_node('C')
    graph.add_node('D')
    graph.add_node('E')
    graph.add_node('F')

    # Thêm các edge (ví dụ: đồ thị có hướng)
    graph.add_edge('A', 'B', 4)
    graph.add_edge('A', 'C', 2)
    graph.add_edge('B', 'C', 1)
    graph.add_edge('B', 'D', 5)
    graph.add_edge('C', 'D', 8)
    graph.add_edge('C', 'E', 10)
    graph.add_edge('D', 'E', 2)
    graph.add_edge('D', 'F', 6)
    graph.add_edge('E', 'F', 2)

    return graph

