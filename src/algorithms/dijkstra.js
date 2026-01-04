import Graph from '../utils/Graph';

/**
 * Thuật toán Dijkstra tìm đường đi ngắn nhất
 * @param {Graph} graph - Đồ thị cần tìm đường
 * @param {string} startNode - Node bắt đầu
 * @param {string} endNode - Node kết thúc
 * @returns {Object} {path: Array, distance: number, visitedNodes: Array}
 *   - path: mảng các node từ start đến end (ngắn nhất)
 *   - distance: khoảng cách ngắn nhất
 *   - visitedNodes: mảng các node đã được duyệt (để visualize)
 */
export function dijkstra(graph, startNode, endNode) {
  // Kiểm tra input
  if (!graph.hasNode(startNode) || !graph.hasNode(endNode)) {
    throw new Error('Start node hoặc end node không tồn tại trong đồ thị');
  }

  // Nếu start = end
  if (startNode === endNode) {
    return {
      path: [startNode],
      distance: 0,
      visitedNodes: [startNode],
    };
  }

  // Khởi tạo
  const distances = {}; // Lưu khoảng cách ngắn nhất đến mỗi node
  const previous = {}; // Lưu node trước đó trong đường đi ngắn nhất
  const visited = new Set(); // Set các node đã được xét
  const unvisited = new Set(); // Set các node chưa được xét
  const visitedOrder = []; // Thứ tự các node đã visit (để visualize)

  // Khởi tạo distances: startNode = 0, các node khác = Infinity
  const allNodes = graph.getAllNodes();
  allNodes.forEach((node) => {
    distances[node] = node === startNode ? 0 : Infinity;
    previous[node] = null;
    unvisited.add(node);
  });

  // Vòng lặp chính của thuật toán Dijkstra
  while (unvisited.size > 0) {
    // Bước 1: Chọn node chưa visit có distance nhỏ nhất
    let currentNode = null;
    let minDistance = Infinity;

    unvisited.forEach((node) => {
      if (distances[node] < minDistance) {
        minDistance = distances[node];
        currentNode = node;
      }
    });

    // Nếu không tìm thấy node nào (không có đường đi)
    if (currentNode === null || minDistance === Infinity) {
      break;
    }

    // Đánh dấu currentNode đã được visit
    unvisited.delete(currentNode);
    visited.add(currentNode);
    visitedOrder.push(currentNode);

    // Nếu đã đến endNode, có thể dừng sớm (tùy chọn)
    if (currentNode === endNode) {
      break;
    }

    // Bước 2: Xét tất cả các neighbor của currentNode
    const neighbors = graph.getNeighbors(currentNode);
    neighbors.forEach(({ node: neighbor, weight }) => {
      // Bỏ qua nếu neighbor đã được visit
      if (visited.has(neighbor)) {
        return;
      }

      // Tính khoảng cách mới qua currentNode
      const newDistance = distances[currentNode] + weight;

      // Nếu tìm thấy đường đi ngắn hơn
      if (newDistance < distances[neighbor]) {
        distances[neighbor] = newDistance;
        previous[neighbor] = currentNode;
      }
    });
  }

  // Bước 3: Tái tạo đường đi từ endNode ngược về startNode
  const path = [];
  let current = endNode;

  // Trace ngược lại từ endNode về startNode
  while (current !== null) {
    path.unshift(current); // Thêm vào đầu mảng
    current = previous[current];
  }

  // Kiểm tra có tìm thấy đường đi không
  if (path[0] !== startNode) {
    return {
      path: [],
      distance: Infinity,
      visitedNodes: visitedOrder,
      message: 'Không tìm thấy đường đi',
    };
  }

  return {
    path: path,
    distance: distances[endNode],
    visitedNodes: visitedOrder,
  };
}

/**
 * Hàm helper để tạo graph mẫu (để test)
 */
export function createSampleGraph() {
  const graph = new Graph();

  // Thêm các node
  graph.addNode('A');
  graph.addNode('B');
  graph.addNode('C');
  graph.addNode('D');
  graph.addNode('E');
  graph.addNode('F');

  // Thêm các edge (ví dụ: đồ thị có hướng)
  graph.addEdge('A', 'B', 4);
  graph.addEdge('A', 'C', 2);
  graph.addEdge('B', 'C', 1);
  graph.addEdge('B', 'D', 5);
  graph.addEdge('C', 'D', 8);
  graph.addEdge('C', 'E', 10);
  graph.addEdge('D', 'E', 2);
  graph.addEdge('D', 'F', 6);
  graph.addEdge('E', 'F', 2);

  return graph;
}

