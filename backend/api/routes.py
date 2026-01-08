"""
Đăng ký tất cả routes
"""
from flask import Flask
from api.route_api import route_bp

def register_routes(app: Flask):
    """
    Đăng ký tất cả routes vào Flask app
    
    Args:
        app: Flask app instance
    """
    app.register_blueprint(route_bp, url_prefix='/api')

