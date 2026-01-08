"""
Dữ liệu nodes bản đồ Hà Nội
"""
# Lazy import - chỉ import khi cần
def _get_osm_loader():
    """Lấy OSMLoader, chỉ import khi cần"""
    from map.osm_loader import OSMLoader, is_osm_available
    return OSMLoader, is_osm_available

def _get_logger():
    """Lấy logger"""
    from utils.logger import logger
    return logger

# Biến global để lưu nodes từ OSM
_OSM_NODES = None

def load_nodes_from_osm(place: str = "Hanoi, Vietnam", 
                       network_type: str = "drive",
                       force_reload: bool = False) -> dict:
    """
    Load nodes từ OpenStreetMap
    
    Args:
        place: Tên địa điểm
        network_type: Loại mạng lưới
        force_reload: Có force reload không
    
    Returns:
        Dict chứa nodes với key là node_id và value là {'lat': ..., 'lng': ...}
    
    Raises:
        ImportError: Nếu osmnx chưa được cài đặt
        Exception: Nếu không thể load từ OSM
    """
    global _OSM_NODES
    
    if _OSM_NODES is not None and not force_reload:
        return _OSM_NODES
    
    # Lazy import
    OSMLoader, is_osm_available = _get_osm_loader()
    logger = _get_logger()
    
    # Kiểm tra OSM có sẵn không
    if not is_osm_available():
        error_msg = "osmnx chưa được cài đặt. Vui lòng cài đặt: pip install osmnx networkx geopy"
        logger.error(error_msg)
        raise ImportError(error_msg)
    
    try:
        loader = OSMLoader()
        nx_graph = loader.load_network_from_place(place, network_type)
        _OSM_NODES = loader.get_nodes_coordinates(nx_graph)
        logger.info(f"Loaded {len(_OSM_NODES)} nodes from OSM")
        return _OSM_NODES
    except Exception as e:
        logger.error(f"Error loading nodes from OSM: {str(e)}")
        raise

def get_nodes(use_osm: bool = True) -> dict:
    """
    Lấy nodes từ OSM
    
    Args:
        use_osm: Có sử dụng OSM không (phải là True)
    
    Returns:
        Dict chứa nodes
    
    Raises:
        ImportError: Nếu osmnx chưa được cài đặt
    """
    if not use_osm:
        raise ValueError("Sample data đã bị xóa. Chỉ có thể dùng OSM data.")
    
    return load_nodes_from_osm()

# Export NODES - sẽ load từ OSM khi được gọi
# Không export NODES mặc định để tránh lỗi khi import
NODES = {}  # Empty dict, sẽ được load từ OSM khi cần

