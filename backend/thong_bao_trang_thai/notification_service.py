"""
Service gửi thông báo cho người dùng
"""
from typing import Dict, Any, Optional

class NotificationService:
    """
    Service gửi thông báo
    """
    
    def __init__(self):
        self.notifications = []
    
    def send_notification(self, user_id: Optional[str], message: str, 
                         notification_type: str = "info") -> bool:
        """
        Gửi thông báo cho người dùng
        
        Args:
            user_id: ID người dùng (None nếu không cần)
            message: Nội dung thông báo
            notification_type: Loại thông báo (info, success, error, warning)
        
        Returns:
            True nếu gửi thành công
        """
        notification = {
            'user_id': user_id,
            'message': message,
            'type': notification_type,
            'timestamp': self._get_timestamp()
        }
        
        self.notifications.append(notification)
        
        # TODO: Implement gửi thông báo thực tế (email, push, SMS)
        print(f"[NOTIFICATION] {notification_type.upper()}: {message}")
        
        return True
    
    def notify_route_calculated(self, user_id: Optional[str], route_info: Dict[str, Any]):
        """
        Thông báo khi tính toán route xong
        
        Args:
            user_id: ID người dùng
            route_info: Thông tin route
        """
        distance = route_info.get('distance', 0)
        num_points = len(route_info.get('route', []))
        
        message = f"Đã tìm được đường đi qua {num_points} điểm, tổng khoảng cách: {distance:.2f} km"
        self.send_notification(user_id, message, "success")
    
    def notify_error(self, user_id: Optional[str], error_message: str):
        """
        Thông báo lỗi
        
        Args:
            user_id: ID người dùng
            error_message: Thông báo lỗi
        """
        self.send_notification(user_id, f"Lỗi: {error_message}", "error")
    
    def _get_timestamp(self) -> str:
        """
        Lấy timestamp hiện tại
        
        Returns:
            Timestamp dạng string
        """
        from datetime import datetime
        return datetime.now().isoformat()

