"""
API routes cho tìm đường đi
"""
from flask import Blueprint, request
from thuat_toan.solver import RouteSolver
from thong_tin.models.location import Location
from thong_tin.data_validator import DataValidator
from ket_qua.response_builder import ResponseBuilder
from utils.exceptions import InvalidCoordinatesException, NoPathFoundException
from utils.logger import logger

route_bp = Blueprint('route', __name__)

@route_bp.route('/route', methods=['GET'])
def find_route():
    """
    Tìm đường đi giữa 2 điểm
    
    Query params:
        start: Node ID điểm bắt đầu
        end: Node ID điểm kết thúc
    """
    try:
        start = request.args.get("start")
        end = request.args.get("end")
        
        if not start or not end:
            return ResponseBuilder.error_response("Thiếu start hoặc end", 400)
        
        solver = RouteSolver()
        graph = solver.map_service.get_graph()
        
        from thuat_toan.algorithms.astar import astar
        from thuat_toan.utils.path_converter import nodes_to_coordinates
        
        # Lấy node_coordinates từ map_service
        node_coords = solver.map_service.get_all_node_coordinates()
        result = astar(graph, start, end, node_coordinates=node_coords)
        
        if result['distance'] == float('inf'):
            return ResponseBuilder.error_response("Không tìm thấy đường đi", 404)
        
        coords = nodes_to_coordinates(result["path"], node_coordinates=node_coords)
        
        return ResponseBuilder.success_response({
            "distance": result["distance"],
            "path": coords,
            "path_nodes": result["path"]
        })
    
    except Exception as e:
        logger.error(f"Error in find_route: {str(e)}")
        return ResponseBuilder.error_response(str(e), 500)

@route_bp.route('/multi-route', methods=['POST'])
def find_multi_route():
    """
    Tìm route tối ưu đi qua nhiều điểm từ tọa độ GPS
    
    Request body:
    {
        "points": [
            {"lat": 21.0285, "lng": 105.8542},
            {"lat": 21.0300, "lng": 105.8560},
            ...
        ],
        "consider_traffic": true (optional),
        "ga_population_size": 100 (optional),
        "ga_generations": 500 (optional)
    }
    """
    try:
        data = request.get_json()
        points = data.get("points", [])
        
        # Validate dữ liệu
        is_valid, error_message = DataValidator.validate_coordinates(points)
        if not is_valid:
            return ResponseBuilder.error_response(error_message, 400)
        
        # Lấy các tham số tùy chọn
        consider_traffic = data.get("consider_traffic", True)
        ga_population_size = data.get("ga_population_size", 100)
        ga_generations = data.get("ga_generations", 500)
        
        # Tạo solver và giải
        solver = RouteSolver(consider_traffic=consider_traffic)
        result = solver.solve_from_coordinates(
            points,
            ga_population_size=ga_population_size,
            ga_generations=ga_generations
        )
        
        # Format và trả về kết quả
        return ResponseBuilder.multi_route_response(result)
    
    except Exception as e:
        logger.error(f"Error in find_multi_route: {str(e)}")
        return ResponseBuilder.error_response(str(e), 500)

