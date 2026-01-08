"""
Service quản lý vị trí
KHÔNG dùng sample data nữa - chỉ dùng OSM
"""
from typing import List, Optional, Dict
from thong_tin.models.location import Location

class LocationService:
    """
    Service quản lý vị trí
    """
    
    def __init__(self, map_service=None):
        """
        Khởi tạo LocationService
        
        Args:
            map_service: MapDataService instance (optional, để tìm node từ OSM)
        """
        self.map_service = map_service
    
    def addresses_to_nodes(self, locations: List[Location]) -> List[str]:
        """
        Chuyển đổi địa chỉ sang nodes trong graph
        Tìm node gần nhất với mỗi địa chỉ
        
        Args:
            locations: List các Location
        
        Returns:
            List các node_id
        """
        nodes = []
        for location in locations:
            # Tìm node gần nhất
            node_id = self._find_nearest_node(location.lat, location.lng)
            if node_id:
                nodes.append(node_id)
                location.node_id = node_id
            else:
                # Fallback: sử dụng tọa độ trực tiếp nếu không tìm thấy node
                nodes.append(f"custom_{len(nodes)}")
                location.node_id = f"custom_{len(nodes)-1}"
        
        return nodes
    
    def _find_nearest_node(self, lat: float, lng: float) -> Optional[str]:
        """
        Tìm node gần nhất với tọa độ cho trước
        
        Args:
            lat: Vĩ độ
            lng: Kinh độ
        
        Returns:
            node_id gần nhất hoặc None
        """
        # Ưu tiên tìm từ map_service (OSM data)
        if self.map_service:
            node_id = self.map_service.find_nearest_node(lat, lng)
            if node_id:
                return node_id
        
        # Không có fallback về sample data nữa
        # Nếu không tìm thấy từ map_service, return None
        return None
    
    def get_node_coordinates(self, node_id: str) -> Optional[Dict]:
        """
        Lấy tọa độ của một node
        
        Args:
            node_id: ID của node
        
        Returns:
            Dict chứa lat, lng hoặc None
        """
        # Ưu tiên lấy từ map_service
        if self.map_service:
            coords = self.map_service.get_node_coordinates(node_id)
            if coords:
                return coords
        
        # Không có fallback về sample data nữa
        return None

