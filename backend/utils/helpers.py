"""
Helper functions
"""
from __future__ import annotations
from typing import List, Dict, Any

def generate_request_id() -> str:
    """
    Tạo request ID duy nhất
    
    Returns:
        Request ID
    """
    import uuid
    return str(uuid.uuid4())

def validate_points(points: List[Dict[str, float]]) -> tuple[bool, str]:
    """
    Validate danh sách điểm
    
    Args:
        points: List các dict chứa lat, lng
    
    Returns:
        (is_valid, error_message)
    """
    if not points:
        return False, "Danh sách điểm không được rỗng"
    
    if len(points) < 2:
        return False, "Cần ít nhất 2 điểm"
    
    return True, ""

