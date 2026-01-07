from flask import Flask, request, jsonify
from algorithms.astar import astar
from utils.graph import Graph
from utils.path_converter import nodes_to_coordinates

app = Flask(__name__)

# load graph (tạm hardcode, sau nâng cấp)
graph = Graph()
graph.load_sample_data()   # hoặc load từ OSM sau

@app.route("/route", methods=["GET"])
def find_route():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"error": "missing start or end"}), 400

    result = astar(graph, start, end)
    coords = nodes_to_coordinates(result["path"])

    return jsonify({
        "distance": result["distance"],
        "path": coords
    })

if __name__ == "__main__":
    app.run(debug=True)
