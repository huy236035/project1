""" đổi danh sách các node thành tọa độ GPS
    path: ['A', 'B', 'C']
    return: [{'lat': ..., 'lng': ...}, ...]
"""

from data.nodes import NODES

def nodes_to_coordinates(path):
    
    coords = []

    for node in path:
        if node not in NODES:
            raise ValueError(f"Node {node} không có tọa độ")

        coords.append({
            "lat": NODES[node]["lat"],
            "lng": NODES[node]["lng"]
        })

    return coords
