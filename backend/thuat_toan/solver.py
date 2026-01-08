"""
Solver chính kết hợp A* và GA để tìm đường đi ngắn nhất
"""
from __future__ import annotations
from typing import List, Dict, Any
from thuat_toan.algorithms.astar import astar
from thuat_toan.algorithms.genetic_algorithm import genetic_algorithm
from thuat_toan.utils.graph import Graph
from thuat_toan.utils.distance_calculator import haversine_distance
from map.map_data_service import MapDataService
from thong_tin.location_service import LocationService
from thong_tin.models.location import Location
from utils.logger import logger

class RouteSolver:
    """
    Solver chính kết hợp A* và GA để tìm đường đi ngắn nhất
    """
    
    def __init__(self, consider_traffic: bool = True):
        """
        Khởi tạo Solver
        
        Args:
            consider_traffic: Có xem xét tắc đường không
        """
        # Lazy initialization - chỉ khởi tạo khi cần (cho solve() method)
        self._map_service = None
        self._location_service = None
        self.consider_traffic = consider_traffic
        self._original_coordinates = {}  # Lưu tọa độ gốc từ người dùng
    
    @property
    def map_service(self):
        """Lazy load MapDataService - chỉ khi cần (cho solve() method)"""
        if self._map_service is None:
            self._map_service = MapDataService()
        return self._map_service
    
    @property
    def location_service(self):
        """Lazy load LocationService - chỉ khi cần (cho solve() method)"""
        if self._location_service is None:
            self._location_service = LocationService(map_service=self.map_service)
        return self._location_service
    
    def solve(self, locations: List[Location], 
              ga_population_size: int = 100, 
              ga_generations: int = 500) -> Dict[str, Any]:
        """
        Tìm đường đi tối ưu qua nhiều điểm
        
        Args:
            locations: List địa chỉ/vị trí người dùng chọn
            ga_population_size: Số lượng cá thể trong GA
            ga_generations: Số thế hệ trong GA
        
        Returns:
            Kết quả đường đi tối ưu
        """
        if len(locations) < 2:
            return {
                'route': [loc.node_id for loc in locations] if locations else [],
                'distance': 0,
                'path_coordinates': [{'lat': loc.lat, 'lng': loc.lng} for loc in locations],
                'message': 'Cần ít nhất 2 điểm'
            }
        
        # 1. Lấy dữ liệu bản đồ từ map service
        # Nếu không có OSM data, load động từ tọa độ người dùng
        graph = self.map_service.get_graph(self.consider_traffic)
        
        # Graph đã được load từ MapDataService
        
        # 2. Chuyển đổi địa chỉ sang nodes trong graph
        nodes = self.location_service.addresses_to_nodes(locations)
        
        # Lưu mapping từ node_id sang tọa độ gốc của người dùng
        self._original_coordinates = {}
        for i, location in enumerate(locations):
            if location.node_id:
                self._original_coordinates[location.node_id] = {
                    'lat': location.lat,
                    'lng': location.lng
                }
            # Nếu node_id không có, dùng index
            if i < len(nodes):
                self._original_coordinates[nodes[i]] = {
                    'lat': location.lat,
                    'lng': location.lng
                }
        
        if len(nodes) == 2:
            # Nếu chỉ có 2 điểm, dùng A* để tìm đường đi thực tế (đường bộ)
            node_coords = self.map_service.get_all_node_coordinates()
            result = astar(graph, nodes[0], nodes[1], node_coordinates=node_coords)
            
            # Xây dựng path_coordinates từ đường đi thực tế (bao gồm tất cả các điểm trung gian)
            path_coordinates = self._build_path_coordinates(result['path'])
            
            # Xử lý các trường hợp đặc biệt
            # Nếu không tìm thấy đường đi trong graph
            if result['distance'] == float('inf'):
                logger.warning(f"Could not find road path between {nodes[0]} and {nodes[1]}")
                # Fallback: đường chim bay
                if len(locations) == 2:
                    direct_distance = haversine_distance(
                        locations[0].lat, locations[0].lng,
                        locations[1].lat, locations[1].lng
                    )
                    result['path'] = [nodes[0], nodes[1]]
                    result['distance'] = direct_distance
                    path_coordinates = [
                        {'lat': locations[0].lat, 'lng': locations[0].lng},
                        {'lat': locations[1].lat, 'lng': locations[1].lng}
                    ]
            
            # Nếu khoảng cách = 0 nhưng không phải cùng một điểm
            elif result['distance'] == 0 and nodes[0] != nodes[1]:
                logger.warning(f"Distance is 0 between different nodes {nodes[0]} and {nodes[1]}")
                # Tính lại từ tọa độ gốc
                if len(locations) == 2:
                    direct_distance = haversine_distance(
                        locations[0].lat, locations[0].lng,
                        locations[1].lat, locations[1].lng
                    )
                    if direct_distance > 0:
                        result['distance'] = direct_distance
            
            # Chuyển tuple key thành string key để JSON serialization
            key = f"{nodes[0]}_{nodes[1]}"
            return {
                'route': result['path'],
                'distance': result['distance'],  # Khoảng cách đường bộ từ A* hoặc đường chim bay
                'path_coordinates': path_coordinates,  # Đường đi thực tế với tất cả điểm trung gian
                'detailed_paths': {
                    key: {
                        'path': result['path'],
                        'distance': result['distance']
                    }
                }
            }
        
        # 3. Sử dụng A* để tính ma trận khoảng cách
        node_coords = self.map_service.get_all_node_coordinates()
        distance_matrix = self._calculate_distance_matrix(graph, nodes, node_coordinates=node_coords)
        
        # 4. Tạo complete graph từ ma trận khoảng cách
        complete_graph = self._create_complete_graph(distance_matrix, nodes)
        
        # 5. Sử dụng GA để tìm thứ tự tối ưu
        ga_result = genetic_algorithm(
            complete_graph,
            nodes,
            population_size=ga_population_size,
            generations=ga_generations,
            mutation_rate=0.1,
            elite_size=5
        )
        
        # 6. Tạo đường đi chi tiết bằng A*
        node_coords = self.map_service.get_all_node_coordinates()
        detailed_paths = self._build_detailed_path(graph, ga_result['route'], node_coordinates=node_coords)
        
        # 7. Tạo path_coordinates
        path_coordinates = self._build_path_coordinates(ga_result['route'])
        
        return {
            'route': ga_result['route'],
            'distance': ga_result['distance'],
            'path_coordinates': path_coordinates,
            'distance_matrix': distance_matrix,
            'detailed_paths': detailed_paths
        }
    
    def solve_from_coordinates(self, coordinates: List[Dict[str, float]],
                               ga_population_size: int = 100,
                               ga_generations: int = 500) -> Dict[str, Any]:
        """
        Tìm đường đi tối ưu từ danh sách tọa độ
        Trả về route indices (0, 1, 2, ...) để frontend có thể gọi OSM Routing API
        
        Args:
            coordinates: List các dict chứa lat, lng
            ga_population_size: Số lượng cá thể trong GA
            ga_generations: Số thế hệ trong GA
        
        Returns:
            Kết quả đường đi tối ưu với route là indices (0, 1, 2, ...)
        """
        if len(coordinates) < 2:
            return {
                'route': list(range(len(coordinates))),
                'distance': 0,
                'message': 'Cần ít nhất 2 điểm'
            }
        
        # Tạo graph đơn giản từ coordinates (chỉ dùng haversine để tính khoảng cách)
        # Graph này chỉ để GA tính toán thứ tự tối ưu
        simple_graph = Graph()
        n = len(coordinates)
        
        # Tạo nodes với index (0, 1, 2, ...)
        for i in range(n):
            simple_graph.add_node(str(i))
        
        # Tạo edges giữa tất cả các cặp điểm với khoảng cách haversine
        for i in range(n):
            for j in range(i + 1, n):
                distance = haversine_distance(
                    coordinates[i]['lat'], coordinates[i]['lng'],
                    coordinates[j]['lat'], coordinates[j]['lng']
                )
                simple_graph.add_edge(str(i), str(j), distance)
                simple_graph.add_edge(str(j), str(i), distance)
        
        # Tạo complete graph cho GA
        nodes = [str(i) for i in range(n)]
        complete_graph = simple_graph  # Đã là complete graph
        
        # Sử dụng GA để tìm thứ tự tối ưu
        ga_result = genetic_algorithm(
            complete_graph,
            nodes,
            population_size=ga_population_size,
            generations=ga_generations,
            mutation_rate=0.1,
            elite_size=5
        )
        
        # Chuyển đổi route từ string indices sang int indices
        route_indices = [int(node) for node in ga_result['route']]
        
        return {
            'route': route_indices,  # [0, 2, 1, 3] chẳng hạn
            'distance': round(ga_result['distance'], 2),  # Khoảng cách ước tính từ haversine
            'message': 'Tìm đường đi thành công. Frontend sẽ gọi OSM Routing API để lấy đường đi chi tiết.'
        }
    
    def _calculate_distance_matrix(self, graph: Graph, nodes: List[str], node_coordinates=None) -> Dict:
        """
        Tính ma trận khoảng cách giữa tất cả các cặp điểm bằng A*
        
        Args:
            graph: Đồ thị
            nodes: List các node
            node_coordinates: Dict chứa tọa độ các nodes (optional)
        
        Returns:
            Dict với key là string "node1_node2" và value là khoảng cách
        """
        distance_matrix = {}
        n = len(nodes)
        
        for i in range(n):
            for j in range(i + 1, n):
                node1 = nodes[i]
                node2 = nodes[j]
                
                # Sử dụng A* để tìm đường đi ngắn nhất
                result = astar(graph, node1, node2, node_coordinates=node_coordinates)
                distance = result['distance']
                
                # Lưu cả 2 chiều, dùng string key để JSON serialization
                key1 = f"{node1}_{node2}"
                key2 = f"{node2}_{node1}"
                distance_matrix[key1] = distance
                distance_matrix[key2] = distance
        
        return distance_matrix
    
    def _create_complete_graph(self, distance_matrix: Dict, nodes: List[str]) -> Graph:
        """
        Tạo complete graph từ ma trận khoảng cách
        
        Args:
            distance_matrix: Ma trận khoảng cách (key là string "node1_node2")
            nodes: List các node
        
        Returns:
            Complete graph
        """
        complete_graph = Graph()
        
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    node1 = nodes[i]
                    node2 = nodes[j]
                    # Dùng string key để lookup
                    key = f"{node1}_{node2}"
                    distance = distance_matrix.get(key, float('inf'))
                    complete_graph.add_edge(node1, node2, distance)
        
        return complete_graph
    
    def _build_detailed_path(self, graph: Graph, route: List[str], node_coordinates=None) -> Dict:
        """
        Xây dựng đường đi chi tiết bằng A*
        
        Args:
            graph: Đồ thị
            route: Route tối ưu từ GA
            node_coordinates: Dict chứa tọa độ các nodes (optional)
        
        Returns:
            Dict chứa đường đi chi tiết giữa các cặp điểm liên tiếp (key là string "start_end")
        """
        detailed_paths = {}
        
        for i in range(len(route) - 1):
            start = route[i]
            end = route[i + 1]
            
            # Tìm đường đi chi tiết bằng A*
            path_result = astar(graph, start, end, node_coordinates=node_coordinates)
            # Dùng string key để JSON serialization
            key = f"{start}_{end}"
            detailed_paths[key] = {
                'path': path_result['path'],
                'distance': path_result['distance']
            }
        
        return detailed_paths
    
    def _build_path_coordinates(self, route: List[str]) -> List[Dict[str, float]]:
        """
        Xây dựng path_coordinates từ route
        Bao gồm tất cả các điểm trung gian để vẽ đường đi thực tế trên bản đồ
        
        Args:
            route: Route chứa các node_id (có thể có nhiều điểm trung gian từ A*)
        
        Returns:
            List các dict chứa lat, lng (đường đi thực tế với tất cả điểm trung gian)
        """
        path_coordinates = []
        
        # Lấy từ map_service (có thể là OSM hoặc sample)
        node_coords = self.map_service.get_all_node_coordinates()
        
        for idx, node_id in enumerate(route):
            node_id_str = str(node_id)
            
            # Ưu tiên 1: Dùng tọa độ gốc từ người dùng (chỉ cho điểm đầu và cuối)
            # Các điểm trung gian sẽ dùng tọa độ từ node_coordinates để vẽ đường đi thực tế
            if hasattr(self, '_original_coordinates') and node_id_str in self._original_coordinates:
                # Chỉ dùng tọa độ gốc cho điểm đầu và cuối
                # Điểm trung gian dùng tọa độ từ graph để vẽ đường đi thực tế
                if idx == 0 or idx == len(route) - 1:
                    path_coordinates.append(self._original_coordinates[node_id_str].copy())
                else:
                    # Điểm trung gian: dùng tọa độ từ graph (đường bộ thực tế)
                    if node_id_str in node_coords:
                        path_coordinates.append({
                            'lat': node_coords[node_id_str]['lat'],
                            'lng': node_coords[node_id_str]['lng']
                        })
                continue
            
            # Ưu tiên 2: Lấy từ node_coordinates của map_service
            # Điều này đảm bảo các điểm trung gian được vẽ đúng trên bản đồ
            if node_id_str in node_coords:
                path_coordinates.append({
                    'lat': node_coords[node_id_str]['lat'],
                    'lng': node_coords[node_id_str]['lng']
                })
            else:
                # Fallback: thử lấy từ location_service
                coords = self.location_service.get_node_coordinates(node_id_str)
                if coords:
                    path_coordinates.append(coords)
                else:
                    # Nếu không tìm thấy, bỏ qua node này
                    pass
        
        return path_coordinates

