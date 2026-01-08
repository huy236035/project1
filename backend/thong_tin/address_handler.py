"""
Xử lý địa chỉ các điểm người dùng chọn
"""
from typing import List, Dict
from thong_tin.models.location import Location
from thong_tin.models.address import Address

class AddressHandler:
    """
    Xử lý địa chỉ các điểm
    """
    
    def __init__(self):
        self.locations = []
    
    def add_location(self, location: Location):
        """
        Thêm một địa điểm
        
        Args:
            location: Location object
        """
        self.locations.append(location)
    
    def add_location_from_coords(self, lat: float, lng: float, name: str = None):
        """
        Thêm địa điểm từ tọa độ
        
        Args:
            lat: Vĩ độ
            lng: Kinh độ
            name: Tên địa điểm
        """
        location = Location(lat=lat, lng=lng, name=name)
        self.add_location(location)
    
    def get_locations(self) -> List[Location]:
        """
        Lấy danh sách địa điểm
        
        Returns:
            List các Location
        """
        return self.locations
    
    def clear_locations(self):
        """
        Xóa tất cả địa điểm
        """
        self.locations = []
    
    def locations_to_coordinates(self) -> List[Dict]:
        """
        Chuyển đổi danh sách địa điểm sang tọa độ
        
        Returns:
            List các dict chứa lat, lng
        """
        return [{'lat': loc.lat, 'lng': loc.lng} for loc in self.locations]

