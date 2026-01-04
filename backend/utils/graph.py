"""
Class Graph để quản lý đồ thị
"""
from typing import Dict, List, Tuple, Optional


class Graph:
    def __init__(self):
        """
        Khởi tạo đồ thị
        adjacency_list: dict lưu danh sách kề
        Format: { node: [(neighbor, weight), ...] }
        """
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = {}

    def add_node(self, node: str) -> None:
        """Thêm node vào đồ thị"""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, node1: str, node2: str, weight: float) -> None:
        """
        Thêm cạnh có hướng (directed edge)
        node1 -> node2 với trọng số = weight
        """
        # Đảm bảo cả 2 node đều tồn tại
        if node1 not in self.adjacency_list:
            self.add_node(node1)
        if node2 not in self.adjacency_list:
            self.add_node(node2)

        # Thêm edge: node1 -> node2 với weight
        self.adjacency_list[node1].append((node2, weight))

    def add_undirected_edge(self, node1: str, node2: str, weight: float) -> None:
        """
        Thêm cạnh vô hướng (undirected edge)
        node1 <-> node2 với trọng số = weight
        """
        self.add_edge(node1, node2, weight)
        self.add_edge(node2, node1, weight)

    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Lấy danh sách các node kề (neighbors) của một node"""
        return self.adjacency_list.get(node, [])

    def has_node(self, node: str) -> bool:
        """Kiểm tra node có tồn tại không"""
        return node in self.adjacency_list

    def get_all_nodes(self) -> List[str]:
        """Lấy tất cả các node trong đồ thị"""
        return list(self.adjacency_list.keys())

    def remove_node(self, node: str) -> None:
        """Xóa node khỏi đồ thị"""
        # Xóa node khỏi adjacency list
        if node in self.adjacency_list:
            del self.adjacency_list[node]

        # Xóa tất cả các edge trỏ đến node này
        for key in self.adjacency_list:
            self.adjacency_list[key] = [
                (neighbor, weight)
                for neighbor, weight in self.adjacency_list[key]
                if neighbor != node
            ]

