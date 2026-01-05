class Graph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = {}

    def add_edge(self, u, v, weight):
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = weight

    def get_all_nodes(self):
        return self.adj.keys()

    def get_neighbors(self, node):
        return self.adj[node].items()

    
    def load_sample_data(self):
        self.add_edge("A", "B", 2)
        self.add_edge("A", "C", 5)
        self.add_edge("B", "C", 1)
        self.add_edge("B", "D", 4)
        self.add_edge("C", "D", 2)
