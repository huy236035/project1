import itertools

def held_karp(matrix):
    n = len(matrix)
    
    C = {}

    for k in range(1, n):
        mask = (1 << k) | 1 
        C[(mask, k)] = (matrix[0][k], 0)

    for s in range(3, n + 1):
        for subset in itertools.combinations(range(1, n), s - 1):
            mask = 1
            for bit in subset:
                mask |= (1 << bit)
            
            for k in subset:
                prev_mask = mask & ~(1 << k)
                
                min_dist = float('inf')
                parent = -1
                
                for m in subset:
                    if m == k: continue
                    
                    if (prev_mask, m) in C:
                        dist = C[(prev_mask, m)][0] + matrix[m][k]
                        if dist < min_dist:
                            min_dist = dist
                            parent = m
                
                if parent != -1:
                    C[(mask, k)] = (min_dist, parent)

    full_mask = (1 << n) - 1
    min_tour_dist = float('inf')
    last_node = -1
    
    for k in range(1, n):
        if (full_mask, k) in C:
            dist = C[(full_mask, k)][0] + matrix[k][0]
            if dist < min_tour_dist:
                min_tour_dist = dist
                last_node = k
                
    if last_node == -1:
        return {'route': list(range(n)), 'distance': 0}
        
    path = []
    curr_mask = full_mask
    curr_node = last_node
    
    while curr_node != 0:
        path.append(curr_node)
        _, prev_node = C[(curr_mask, curr_node)]
        curr_mask = curr_mask & ~(1 << curr_node)
        curr_node = prev_node
        
    path.append(0)
    path.reverse()
    path.append(0)
    
    return {
        'route': path,
        'distance': min_tour_dist
    }
