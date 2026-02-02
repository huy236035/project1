"""
Xây dựng response JSON
"""
from typing import Dict, Any, Optional
from flask import jsonify
from ket_qua.result_formatter import ResultFormatter

class ResponseBuilder:
    @staticmethod
    def success_response(data: Dict[str, Any], status_code: int = 200):
        response = {
            'success': True,
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(error_message: str, status_code: int = 400):
        response = {
            'success': False,
            'error': error_message
        }
        return jsonify(response), status_code
    
    @staticmethod
    def route_response(result: Dict[str, Any], status_code: int = 200):
        formatted = ResultFormatter.format_route_result(result)
        return jsonify(formatted), status_code
    
    @staticmethod
    def multi_route_response(result: Dict[str, Any], status_code: int = 200):
        formatted = ResultFormatter.format_multi_route_result(result)
        return jsonify(formatted), status_code
