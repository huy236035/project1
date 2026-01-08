"""
Xử lý thông tin tắc đường
"""
from map.data.traffic_data import get_traffic_factor

class TrafficHandler:
    """
    Xử lý thông tin tắc đường
    """
    
    def __init__(self):
        self.traffic_data = {}
    
    def get_traffic_factor(self, node_id):
        """
        Lấy hệ số tắc đường cho một node
        
        Args:
            node_id: ID của node
        
        Returns:
            Hệ số tắc đường (1.0 = bình thường, >1.0 = tắc đường)
        """
        return get_traffic_factor(node_id)
    
    def update_traffic(self, node_id, factor):
        """
        Cập nhật thông tin tắc đường cho một node
        
        Args:
            node_id: ID của node
            factor: Hệ số tắc đường
        """
        self.traffic_data[node_id] = factor
    
    def apply_traffic_to_weight(self, node_id, base_weight):
        """
        Áp dụng hệ số tắc đường vào trọng số cạnh
        
        Args:
            node_id: ID của node
            base_weight: Trọng số gốc
        
        Returns:
            Trọng số sau khi áp dụng tắc đường
        """
        factor = self.get_traffic_factor(node_id)
        return base_weight * factor

