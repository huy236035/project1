"""
Custom exceptions
"""

class RouteException(Exception):
    """Exception cho route"""
    pass

class InvalidCoordinatesException(RouteException):
    """Exception khi tọa độ không hợp lệ"""
    pass

class NoPathFoundException(RouteException):
    """Exception khi không tìm thấy đường đi"""
    pass

class InvalidLocationException(RouteException):
    """Exception khi địa điểm không hợp lệ"""
    pass

