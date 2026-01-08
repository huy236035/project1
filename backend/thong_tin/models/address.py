"""
Model địa chỉ
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Address:
    """
    Model địa chỉ
    """
    street: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str = "Hà Nội"
    full_address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    def to_dict(self):
        """
        Chuyển đổi sang dictionary
        """
        return {
            'street': self.street,
            'ward': self.ward,
            'district': self.district,
            'city': self.city,
            'full_address': self.full_address,
            'lat': self.lat,
            'lng': self.lng
        }
    
    def get_full_address(self):
        """
        Lấy địa chỉ đầy đủ
        """
        if self.full_address:
            return self.full_address
        
        parts = []
        if self.street:
            parts.append(self.street)
        if self.ward:
            parts.append(self.ward)
        if self.district:
            parts.append(self.district)
        if self.city:
            parts.append(self.city)
        
        return ", ".join(parts) if parts else ""

