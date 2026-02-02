# Thuật toán Genetic Algorithm (GA) 
import random
import math
from typing import List, Tuple

def calculate_route_distance(matrix, route):
    """
    Tính tổng khoảng cách của một route (quay về điểm xuất phát)
    Truy cập trực tiếp Matrix[i][j] thay vì qua lớp Wrapper để tối ưu tốc độ
    """
    if len(route) < 2:
        return 0
    
    total_distance = 0
    n = len(matrix)
    
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        
        # Matrix lookup O(1) instead of dict creation
        if u < n and v < n:
            total_distance += matrix[u][v]
        else:
            return float('inf')
            
    last = route[-1]
    first = route[0]
    
    if last < n and first < n:
        total_distance += matrix[last][first]
    else:
        return float('inf')
    
    return total_distance

def create_initial_population(points, population_size):
    population = []
    
    # Giữ điểm đầu tiên cố định (start point)
    start_point = points[0]
    other_points = points[1:]
    
    for _ in range(population_size):
        shuffled = other_points.copy()
        random.shuffle(shuffled)
        route = [start_point] + shuffled
        population.append(route)
    
    return population

def fitness(matrix, route):
    distance = calculate_route_distance(matrix, route)
    if distance == float('inf'):
        return 0
    return 1 / (distance + 1)

def selection(population, fitness_scores, num_parents):
    parents = []
    
    for _ in range(num_parents):
        # Chọn 3 cá thể ngẫu nhiên, lấy tốt nhất
        tournament_size = 3
        tournament = random.sample(list(zip(population, fitness_scores)), 
                                   min(tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x[1])
        parents.append(winner[0])
    
    return parents

def crossover(parent1, parent2):
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
        idx1, idx2 = random.sample(range(1, len(route)), 2)
        route[idx1], route[idx2] = route[idx2], route[idx1]
    
    return route

def genetic_algorithm(graph, points, population_size=50, generations=100, 
                     mutation_rate=0.1, elite_size=5):
    if len(points) < 2:
        return {
            'route': points,
            'distance': 0
        }
    
    if len(points) == 2:
        # Nếu chỉ có 2 điểm, trả về trực tiếp khoảng cách giữa chúng
        try:
             # Direct matrix access
             dist = graph[points[0]][points[1]]
             return {
                'route': points + [points[0]], # Quay về đầu
                'distance': dist * 2
             }
        except:
             return {
                'route': points,
                'distance': 0
             }
    
    population = create_initial_population(points, population_size)
    
    best_route = None
    best_distance = float('inf')
    
    # Vòng lặp qua các thế hệ
    for generation in range(generations):
        fitness_scores = [fitness(graph, route) for route in population]
        
        best_idx = fitness_scores.index(max(fitness_scores))
        current_best = population[best_idx]
        current_distance = calculate_route_distance(graph, current_best)
        
        if current_distance < best_distance:
            best_route = current_best.copy()
            best_distance = current_distance
        
        new_population = []
        
        elite_indices = sorted(range(len(fitness_scores)), 
                               key=lambda i: fitness_scores[i], 
                               reverse=True)[:elite_size]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
        
        while len(new_population) < population_size:
            parents = selection(population, fitness_scores, 2)
            
            child1, child2 = crossover(parents[0], parents[1])
            
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)
        
        # 2-OPT Local Search (Memetic Algorithm)
        # Áp dụng 2-opt cho cá thể tốt nhất của thế hệ mới để tinh chỉnh
        if new_population:
            best_in_new_pop = new_population[0] 
            new_population[0] = two_opt(graph, best_in_new_pop)

        population = new_population[:population_size]
    
    final_route = best_route if best_route else points
    if final_route and final_route[0] == points[0]:
         final_route = list(final_route) 
         final_route.append(final_route[0])
         
    return {
        'route': final_route,
        'distance': best_distance
    }

def two_opt(graph, route):
    """
    Thuật toán tìm kiếm cục bộ 2-Opt để gỡ các nút thắt (un-crossing edges)
    """
    best_route = route
    # Giới hạn số lần thử để đảm bảo hiệu năng
    improved = True
    count = 0
    max_count = 50 
    
    while improved and count < max_count:
        improved = False
        count += 1
        
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if j - i == 1: continue
                
                new_route = route[:]
                new_route[i:j+1] = route[i:j+1][::-1] 
                
                dist_current = calculate_route_distance(graph, route)
                dist_new = calculate_route_distance(graph, new_route)
                
                if dist_new < dist_current:
                    route = new_route
                    improved = True
                    best_route = route
                    
    return best_route
