# Multi-point Router - Tìm route tối ưu cho nhiều điểm
from utils.graph import Graph
from algorithms.astar import astar
from algorithms.genetic_algorithm import genetic_algorithm

def calculate_distance_matrix(graph, points):
    """
    Tính ma trận khoảng cách giữa tất cả các cặp điểm
    
    Args:
        graph: Đồ thị gốc
        points: List các điểm cần tính ['A', 'B', 'C', 'D']
    
    Returns:
        distance_matrix: Dict với key là (point1, point2) và value là khoảng cách
        Ví dụ: {('A', 'B'): 3.5, ('A', 'C'): 5.2, ...}
    """
    distance_matrix = {}
    n = len(points)
    
    print(f"Calculating distances between {n} points...")
    
    for i in range(n):
        for j in range(i + 1, n):
            point1 = points[i]
            point2 = points[j]
            
            # Use A* to find shortest path between 2 points
            try:
                result = astar(graph, point1, point2)
                distance = result['distance']
                
                # Store both directions (A->B and B->A)
                distance_matrix[(point1, point2)] = distance
                distance_matrix[(point2, point1)] = distance
                
                print(f"  {point1} -> {point2}: {distance}")
            except Exception as e:
                print(f"  Error calculating {point1} -> {point2}: {e}")
                # If no path found, set distance = infinity
                distance_matrix[(point1, point2)] = float('inf')
                distance_matrix[(point2, point1)] = float('inf')
    
    return distance_matrix

def create_complete_graph(distance_matrix, points):
    """
    Tạo một complete graph từ ma trận khoảng cách
    
    Args:
        distance_matrix: Dict khoảng cách giữa các điểm
        points: List các điểm
    
    Returns:
        complete_graph: Graph đầy đủ với tất cả các edges
    """
    complete_graph = Graph()
    
    for i in range(len(points)):
        for j in range(len(points)):
            if i != j:
                point1 = points[i]
                point2 = points[j]
                distance = distance_matrix.get((point1, point2), float('inf'))
                complete_graph.add_edge(point1, point2, distance)
    
    return complete_graph

def find_optimal_route(graph, points, ga_population_size=50, ga_generations=100):
    """
    Tìm route tối ưu đi qua n điểm
    
    Quy trình:
    1. Tính khoảng cách giữa tất cả các cặp điểm (dùng A*)
    2. Tạo complete graph từ ma trận khoảng cách
    3. Dùng GA để tìm route tối ưu
    
    Args:
        graph: Đồ thị gốc (có thể không đầy đủ)
        points: List các điểm cần đi qua ['A', 'B', 'C', 'D', 'E']
        ga_population_size: Số cá thể trong GA
        ga_generations: Số thế hệ trong GA
    
    Returns:
        {
            'route': ['A', 'B', 'C', 'D', 'E'],
            'distance': 15.5,
            'distance_matrix': {...},
            'detailed_paths': {
                ('A', 'B'): {'path': ['A', 'X', 'B'], 'distance': 3.5},
                ...
            }
        }
    """
    if len(points) < 2:
        return {
            'route': points,
            'distance': 0,
            'distance_matrix': {},
            'detailed_paths': {}
        }
    
    if len(points) == 2:
        # Nếu chỉ có 2 điểm, dùng A* trực tiếp
        result = astar(graph, points[0], points[1])
        return {
            'route': result['path'],
            'distance': result['distance'],
            'distance_matrix': {(points[0], points[1]): result['distance']},
            'detailed_paths': {
                (points[0], points[1]): {
                    'path': result['path'],
                    'distance': result['distance']
                }
            }
        }
    
    # Step 1: Calculate distance matrix
    print("\n=== Step 1: Calculate distances between points ===")
    distance_matrix = calculate_distance_matrix(graph, points)
    
    # Step 2: Create complete graph
    print("\n=== Step 2: Create complete graph ===")
    complete_graph = create_complete_graph(distance_matrix, points)
    
    # Step 3: Use GA to find optimal route
    print("\n=== Step 3: Find optimal route using GA ===")
    ga_result = genetic_algorithm(
        complete_graph,
        points,
        population_size=ga_population_size,
        generations=ga_generations,
        mutation_rate=0.1,
        elite_size=5
    )
    
    # Step 4: Create detailed paths (detailed path between consecutive points)
    print("\n=== Step 4: Create detailed paths ===")
    detailed_paths = {}
    route = ga_result['route']
    
    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]
        
        # Find detailed path in original graph
        path_result = astar(graph, start, end)
        detailed_paths[(start, end)] = {
            'path': path_result['path'],
            'distance': path_result['distance']
        }
        print(f"  {start} -> {end}: {path_result['path']} (distance: {path_result['distance']})")
    
    return {
        'route': route,
        'distance': ga_result['distance'],
        'distance_matrix': distance_matrix,
        'detailed_paths': detailed_paths
    }

