
# Solver kết hợp OSRM và Chiến thuật lai (Held-Karp / GA+2Opt) để tìm đường đi ngắn nhất

from __future__ import annotations
from typing import List, Dict, Any, Tuple
from thuat_toan.algorithms.genetic_algorithm import genetic_algorithm
from thuat_toan.algorithms.held_karp import held_karp
from thong_tin.osrm_service import OSRMService
from utils.logger import logger

class MatrixGraph:
    """Wrapper để GA có thể đọc ma trận khoảng cách như một đồ thị"""
    def __init__(self, matrix):
        self.matrix = matrix
        self.n = len(matrix)

    def get_neighbors(self, node):
        idx = int(node)
        return [(i, self.matrix[idx][i]) for i in range(self.n) if i != idx]

class RouteSolver:
    """
    - N <= 12: Held-Karp 
    - N > 12: GA + 2-Opt 
    """
    
    def __init__(self, consider_traffic: bool = True):
        self.consider_traffic = consider_traffic
    
    def solve_from_coordinates(self, coordinates: List[Dict[str, float]],
                               ga_population_size: int = 100,
                               ga_generations: int = 100) -> Dict[str, Any]:
      
        n = len(coordinates)
        if n < 2:
            return {
                'route': list(range(n)),
                'distance': 0,
                'message': 'Cần ít nhất 2 điểm'
            }
        
        
        # 1. Lấy Ma trận khoảng cách từ OSRM
        import time
        start_osrm = time.time()
        matrix = OSRMService.get_distance_matrix(coordinates)
        end_osrm = time.time()
        logger.info(f"OSRM Request Time: {end_osrm - start_osrm:.4f}s")
        
        if not matrix:
            logger.error("Failed to get distance matrix from OSRM")
            return {
                'route': [],
                'distance': 0,
                'message': 'Lỗi kết nối OSRM (Không lấy được dữ liệu bản đồ). Vui lòng thử lại.'
            }
            
        logger.info(f"Using OSRM Distance Matrix for {n} points")
        
        result_route = []
        result_distance = 0
        algo_name = ""
        
        start_algo = time.time()
        # 2. Chọn thuật toán dựa trên N
        if n <= 12:
            logger.info("N <= 12: Using Held-Karp Algorithm (Exact)")
            hk_result = held_karp(matrix)
            result_route = hk_result['route']
            result_distance = hk_result['distance']
            algo_name = "Held-Karp (Chính xác tuyệt đối)"
        else:
            logger.info("N > 12: Using Genetic Algorithm + 2-Opt")
            # PASS RAW MATRIX instead of Graph Wrapper for performance
            # graph = MatrixGraph(matrix) 
            nodes = list(range(n))
            
            ga_result = genetic_algorithm(
                matrix, # Pass matrix directly
                nodes,
                population_size=ga_population_size,
                generations=ga_generations
            )
            result_route = ga_result['route']
            result_distance = ga_result['distance']
            algo_name = "Memetic Algorithm (GA + 2-Opt)"
            
        end_algo = time.time()
        logger.info(f"Algorithm Execution Time: {end_algo - start_algo:.4f}s")
            
        # 3. Xử lý kết quả (Convert m -> km)
        distance_km = result_distance / 1000.0
            
        return {
            'route': result_route, 
            'distance': round(distance_km, 2),
            'message': f'Tối ưu thành công bằng {algo_name}'
        }
