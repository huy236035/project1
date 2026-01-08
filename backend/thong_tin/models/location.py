"""
Model địa điểm
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Location:
    """
    Model địa điểm
    """
    lat: float
    lng: float
    name: Optional[str] = None
    address: Optional[str] = None
    node_id: Optional[str] = None
    
    def to_dict(self):
        """
        Chuyển đổi sang dictionary
        """
        return {
            'lat': self.lat,
            'lng': self.lng,
            'name': self.name,
            'address': self.address,
            'node_id': self.node_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo Location từ dictionary
        """
        return cls(
            lat=data.get('lat'),
            lng=data.get('lng'),
            name=data.get('name'),
            address=data.get('address'),
            node_id=data.get('node_id')
        )

