# Thuật toán Genetic Algorithm (GA) - Tối ưu route cho nhiều điểm
import random
import math
from typing import List, Tuple

def calculate_route_distance(graph, route):
    """
    Tính tổng khoảng cách của một route
    route: ['A', 'B', 'C', 'D']
    """
    if len(route) < 2:
        return 0
    
    total_distance = 0
    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]
        
        # Tìm weight giữa 2 node
        neighbors = dict(graph.get_neighbors(start))
        if end in neighbors:
            total_distance += neighbors[end]
        else:
            # Nếu không có đường trực tiếp, return infinity
            return float('inf')
    
    return total_distance

def create_initial_population(points, population_size):
    """
    Tạo population ban đầu
    points: ['A', 'B', 'C', 'D', 'E']
    """
    population = []
    
    # Giữ điểm đầu tiên cố định (start point)
    start_point = points[0]
    other_points = points[1:]
    
    for _ in range(population_size):
        # Shuffle các điểm còn lại
        shuffled = other_points.copy()
        random.shuffle(shuffled)
        route = [start_point] + shuffled
        population.append(route)
    
    return population

def fitness(graph, route):
    """
    Tính fitness của một route (khoảng cách càng ngắn thì fitness càng cao)
    Fitness = 1 / (distance + 1) để tránh chia cho 0
    """
    distance = calculate_route_distance(graph, route)
    if distance == float('inf'):
        return 0
    return 1 / (distance + 1)

def selection(population, fitness_scores, num_parents):
    """
    Chọn parents dựa trên fitness (tournament selection)
    """
    parents = []
    
    for _ in range(num_parents):
        # Tournament selection: chọn 3 cá thể ngẫu nhiên, lấy tốt nhất
        tournament_size = 3
        tournament = random.sample(list(zip(population, fitness_scores)), 
                                   min(tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x[1])
        parents.append(winner[0])
    
    return parents

def crossover(parent1, parent2):
    """
    Order Crossover (OX) - phù hợp cho TSP
    Đảm bảo không có duplicate và giữ điểm đầu cố định
    """
    if len(parent1) < 3:
        return parent1.copy(), parent2.copy()
    
    # Điểm đầu luôn giữ nguyên
    start_point = parent1[0]
    p1_rest = parent1[1:]
    p2_rest = parent2[1:]
    
    # Chọn 2 điểm cắt ngẫu nhiên
    if len(p1_rest) < 2:
        return parent1.copy(), parent2.copy()
    
    start = random.randint(0, len(p1_rest) - 1)
    end = random.randint(start + 1, len(p1_rest))
    
    # Tạo child1
    segment1 = p1_rest[start:end]
    remaining1 = [x for x in p2_rest if x not in segment1]
    child1 = [start_point] + remaining1[:start] + segment1 + remaining1[start:]
    
    # Tạo child2
    segment2 = p2_rest[start:end]
    remaining2 = [x for x in p1_rest if x not in segment2]
    child2 = [start_point] + remaining2[:start] + segment2 + remaining2[start:]
    
    return child1, child2

def mutate(route, mutation_rate=0.1):
    """
    Mutation: đổi chỗ 2 điểm ngẫu nhiên (trừ điểm đầu)
    """
    if random.random() < mutation_rate and len(route) > 3:
        # Chọn 2 điểm ngẫu nhiên (trừ điểm đầu)
        idx1, idx2 = random.sample(range(1, len(route)), 2)
        route[idx1], route[idx2] = route[idx2], route[idx1]
    
    return route

def genetic_algorithm(graph, points, population_size=50, generations=100, 
                     mutation_rate=0.1, elite_size=5):
    """
    Thuật toán Genetic Algorithm để tối ưu route cho nhiều điểm
    
    Args:
        graph: Đồ thị
        points: List các điểm cần thăm ['A', 'B', 'C', 'D', 'E']
        population_size: Số lượng cá thể trong population
        generations: Số thế hệ
        mutation_rate: Tỷ lệ mutation
        elite_size: Số cá thể tốt nhất giữ lại mỗi thế hệ
    
    Returns:
        {
            'route': ['A', 'B', 'C', 'D', 'E'],
            'distance': 10.5
        }
    """
    if len(points) < 2:
        return {
            'route': points,
            'distance': 0
        }
    
    if len(points) == 2:
        # Nếu chỉ có 2 điểm, dùng A* hoặc Dijkstra
        from algorithms.astar import astar
        result = astar(graph, points[0], points[1])
        return {
            'route': result['path'],
            'distance': result['distance']
        }
    
    # Tạo population ban đầu
    population = create_initial_population(points, population_size)
    
    best_route = None
    best_distance = float('inf')
    
    # Vòng lặp qua các thế hệ
    for generation in range(generations):
        # Tính fitness cho mỗi cá thể
        fitness_scores = [fitness(graph, route) for route in population]
        
        # Tìm cá thể tốt nhất
        best_idx = fitness_scores.index(max(fitness_scores))
        current_best = population[best_idx]
        current_distance = calculate_route_distance(graph, current_best)
        
        if current_distance < best_distance:
            best_route = current_best.copy()
            best_distance = current_distance
        
        # Tạo thế hệ mới
        new_population = []
        
        # Elitism: giữ lại các cá thể tốt nhất
        elite_indices = sorted(range(len(fitness_scores)), 
                              key=lambda i: fitness_scores[i], 
                              reverse=True)[:elite_size]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
        
        # Tạo các cá thể mới bằng crossover và mutation
        while len(new_population) < population_size:
            # Chọn parents
            parents = selection(population, fitness_scores, 2)
            
            # Crossover
            child1, child2 = crossover(parents[0], parents[1])
            
            # Mutation
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)
        
        population = new_population[:population_size]
    
    return {
        'route': best_route if best_route else points,
        'distance': best_distance
    }

