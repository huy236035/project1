"""
Xây dựng response JSON
"""
from typing import Dict, Any, Optional
from flask import jsonify
from ket_qua.result_formatter import ResultFormatter

class ResponseBuilder:
    """
    Xây dựng response JSON
    """
    
    @staticmethod
    def success_response(data: Dict[str, Any], status_code: int = 200):
        """
        Tạo response thành công
        
        Args:
            data: Dữ liệu trả về
            status_code: HTTP status code
        
        Returns:
            Flask response
        """
        response = {
            'success': True,
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(error_message: str, status_code: int = 400):
        """
        Tạo response lỗi
        
        Args:
            error_message: Thông báo lỗi
            status_code: HTTP status code
        
        Returns:
            Flask response
        """
        response = {
            'success': False,
            'error': error_message
        }
        return jsonify(response), status_code
    
    @staticmethod
    def route_response(result: Dict[str, Any], status_code: int = 200):
        """
        Tạo response cho route
        
        Args:
            result: Kết quả từ Solver
            status_code: HTTP status code
        
        Returns:
            Flask response
        """
        formatted = ResultFormatter.format_route_result(result)
        return jsonify(formatted), status_code
    
    @staticmethod
    def multi_route_response(result: Dict[str, Any], status_code: int = 200):
        """
        Tạo response cho multi-route
        
        Args:
            result: Kết quả từ Solver
            status_code: HTTP status code
        
        Returns:
            Flask response
        """
        formatted = ResultFormatter.format_multi_route_result(result)
        return jsonify(formatted), status_code

