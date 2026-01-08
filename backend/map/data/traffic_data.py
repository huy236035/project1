"""
Dữ liệu tắc đường Hà Nội
Có thể mở rộng để lấy từ API real-time hoặc file JSON
"""
# Ví dụ dữ liệu tắc đường
# Format: {node_id: traffic_factor}
# traffic_factor > 1.0 nghĩa là tắc đường (tăng thời gian đi)
TRAFFIC_DATA = {
    # Có thể thêm dữ liệu tắc đường ở đây
    # "A": 1.5,  # Tắc đường, tăng thời gian 50%
}

def get_traffic_factor(node_id):
    """
    Lấy hệ số tắc đường cho một node
    Returns: Hệ số (1.0 = bình thường, >1.0 = tắc đường)
    """
    return TRAFFIC_DATA.get(node_id, 1.0)

