"""
Quản lý mạng lưới đường
"""
from thuat_toan.utils.graph import Graph

class RoadNetwork:
    """
    Quản lý mạng lưới đường Hà Nội
    """
    
    def __init__(self, graph=None):
        self.graph = graph or Graph()
    
    def get_graph(self):
        """
        Lấy đồ thị mạng lưới đường
        
        Returns:
            Graph object
        """
        return self.graph
    
    def add_road(self, start_node, end_node, weight):
        """
        Thêm một đoạn đường vào mạng lưới
        
        Args:
            start_node: Node bắt đầu
            end_node: Node kết thúc
            weight: Trọng số (khoảng cách hoặc thời gian)
        """
        self.graph.add_edge(start_node, end_node, weight)
    
    def get_route(self, start_node, end_node):
        """
        Lấy thông tin route giữa 2 node
        
        Args:
            start_node: Node bắt đầu
            end_node: Node kết thúc
        
        Returns:
            Dict chứa thông tin route
        """
        # Có thể mở rộng để trả về thông tin chi tiết về route
        return {
            'start': start_node,
            'end': end_node,
            'exists': end_node in dict(self.graph.get_neighbors(start_node))
        }

