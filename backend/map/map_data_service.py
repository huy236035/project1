"""
Service cung cấp dữ liệu bản đồ cho Solver
"""
from typing import Optional, Dict
from map.map_loader import load_map_from_sample, load_map_from_osm, load_hanoi_map
from map.traffic_handler import TrafficHandler
from map.road_network import RoadNetwork
from config import Config
from utils.logger import logger

class MapDataService:
    """
    Service cung cấp dữ liệu bản đồ
    """
    
    def __init__(self, use_osm: bool = True, place: str = "Hanoi, Vietnam"):
        """
        Khởi tạo MapDataService
        
        Args:
            use_osm: Có sử dụng dữ liệu từ OSM không
            place: Tên địa điểm để load từ OSM
        """
        self.use_osm = use_osm
        self.place = place
        self.traffic_handler = TrafficHandler()
        self.node_coordinates = {}  # Lưu tọa độ các nodes
        
        # Load graph - CHỈ dùng OSM, không dùng sample data
        if not use_osm:
            raise ValueError("Sample data đã bị xóa. Chỉ có thể dùng OSM data. Set use_osm=True")
        
        try:
            logger.info(f"Loading map from OSM for {place}...")
            # Load graph và node_coordinates từ cùng một nx_graph để đảm bảo đồng bộ
            graph, node_coords = self._load_graph_and_coordinates_from_osm(place)
            self.node_coordinates = node_coords
            
            self.road_network = RoadNetwork(graph)
            logger.info(f"Map data service initialized successfully: {len(self.node_coordinates)} node coordinates")
        except Exception as e:
            logger.error(f"Error initializing map data service: {str(e)}")
            raise  # Không fallback về sample data nữa
    
    def get_graph(self, consider_traffic=True, reload: bool = False):
        """
        Lấy đồ thị bản đồ
        
        Args:
            consider_traffic: Có xem xét tắc đường không
            reload: Có reload lại từ OSM không
        
        Returns:
            Graph object
        """
        if reload and self.use_osm:
            try:
                graph = load_hanoi_map()
                self.road_network = RoadNetwork(graph)
            except Exception as e:
                logger.error(f"Error reloading graph: {str(e)}")
        
        graph = self.road_network.get_graph()
        
        if consider_traffic:
            # Áp dụng tắc đường vào trọng số
            graph = self._apply_traffic_to_graph(graph)
        
        return graph
    
    def _apply_traffic_to_graph(self, graph):
        """
        Áp dụng hệ số tắc đường vào graph
        
        Args:
            graph: Graph object
        
        Returns:
            Graph với trọng số đã được điều chỉnh theo traffic
        """
        # Tạo graph mới với trọng số đã điều chỉnh
        from thuat_toan.utils.graph import Graph
        new_graph = Graph()
        
        for node in graph.get_all_nodes():
            for neighbor, weight in graph.get_neighbors(node):
                # Áp dụng hệ số tắc đường
                traffic_factor = self.traffic_handler.get_traffic_factor(node)
                adjusted_weight = weight * traffic_factor
                new_graph.add_edge(node, neighbor, adjusted_weight)
        
        return new_graph
    
    def get_traffic_handler(self):
        """
        Lấy traffic handler
        
        Returns:
            TrafficHandler object
        """
        return self.traffic_handler
    
    def get_road_network(self):
        """
        Lấy road network
        
        Returns:
            RoadNetwork object
        """
        return self.road_network
    
    def _load_graph_and_coordinates_from_osm(self, place: str):
        """
        Load graph và node coordinates từ cùng một OSM graph để đảm bảo đồng bộ
        Sử dụng OSM service tối ưu hóa
        
        Args:
            place: Tên địa điểm
        
        Returns:
            (graph, node_coordinates) tuple
        """
        try:
            from map.osm_service import load_osm_data
            graph, node_coordinates = load_osm_data(place=place, network_type="drive", use_cache=True)
            return graph, node_coordinates
        except Exception as e:
            logger.error(f"Could not load graph and coordinates from OSM: {str(e)}")
            raise  # Không fallback về sample data nữa
    
    def _load_node_coordinates_from_osm(self):
        """
        Load node coordinates từ OSM graph (deprecated - dùng _load_graph_and_coordinates_from_osm thay thế)
        """
        try:
            from map.osm_loader import OSMLoader
            loader = OSMLoader()
            nx_graph = loader.load_network_from_place(self.place, network_type="drive")
            self.node_coordinates = loader.get_nodes_coordinates(nx_graph)
            logger.info(f"Loaded {len(self.node_coordinates)} node coordinates from OSM")
        except Exception as e:
            logger.error(f"Could not load node coordinates from OSM: {str(e)}")
            raise  # Không fallback về sample data nữa
    
    def get_node_coordinates(self, node_id: str) -> Optional[Dict]:
        """
        Lấy tọa độ của một node
        
        Args:
            node_id: ID của node
        
        Returns:
            Dict chứa lat, lng hoặc None
        """
        return self.node_coordinates.get(str(node_id))
    
    def get_all_node_coordinates(self) -> Dict:
        """
        Lấy tất cả node coordinates
        
        Returns:
            Dict chứa tất cả node coordinates
        """
        return self.node_coordinates.copy()
    
    def find_nearest_node(self, lat: float, lng: float) -> Optional[str]:
        """
        Tìm node gần nhất với tọa độ cho trước
        
        Args:
            lat: Vĩ độ
            lng: Kinh độ
        
        Returns:
            node_id gần nhất hoặc None
        """
        from thuat_toan.utils.distance_calculator import haversine_distance
        
        if not self.node_coordinates:
            return None
        
        min_distance = float('inf')
        nearest_node = None
        
        for node_id, coords in self.node_coordinates.items():
            distance = haversine_distance(
                lat, lng,
                coords['lat'], coords['lng']
            )
            if distance < min_distance:
                min_distance = distance
                nearest_node = node_id
        
        return nearest_node
    
    def reload_from_osm(self, place: Optional[str] = None):
        """
        Reload dữ liệu từ OSM
        
        Args:
            place: Tên địa điểm (nếu None thì dùng place hiện tại)
        """
        if place:
            self.place = place
        
        try:
            logger.info(f"Reloading map from OSM for {self.place}...")
            graph, node_coords = self._load_graph_and_coordinates_from_osm(self.place)
            self.road_network = RoadNetwork(graph)
            self.node_coordinates = node_coords
            logger.info("Map reloaded successfully")
        except Exception as e:
            logger.error(f"Error reloading from OSM: {str(e)}")

