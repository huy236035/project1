from flask import Blueprint, request, jsonify
from thuat_toan.solver import RouteSolver
from thong_tin.data_validator import validate_coordinates
from utils.logger import logger

route_bp = Blueprint('route', __name__)

@route_bp.route('/multi-route', methods=['POST'])
def find_multi_route():
    try:
        data = request.get_json()
        points = data.get("points", [])
        
        is_valid, error_message = validate_coordinates(points)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400
        
        consider_traffic = data.get("consider_traffic", True)
        ga_population_size = data.get("ga_population_size", 100)
        ga_generations = data.get("ga_generations", 500)
        
        solver = RouteSolver(consider_traffic=consider_traffic)
        result = solver.solve_from_coordinates(
            points,
            ga_population_size=ga_population_size,
            ga_generations=ga_generations
        )
        
        # Format response
        response = {
            'success': True,
            'route': result.get('route', []),
            'distance': result.get('distance', 0),
            'message': result.get('message', 'Thành công')
        }
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in find_multi_route: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
