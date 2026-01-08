"""
Load dữ liệu bản đồ từ OSM
KHÔNG dùng sample data nữa
"""
from thuat_toan.utils.graph import Graph
from map.osm_loader import OSMLoader
from utils.logger import logger
from typing import Optional, Tuple

def load_map_from_sample():
    """
    DEPRECATED: Sample data đã bị xóa
    Sử dụng load_map_from_osm() hoặc load_osm_from_coordinates() thay thế
    """
    raise ValueError("Sample data đã bị xóa. Sử dụng load_map_from_osm() hoặc load OSM động từ tọa độ.")

def load_map_from_osm(place: Optional[str] = None,
                     bbox: Optional[Tuple[float, float, float, float]] = None,
                     center_point: Optional[Tuple[float, float]] = None,
                     dist: int = 5000,
                     network_type: str = "drive",
                     simplify: bool = True) -> Graph:
    """
    Load dữ liệu bản đồ từ OpenStreetMap
    
    Args:
        place: Tên địa điểm (ví dụ: "Hanoi, Vietnam")
        bbox: Bounding box (north, south, east, west)
        center_point: (lat, lng) điểm trung tâm
        dist: Khoảng cách tính bằng mét (nếu dùng center_point)
        network_type: Loại mạng lưới ('drive', 'walk', 'bike', 'all')
        simplify: Có đơn giản hóa graph không
    
    Returns:
        Graph object
    """
    loader = OSMLoader()
    
    try:
        if place:
            nx_graph = loader.load_network_from_place(place, network_type)
        elif bbox:
            nx_graph = loader.load_network_from_bbox(bbox, network_type)
        elif center_point:
            nx_graph = loader.load_network_from_point(center_point, dist, network_type)
        else:
            # Default: load Hanoi
            logger.info("No location specified, loading Hanoi by default")
            nx_graph = loader.load_network_from_place("Hanoi, Vietnam", network_type)
        
        # Đơn giản hóa nếu cần
        if simplify:
            nx_graph = loader.simplify_graph(nx_graph)
        
        # Chuyển đổi sang Graph object
        graph = loader.convert_networkx_to_graph(nx_graph)
        
        return graph
    
    except Exception as e:
        logger.error(f"Error loading map from OSM: {str(e)}")
        raise  # Không fallback về sample data nữa

def load_hanoi_map(use_cache: bool = True) -> Graph:
    """
    Load bản đồ Hà Nội từ OSM
    
    Args:
        use_cache: Có sử dụng cache không
    
    Returns:
        Graph object
    """
    return load_map_from_osm(place="Hanoi, Vietnam", network_type="drive", simplify=True)

