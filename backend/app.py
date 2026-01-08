"""
Flask application chính
"""
import sys
import os

# Thêm thư mục backend vào sys.path để absolute imports hoạt động
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask
from flask_cors import CORS
from config import Config
from api.routes import register_routes
from utils.logger import logger

def create_app():
    """
    Tạo Flask app
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # CORS
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Đăng ký routes
    register_routes(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'service': 'route-finder'}, 200
    
    logger.info("Flask app initialized")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)

