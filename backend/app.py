import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask
from flask_cors import CORS
from config import Config
from api.routes import register_routes
from utils.logger import logger

def create_app():
    app = Flask(__name__)
    CORS(app, origins=Config.CORS_ORIGINS)
    register_routes(app)
    
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'service': 'route-finder'}, 200
    
    logger.info("Flask app initialized")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
