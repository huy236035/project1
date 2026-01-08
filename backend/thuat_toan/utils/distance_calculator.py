"""
Tính toán khoảng cách giữa các điểm
"""
import math

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Tính khoảng cách đường thẳng giữa 2 tọa độ GPS (Haversine)
    Trả về khoảng cách tính bằng km
    
    Args:
        lat1, lng1: Tọa độ điểm đầu
        lat2, lng2: Tọa độ điểm cuối
    
    Returns:
        Khoảng cách tính bằng km
    """
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    # Công thức Haversine
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Bán kính Trái Đất (km)
    R = 6371.0
    
    # Khoảng cách tính bằng km
    distance = R * c
    
    return distance

