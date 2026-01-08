""" đổi danh sách các node thành tọa độ GPS
    path: ['A', 'B', 'C']
    return: [{'lat': ..., 'lng': ...}, ...]
    
    DEPRECATED: Không dùng sample data nữa
    Sử dụng node_coordinates từ map_service thay thế
"""
from typing import List, Dict

def nodes_to_coordinates(path: List[str], node_coordinates: Dict = None):
    """
    Đổi danh sách các node thành tọa độ GPS
    
    Args:
        path: List các node_id
        node_coordinates: Dict chứa tọa độ các nodes (từ OSM)
    
    Returns:
        List các dict chứa lat, lng
    """
    if node_coordinates is None:
        raise ValueError("node_coordinates phải được cung cấp. Sample data đã bị xóa.")
    
    coords = []
    for node in path:
        node_str = str(node)
        if node_str not in node_coordinates:
            raise ValueError(f"Node {node_str} không có tọa độ trong node_coordinates")
        
        coords.append({
            "lat": node_coordinates[node_str]["lat"],
            "lng": node_coordinates[node_str]["lng"]
        })
    
    return coords

