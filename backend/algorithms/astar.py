# Thuật toán A* - Tìm đường đi ngắn nhất với heuristic
import math
from data.nodes import NODES

def haversine_distance(node1, node2):
    """
    Tính khoảng cách đường thẳng (heuristic) giữa 2 node
    Sử dụng công thức Haversine cho tọa độ GPS
    """
    if node1 not in NODES or node2 not in NODES:
        return 0  # Nếu không có tọa độ, return 0 (heuristic không chính xác nhưng vẫn chạy được)
    
    lat1, lng1 = NODES[node1]["lat"], NODES[node1]["lng"]
    lat2, lng2 = NODES[node2]["lat"], NODES[node2]["lng"]
    
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    # Công thức Haversine
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Bán kính Trái Đất (km)
    R = 6371.0
    
    # Khoảng cách tính bằng km
    distance = R * c
    
    return distance

def astar(graph, start_node, end_node):
    """
    Thuật toán A* tìm đường đi ngắn nhất
    f(n) = g(n) + h(n)
    - g(n): khoảng cách thực tế từ start đến n
    - h(n): heuristic (khoảng cách đường thẳng từ n đến end)
    """
    # Kiểm tra input
    all_nodes = list(graph.get_all_nodes())
    if start_node not in all_nodes or end_node not in all_nodes:
        return {
            'path': [],
            'distance': float('inf'),
            'message': 'Start node hoặc end node không tồn tại'
        }
    
    # Nếu start = end
    if start_node == end_node:
        return {
            'path': [start_node],
            'distance': 0
        }
    
    # Khởi tạo
    g_score = {}  # g(n): khoảng cách thực tế từ start đến n
    f_score = {}  # f(n) = g(n) + h(n)
    previous = {}  # Lưu node trước đó
    open_set = set()  # Set các node cần xét
    closed_set = set()  # Set các node đã xét
    
    # Khởi tạo g_score và f_score
    for node in all_nodes:
        g_score[node] = float('inf')
        f_score[node] = float('inf')
        previous[node] = None
    
    g_score[start_node] = 0
    h_start = haversine_distance(start_node, end_node)
    f_score[start_node] = g_score[start_node] + h_start
    
    open_set.add(start_node)
    
    # Vòng lặp chính của A*
    while open_set:
        # Chọn node có f_score nhỏ nhất
        current_node = None
        min_f_score = float('inf')
        
        for node in open_set:
            if f_score[node] < min_f_score:
                min_f_score = f_score[node]
                current_node = node
        
        # Nếu không tìm thấy hoặc đã đến end
        if current_node is None or current_node == end_node:
            break
        
        # Chuyển current_node từ open_set sang closed_set
        open_set.remove(current_node)
        closed_set.add(current_node)
        
        # Xét các neighbor của current_node
        neighbors = graph.get_neighbors(current_node)
        for neighbor, weight in neighbors:
            # Bỏ qua nếu đã xét
            if neighbor in closed_set:
                continue
            
            # Tính g_score mới
            tentative_g_score = g_score[current_node] + weight
            
            # Nếu neighbor chưa trong open_set, thêm vào
            if neighbor not in open_set:
                open_set.add(neighbor)
            # Nếu đường đi mới không tốt hơn, bỏ qua
            elif tentative_g_score >= g_score[neighbor]:
                continue
            
            # Cập nhật g_score, previous và f_score
            previous[neighbor] = current_node
            g_score[neighbor] = tentative_g_score
            h_neighbor = haversine_distance(neighbor, end_node)
            f_score[neighbor] = g_score[neighbor] + h_neighbor
    
    # Tái tạo đường đi
    path = []
    current = end_node
    
    while current is not None:
        path.insert(0, current)
        current = previous[current]
    
    # Kiểm tra có tìm thấy đường đi không
    if not path or path[0] != start_node:
        return {
            'path': [],
            'distance': float('inf'),
            'message': 'Không tìm thấy đường đi'
        }
    
    return {
        'path': path,
        'distance': g_score[end_node]
    }

