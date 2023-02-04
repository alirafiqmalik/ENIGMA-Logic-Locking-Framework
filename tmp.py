import networkx as nx

G1 = nx.DiGraph()
G1.add_node(1)
G1.add_node(2)
G1.add_edge(1, 2)

G2 = nx.DiGraph()
G2.add_node(3)
G2.add_node(2)
G2.add_edge(2, 3)

G_merged = nx.DiGraph()
G_merged.add_nodes_from(G1)
G_merged.add_nodes_from(G2)
G_merged.add_edges_from(G1.edges())
G_merged.add_edges_from(G2.edges())

# Add edge connecting common node
G_merged.add_edge(1, 3)

print(G1)
print(G2)
print(G_merged)