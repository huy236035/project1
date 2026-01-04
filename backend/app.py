"""
Flask API server cho ứng dụng tìm đường ngắn nhất
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.graph import Graph
from algorithms.dijkstra import dijkstra, create_sample_graph

app = Flask(__name__)
CORS(app)  # Cho phép frontend gọi API

# Tạo graph mẫu (có thể thay bằng database sau)
sample_graph = create_sample_graph()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server đang chạy'})


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Lấy danh sách tất cả các nodes trong đồ thị"""
    nodes = sample_graph.get_all_nodes()
    return jsonify({'nodes': nodes})


@app.route('/api/path', methods=['POST'])
def find_path():
    """
    Tìm đường đi ngắn nhất giữa 2 nodes
    
    Request body:
        {
            "start": "A",
            "end": "F"
        }
    
    Response:
        {
            "path": ["A", "C", "B", "D", "F"],
            "distance": 12.0,
            "visited_nodes": ["A", "C", "B", "D", "F"]
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body không được để trống'}), 400
        
        start_node = data.get('start')
        end_node = data.get('end')
        
        if not start_node or not end_node:
            return jsonify({'error': 'start và end là bắt buộc'}), 400
        
        # Chạy thuật toán Dijkstra
        result = dijkstra(sample_graph, start_node, end_node)
        
        # Xử lý distance nếu là infinity
        if result['distance'] == float('inf'):
            return jsonify({
                'error': result.get('message', 'Không tìm thấy đường đi'),
                'path': [],
                'distance': None,
                'visited_nodes': result['visited_nodes']
            }), 404
        
        return jsonify({
            'path': result['path'],
            'distance': result['distance'],
            'visited_nodes': result['visited_nodes']
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Lấy toàn bộ đồ thị (để visualize)"""
    graph_data = {}
    nodes = sample_graph.get_all_nodes()
    
    for node in nodes:
        neighbors = sample_graph.get_neighbors(node)
        graph_data[node] = [
            {'node': neighbor, 'weight': weight}
            for neighbor, weight in neighbors
        ]
    
    return jsonify({'graph': graph_data})


@app.route('/api/graph', methods=['POST'])
def create_graph():
    """
    Tạo đồ thị mới từ dữ liệu
    
    Request body:
        {
            "edges": [
                {"from": "A", "to": "B", "weight": 4},
                {"from": "A", "to": "C", "weight": 2},
                ...
            ]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'edges' not in data:
            return jsonify({'error': 'edges là bắt buộc'}), 400
        
        global sample_graph
        sample_graph = Graph()
        
        edges = data['edges']
        for edge in edges:
            from_node = edge.get('from')
            to_node = edge.get('to')
            weight = edge.get('weight')
            
            if not all([from_node, to_node, weight is not None]):
                return jsonify({'error': 'Mỗi edge phải có from, to, và weight'}), 400
            
            sample_graph.add_edge(from_node, to_node, float(weight))
        
        return jsonify({'message': 'Đồ thị đã được tạo thành công'})
    
    except Exception as e:
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

