// Class Graph để quản lý đồ thị
class Graph {
  constructor() {
    // adjacencyList: object lưu danh sách kề
    // Format: { node: [{node: neighbor, weight: number}, ...] }
    this.adjacencyList = {};
  }

  // Thêm node vào đồ thị
  addNode(node) {
    if (!this.adjacencyList[node]) {
      this.adjacencyList[node] = [];
    }
  }

  // Thêm cạnh có hướng (directed edge)
  // node1 -> node2 với trọng số = weight
  addEdge(node1, node2, weight) {
    // Đảm bảo cả 2 node đều tồn tại
    if (!this.adjacencyList[node1]) {
      this.addNode(node1);
    }
    if (!this.adjacencyList[node2]) {
      this.addNode(node2);
    }

    // Thêm edge: node1 -> node2 với weight
    this.adjacencyList[node1].push({ node: node2, weight: weight });
  }

  // Thêm cạnh vô hướng (undirected edge)
  // node1 <-> node2 với trọng số = weight
  addUndirectedEdge(node1, node2, weight) {
    this.addEdge(node1, node2, weight);
    this.addEdge(node2, node1, weight);
  }

  // Lấy danh sách các node kề (neighbors) của một node
  getNeighbors(node) {
    return this.adjacencyList[node] || [];
  }

  // Kiểm tra node có tồn tại không
  hasNode(node) {
    return node in this.adjacencyList;
  }

  // Lấy tất cả các node trong đồ thị
  getAllNodes() {
    return Object.keys(this.adjacencyList);
  }

  // Xóa node khỏi đồ thị
  removeNode(node) {
    // Xóa node khỏi adjacency list
    delete this.adjacencyList[node];

    // Xóa tất cả các edge trỏ đến node này
    for (let key in this.adjacencyList) {
      this.adjacencyList[key] = this.adjacencyList[key].filter(
        (edge) => edge.node !== node
      );
    }
  }
}

export default Graph;

