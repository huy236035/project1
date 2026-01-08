"""
Xử lý các loại message khác nhau
"""
from typing import Dict, Any

class MessageHandler:
    """
    Xử lý các loại message
    """
    
    @staticmethod
    def format_route_message(route_info: Dict[str, Any]) -> str:
        """
        Format message cho route
        
        Args:
            route_info: Thông tin route
        
        Returns:
            Message đã format
        """
        route = route_info.get('route', [])
        distance = route_info.get('distance', 0)
        
        if len(route) == 0:
            return "Không tìm thấy đường đi"
        
        route_str = " -> ".join(str(point) for point in route)
        return f"Đường đi: {route_str}\nKhoảng cách: {distance:.2f} km"
    
    @staticmethod
    def format_error_message(error: Exception) -> str:
        """
        Format message lỗi
        
        Args:
            error: Exception object
        
        Returns:
            Message lỗi đã format
        """
        return f"Đã xảy ra lỗi: {str(error)}"
    
    @staticmethod
    def format_status_message(status: str, progress: int) -> str:
        """
        Format message trạng thái
        
        Args:
            status: Trạng thái
            progress: Tiến độ (0-100)
        
        Returns:
            Message trạng thái đã format
        """
        status_map = {
            'pending': 'Đang chờ',
            'processing': 'Đang xử lý',
            'completed': 'Hoàn thành',
            'failed': 'Thất bại'
        }
        
        status_text = status_map.get(status, status)
        return f"{status_text} ({progress}%)"

