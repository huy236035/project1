"""
Load dữ liệu từ OpenStreetMap (OSM)
Sử dụng lazy import để không crash nếu chưa cài osmnx/networkx
"""
from __future__ import annotations
from typing import Optional, Tuple, Dict, List

# Lazy import - chỉ import khi cần
_osmnx = None
_networkx = None
_OSM_AVAILABLE = None

def _check_osm_available():
    """Kiểm tra xem osmnx và networkx có sẵn không"""
    global _osmnx, _networkx, _OSM_AVAILABLE
    
    if _OSM_AVAILABLE is not None:
        return _OSM_AVAILABLE
    
    try:
        import osmnx as ox
        import networkx as nx
        _osmnx = ox
        _networkx = nx
        _OSM_AVAILABLE = True
        return True
    except ImportError:
        _OSM_AVAILABLE = False
        return False

def _get_osmnx():
    """Lấy osmnx module, raise error nếu chưa cài"""
    if not _check_osm_available():
        raise ImportError(
            "osmnx và networkx chưa được cài đặt. "
            "Chạy: pip install osmnx networkx geopy"
        )
    return _osmnx

def _get_networkx():
    """Lấy networkx module, raise error nếu chưa cài"""
    if not _check_osm_available():
        raise ImportError(
            "networkx chưa được cài đặt. "
            "Chạy: pip install networkx"
        )
    return _networkx

# Import các module khác
try:
    from thuat_toan.utils.graph import Graph
    from thuat_toan.utils.distance_calculator import haversine_distance
    from utils.logger import logger
except ImportError:
    import sys
    import os
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from thuat_toan.utils.graph import Graph
    from thuat_toan.utils.distance_calculator import haversine_distance
    from utils.logger import logger

class OSMLoader:
    """
    Load dữ liệu bản đồ từ OpenStreetMap
    Chỉ import osmnx/networkx khi thực sự cần dùng
    """
    
    def __init__(self):
        """Khởi tạo OSMLoader, chỉ import osmnx khi cần"""
        ox = _get_osmnx()
        # Cấu hình OSMnx
        ox.settings.use_cache = True
        ox.settings.log_console = False
    
    def load_network_from_place(self, place: str = "Hanoi, Vietnam", 
                                network_type: str = "drive"):
        """
        Load mạng lưới đường từ tên địa điểm
        
        Args:
            place: Tên địa điểm (ví dụ: "Hanoi, Vietnam")
            network_type: Loại mạng lưới ('drive', 'walk', 'bike', 'all')
        
        Returns:
            NetworkX MultiDiGraph
        """
        ox = _get_osmnx()
        nx = _get_networkx()
        
        try:
            logger.info(f"Loading OSM network for {place}...")
            G = ox.graph_from_place(place, network_type=network_type)
            logger.info(f"Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")
            return G
        except Exception as e:
            logger.error(f"Error loading OSM network: {str(e)}")
            raise
    
    def load_network_from_bbox(self, bbox: Tuple[float, float, float, float],
                              network_type: str = "drive"):
        """
        Load mạng lưới đường từ bounding box
        
        Args:
            bbox: (north, south, east, west) hoặc (min_lat, min_lng, max_lat, max_lng)
            network_type: Loại mạng lưới ('drive', 'walk', 'bike', 'all')
        
        Returns:
            NetworkX MultiDiGraph
        """
        ox = _get_osmnx()
        nx = _get_networkx()
        
        try:
            logger.info(f"Loading OSM network from bbox {bbox}...")
            # OSMnx expects (north, south, east, west)
            if len(bbox) == 4:
                north, south, east, west = bbox
                G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
            else:
                raise ValueError("bbox must be (north, south, east, west)")
            
            logger.info(f"Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")
            return G
        except Exception as e:
            logger.error(f"Error loading OSM network from bbox: {str(e)}")
            raise
    
    def load_network_from_point(self, center_point: Tuple[float, float],
                               dist: int = 5000, network_type: str = "drive"):
        """
        Load mạng lưới đường từ một điểm trung tâm
        
        Args:
            center_point: (lat, lng) điểm trung tâm
            dist: Khoảng cách tính bằng mét
            network_type: Loại mạng lưới ('drive', 'walk', 'bike', 'all')
        
        Returns:
            NetworkX MultiDiGraph
        """
        ox = _get_osmnx()
        nx = _get_networkx()
        
        try:
            lat, lng = center_point
            logger.info(f"Loading OSM network from point ({lat}, {lng}) within {dist}m...")
            G = ox.graph_from_point((lat, lng), dist=dist, network_type=network_type)
            logger.info(f"Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")
            return G
        except Exception as e:
            logger.error(f"Error loading OSM network from point: {str(e)}")
            raise
    
    def convert_networkx_to_graph(self, nx_graph) -> Graph:
        """
        Chuyển đổi NetworkX graph sang Graph object của chúng ta
        
        Args:
            nx_graph: NetworkX MultiDiGraph
        
        Returns:
            Graph object
        """
        graph = Graph()
        
        # Lấy tọa độ của các nodes
        node_coords = {}
        for node_id, data in nx_graph.nodes(data=True):
            if 'y' in data and 'x' in data:
                node_coords[node_id] = {
                    'lat': data['y'],
                    'lng': data['x']
                }
        
        # Thêm các edges
        for u, v, data in nx_graph.edges(data=True):
            # Tính khoảng cách từ tọa độ nếu có
            if u in node_coords and v in node_coords:
                coords_u = node_coords[u]
                coords_v = node_coords[v]
                distance = haversine_distance(
                    coords_u['lat'], coords_u['lng'],
                    coords_v['lat'], coords_v['lng']
                )
            elif 'length' in data:
                # Sử dụng length từ OSM (tính bằng mét, chuyển sang km)
                distance = data['length'] / 1000.0
            else:
                # Fallback: tính từ tọa độ nếu có
                distance = 1.0  # Default distance
            
            # Lưu node_id dạng string
            graph.add_edge(str(u), str(v), distance)
        
        logger.info(f"Converted NetworkX graph to Graph: {len(graph.get_all_nodes())} nodes")
        return graph
    
    def get_nodes_coordinates(self, nx_graph) -> Dict[str, Dict[str, float]]:
        """
        Lấy tọa độ của tất cả nodes từ NetworkX graph
        
        Args:
            nx_graph: NetworkX MultiDiGraph
        
        Returns:
            Dict với key là node_id (string) và value là {'lat': ..., 'lng': ...}
        """
        nodes = {}
        for node_id, data in nx_graph.nodes(data=True):
            if 'y' in data and 'x' in data:
                nodes[str(node_id)] = {
                    'lat': data['y'],
                    'lng': data['x']
                }
        return nodes
    
    def simplify_graph(self, nx_graph):
        """
        Đơn giản hóa graph (loại bỏ nodes không cần thiết)
        
        Args:
            nx_graph: NetworkX MultiDiGraph
        
        Returns:
            Simplified NetworkX MultiDiGraph
        """
        ox = _get_osmnx()
        
        try:
            simplified = ox.simplify_graph(nx_graph)
            logger.info(f"Simplified graph: {len(simplified.nodes)} nodes, {len(simplified.edges)} edges")
            return simplified
        except Exception as e:
            logger.warning(f"Could not simplify graph: {str(e)}")
            return nx_graph

# Export function để check OSM availability
def is_osm_available() -> bool:
    """Kiểm tra xem OSM có sẵn không (không raise error)"""
    return _check_osm_available()
