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
