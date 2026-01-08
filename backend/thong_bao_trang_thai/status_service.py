"""
Service quản lý trạng thái request
"""
from typing import Dict, Optional
from enum import Enum
from datetime import datetime

class RequestStatus(Enum):
    """
    Trạng thái request
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class StatusService:
    """
    Service quản lý trạng thái
    """
    
    def __init__(self):
        self.requests = {}
    
    def create_request(self, request_id: str, user_id: Optional[str] = None) -> Dict:
        """
        Tạo request mới
        
        Args:
            request_id: ID của request
            user_id: ID người dùng
        
        Returns:
            Dict chứa thông tin request
        """
        request = {
            'id': request_id,
            'user_id': user_id,
            'status': RequestStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        self.requests[request_id] = request
        return request
    
    def update_status(self, request_id: str, status: RequestStatus, 
                     progress: Optional[int] = None, message: Optional[str] = None):
        """
        Cập nhật trạng thái request
        
        Args:
            request_id: ID của request
            status: Trạng thái mới
            progress: Tiến độ (0-100)
            message: Thông báo
        """
        if request_id not in self.requests:
            return
        
        request = self.requests[request_id]
        request['status'] = status.value
        request['updated_at'] = datetime.now().isoformat()
        
        if progress is not None:
            request['progress'] = progress
        
        if message:
            request['message'] = message
    
    def get_status(self, request_id: str) -> Optional[Dict]:
        """
        Lấy trạng thái request
        
        Args:
            request_id: ID của request
        
        Returns:
            Dict chứa thông tin request hoặc None
        """
        return self.requests.get(request_id)
    
    def mark_processing(self, request_id: str):
        """
        Đánh dấu request đang xử lý
        """
        self.update_status(request_id, RequestStatus.PROCESSING, progress=50)
    
    def mark_completed(self, request_id: str, result: Optional[Dict] = None):
        """
        Đánh dấu request hoàn thành
        """
        self.update_status(request_id, RequestStatus.COMPLETED, progress=100)
        if result:
            self.requests[request_id]['result'] = result
    
    def mark_failed(self, request_id: str, error_message: str):
        """
        Đánh dấu request thất bại
        """
        self.update_status(request_id, RequestStatus.FAILED, 
                          progress=0, message=error_message)

