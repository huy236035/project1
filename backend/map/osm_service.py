"""
Service đơn giản và hiệu quả để load OSM data
Tối ưu hóa để đảm bảo tính chính xác của tọa độ và khoảng cách
"""
from __future__ import annotations
from typing import Dict, Tuple, Optional
from utils.logger import logger

# Cache để tránh load lại nhiều lần
_OSM_CACHE: Dict[str, Tuple] = {}

def load_osm_data(place: str = "Hanoi, Vietnam", 
                  network_type: str = "drive",
                  use_cache: bool = True) -> Tuple:
    """
    Load OSM data một cách đơn giản và hiệu quả
    Trả về (graph, node_coordinates) từ cùng một nx_graph
    
    Args:
        place: Tên địa điểm
        network_type: Loại mạng lưới
        use_cache: Có sử dụng cache không
    
    Returns:
        (graph, node_coordinates) tuple
    """
    cache_key = f"{place}_{network_type}"
    
    # Kiểm tra cache
    if use_cache and cache_key in _OSM_CACHE:
        logger.info(f"Using cached OSM data for {place}")
        return _OSM_CACHE[cache_key]
    
    try:
        # Import OSMnx trực tiếp
        import osmnx as ox
        import networkx as nx
        from thuat_toan.utils.graph import Graph
        from thuat_toan.utils.distance_calculator import haversine_distance
        
        logger.info(f"Loading OSM data for {place}...")
        
        # Cấu hình OSMnx
        ox.settings.use_cache = True
        ox.settings.log_console = False
        
        # Load network từ OSM - một lần duy nhất
        nx_graph = ox.graph_from_place(place, network_type=network_type)
        logger.info(f"Loaded {len(nx_graph.nodes)} nodes and {len(nx_graph.edges)} edges from OSM")
        
        # Đơn giản hóa graph
        try:
            nx_graph = ox.simplify_graph(nx_graph)
            logger.info(f"Simplified to {len(nx_graph.nodes)} nodes and {len(nx_graph.edges)} edges")
        except Exception as e:
            logger.warning(f"Could not simplify graph: {str(e)}")
        
        # Lấy node coordinates từ nx_graph
        node_coordinates = {}
        for node_id, data in nx_graph.nodes(data=True):
            if 'y' in data and 'x' in data:
                # OSMnx: y = lat, x = lng
                node_coordinates[str(node_id)] = {
                    'lat': float(data['y']),
                    'lng': float(data['x'])
                }
        
        logger.info(f"Extracted {len(node_coordinates)} node coordinates")
        
        # Convert nx_graph sang Graph object
        graph = Graph()
        
        # Thêm các edges với khoảng cách chính xác
        for u, v, data in nx_graph.edges(data=True):
            u_str = str(u)
            v_str = str(v)
            
            # Tính khoảng cách
            distance = None
            
            # Ưu tiên 1: Dùng length từ OSM (chính xác nhất)
            if 'length' in data:
                # length từ OSM tính bằng mét, chuyển sang km
                distance = float(data['length']) / 1000.0
            # Ưu tiên 2: Tính từ tọa độ bằng Haversine
            elif u_str in node_coordinates and v_str in node_coordinates:
                coords_u = node_coordinates[u_str]
                coords_v = node_coordinates[v_str]
                distance = haversine_distance(
                    coords_u['lat'], coords_u['lng'],
                    coords_v['lat'], coords_v['lng']
                )
            else:
                # Fallback: default distance
                distance = 1.0
                logger.warning(f"Could not calculate distance for edge ({u_str}, {v_str}), using default 1.0 km")
            
            graph.add_edge(u_str, v_str, distance)
        
        logger.info(f"Converted to Graph with {len(graph.get_all_nodes())} nodes")
        
        # Kiểm tra đồng bộ
        graph_nodes = set(graph.get_all_nodes())
        coord_nodes = set(node_coordinates.keys())
        
        if graph_nodes != coord_nodes:
            missing = graph_nodes - coord_nodes
            extra = coord_nodes - graph_nodes
            if missing:
                logger.warning(f"{len(missing)} nodes in graph without coordinates")
            if extra:
                logger.warning(f"{len(extra)} nodes in coordinates not in graph")
        else:
            logger.info("Graph and node coordinates are synchronized")
        
        result = (graph, node_coordinates)
        
        # Cache kết quả
        if use_cache:
            _OSM_CACHE[cache_key] = result
        
        return result
        
    except ImportError:
        error_msg = "osmnx chưa được cài đặt. Vui lòng cài đặt: pip install osmnx networkx geopy"
        logger.error(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        logger.error(f"Error loading OSM data: {str(e)}")
        raise  # Không fallback về sample data nữa

def clear_cache():
    """Xóa cache OSM data"""
    global _OSM_CACHE
    _OSM_CACHE.clear()
    logger.info("OSM cache cleared")

