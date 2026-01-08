"""
Validate dữ liệu đầu vào
"""
from __future__ import annotations
from typing import List, Dict, Any

class DataValidator:
    """
    Validate dữ liệu đầu vào
    """
    
    @staticmethod
    def validate_coordinates(coordinates: List[Dict[str, float]]) -> tuple[bool, str]:
        """
        Validate danh sách tọa độ
        
        Args:
            coordinates: List các dict chứa lat, lng
        
        Returns:
            (is_valid, error_message)
        """
        if not coordinates:
            return False, "Danh sách tọa độ không được rỗng"
        
        if len(coordinates) < 2:
            return False, "Cần ít nhất 2 điểm"
        
        for i, coord in enumerate(coordinates):
            if 'lat' not in coord or 'lng' not in coord:
                return False, f"Điểm {i+1} thiếu lat hoặc lng"
            
            lat = coord['lat']
            lng = coord['lng']
            
            if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
                return False, f"Điểm {i+1}: lat và lng phải là số"
            
            if not (-90 <= lat <= 90):
                return False, f"Điểm {i+1}: lat phải trong khoảng [-90, 90]"
            
            if not (-180 <= lng <= 180):
                return False, f"Điểm {i+1}: lng phải trong khoảng [-180, 180]"
        
        return True, ""
    
    @staticmethod
    def validate_location_data(data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate dữ liệu địa điểm
        
        Args:
            data: Dict chứa thông tin địa điểm
        
        Returns:
            (is_valid, error_message)
        """
        required_fields = ['lat', 'lng']
        
        for field in required_fields:
            if field not in data:
                return False, f"Thiếu trường bắt buộc: {field}"
        
        return DataValidator.validate_coordinates([data])

