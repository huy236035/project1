"""
Format kết quả trả về
"""
from typing import Dict, Any, List

class ResultFormatter:
    """
    Format kết quả trả về
    """
    
    @staticmethod
    def format_route_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format kết quả route
        
        Args:
            result: Kết quả từ Solver
        
        Returns:
            Dict đã format
        """
        return {
            'success': True,
            'route': result.get('route', []),
            'distance': round(result.get('distance', 0), 2),
            'path_coordinates': result.get('path_coordinates', []),
            'message': result.get('message', 'Tìm đường đi thành công')
        }
    
    @staticmethod
    def format_error_result(error_message: str) -> Dict[str, Any]:
        """
        Format kết quả lỗi
        
        Args:
            error_message: Thông báo lỗi
        
        Returns:
            Dict chứa thông tin lỗi
        """
        return {
            'success': False,
            'error': error_message,
            'route': [],
            'distance': 0,
            'path_coordinates': []
        }
    
    @staticmethod
    def format_multi_route_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format kết quả multi-route
        Trả về route indices để frontend gọi OSM Routing API
        
        Args:
            result: Kết quả từ Solver
        
        Returns:
            Dict đã format với route là indices (0, 1, 2, ...)
        """
        return {
            'success': True,
            'route': result.get('route', []),  # [0, 2, 1, 3] - thứ tự tối ưu các điểm
            'distance': round(result.get('distance', 0), 2),  # Khoảng cách ước tính
            'message': result.get('message', 'Tìm đường đi thành công')
        }

