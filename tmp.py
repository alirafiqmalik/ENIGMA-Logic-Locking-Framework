import networkx as nx
import json
import pickle
import base64

G = nx.DiGraph()
# Add node with attributes
G.add_node(1, mode='red', type='circle')
G.add_node(2, mode='green', type='square')
G.add_edge(1, 2)



G1 = nx.DiGraph()
# Add node with attributes
G1.add_node(4, mode='red', type='circle')
G1.add_node(2, mode='green', type='square',init="init")
G1.add_node(3, mode='blue', type='triangle')
G1.add_edge(4, 2)
G1.add_edge(3, 2)



G_merged = nx.DiGraph()

# Add nodes and their attributes from G and G1 to G_merged
for node, attrs in G.nodes(data=True):
    G_merged.add_node(node, **attrs)

for node, attrs in G1.nodes(data=True):
    G_merged.add_node(node, **attrs)



G_merged.add_edges_from(G1.edges())
G_merged.add_edges_from(G.edges())

# Access node attributes
print(G_merged.nodes[1]) # Output: {'mode': 'red', 'type': 'circle'}
print(G_merged.nodes[2]) # Output: {'mode': 'green', 'type': 'square'}






# Encode the graph object to a binary string using pickle
binary_data = pickle.dumps(G_merged)

# Encode the binary string to a base64 string
base64_data = base64.b64encode(binary_data).decode('utf-8')

# Store the base64 encoded data in a JSON object
data = {'DiGraph': base64_data}

# Write the JSON object to a file
with open('./tmp/graph.json', 'w') as f:
    json.dump(data, f)

# Load the JSON object from the file
with open('./tmp/graph.json', 'r') as f:
    data = json.load(f)

# Decode the base64 string back to binary
binary_data = base64.b64decode(data['DiGraph'].encode('utf-8'))

# Decode the binary string back to a graph object
G2 = pickle.loads(binary_data)

# Check if the graph has been successfully decoded
assert nx.is_isomorphic(G_merged, G2)