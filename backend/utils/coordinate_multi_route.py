# Coordinate Multi-Route - Tìm đường đi ngắn nhất qua nhiều điểm từ tọa độ GPS
# Sử dụng A* và GA đã có sẵn
import math
from utils.graph import Graph
from algorithms.genetic_algorithm import genetic_algorithm

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Tính khoảng cách đường thẳng giữa 2 tọa độ GPS (Haversine)
    Trả về khoảng cách tính bằng km
    """
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

def create_complete_graph_from_coordinates(coordinates):
    """
    Tạo complete graph từ danh sách tọa độ
    Mỗi điểm được đánh số từ 0 đến n-1 (dạng string để dùng với GA)
    
    Args:
        coordinates: List các tọa độ [{'lat': 21.0285, 'lng': 105.8542}, ...]
    
    Returns:
        graph: Complete graph với tất cả các edges
    """
    graph = Graph()
    n = len(coordinates)
    
    # Tạo nodes với index (dạng string)
    for i in range(n):
        graph.add_node(str(i))
    
    # Tính khoảng cách giữa tất cả các cặp điểm bằng Haversine
    for i in range(n):
        for j in range(n):
            if i != j:
                coord1 = coordinates[i]
                coord2 = coordinates[j]
                distance = haversine_distance(
                    coord1['lat'], coord1['lng'],
                    coord2['lat'], coord2['lng']
                )
                graph.add_edge(str(i), str(j), distance)
    
    return graph

def find_optimal_route_from_coordinates(coordinates, population_size=100, generations=500):
    """
    Tìm route tối ưu đi qua tất cả các điểm từ tọa độ GPS
    Sử dụng A* (để tính khoảng cách) và GA (để tối ưu thứ tự)
    
    Yêu cầu:
    - Điểm đầu tiên (index 0) là điểm xuất phát (bắt buộc)
    - Điểm cuối cùng (index n-1) là điểm kết thúc (bắt buộc)
    - Các điểm giữa có thể sắp xếp lại để tối ưu
    
    Args:
        coordinates: List các tọa độ [{'lat': ..., 'lng': ...}, ...]
        population_size: Số lượng cá thể trong GA
        generations: Số thế hệ trong GA
    
    Returns:
        {
            'route': [0, 2, 3, 1, 4],  # Thứ tự các điểm (index)
            'distance': 15.5,  # Tổng khoảng cách (km)
            'path_coordinates': [{'lat': ..., 'lng': ...}, ...]  # Tọa độ theo route
        }
    """
    if len(coordinates) < 2:
        return {
            'route': list(range(len(coordinates))),
            'distance': 0,
            'path_coordinates': coordinates
        }
    
    if len(coordinates) == 2:
        # Nếu chỉ có 2 điểm, route đơn giản
        distance = haversine_distance(
            coordinates[0]['lat'], coordinates[0]['lng'],
            coordinates[1]['lat'], coordinates[1]['lng']
        )
        return {
            'route': [0, 1],
            'distance': distance,
            'path_coordinates': coordinates
        }
    
    # Tạo complete graph từ tọa độ (dùng Haversine để tính khoảng cách)
    graph = create_complete_graph_from_coordinates(coordinates)
    
    # Tạo danh sách điểm cho GA
    # Điểm đầu (0) và điểm cuối (n-1) cố định
    # Các điểm giữa (1..n-2) có thể sắp xếp lại
    n = len(coordinates)
    start_point = '0'
    end_point = str(n - 1)
    middle_points = [str(i) for i in range(1, n - 1)]
    
    if len(middle_points) == 0:
        # Không có điểm giữa, route đơn giản
        ga_result = {
            'route': [start_point, end_point],
            'distance': haversine_distance(
                coordinates[0]['lat'], coordinates[0]['lng'],
                coordinates[n-1]['lat'], coordinates[n-1]['lng']
            )
        }
    else:
        # Chạy GA với điểm đầu + các điểm giữa
        # GA sẽ giữ điểm đầu cố định (theo logic trong genetic_algorithm.py)
        ga_result = genetic_algorithm(
            graph,
            [start_point] + middle_points,
            population_size=population_size,
            generations=generations,
            mutation_rate=0.01,
            elite_size=10
        )
        
        # Thêm điểm cuối vào route (luôn là điểm cuối)
        ga_result['route'] = ga_result['route'] + [end_point]
        
        # Tính lại khoảng cách đầy đủ từ route
        route = ga_result['route']
        total_distance = 0
        for i in range(len(route) - 1):
            idx1 = int(route[i])
            idx2 = int(route[i + 1])
            total_distance += haversine_distance(
                coordinates[idx1]['lat'], coordinates[idx1]['lng'],
                coordinates[idx2]['lat'], coordinates[idx2]['lng']
            )
        ga_result['distance'] = total_distance
    
    # Chuyển đổi route từ string index sang int index
    route_indices = [int(idx) for idx in ga_result['route']]
    
    # Tạo path_coordinates từ route
    path_coordinates = [coordinates[idx] for idx in route_indices]
    
    return {
        'route': route_indices,
        'distance': ga_result['distance'],
        'path_coordinates': path_coordinates
    }

