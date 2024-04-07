import networkx as nx

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges to the graph
G.add_edge('Start Node', 'MessageNode1')
G.add_edge('MessageNode1', 'ConditionNode1')
G.add_edge('ConditionNode1', 'MessageNode2', condition='Yes')
G.add_edge('ConditionNode1', 'ConditionNode2', condition='No')
G.add_edge('MessageNode2', 'End Node')
G.add_edge('ConditionNode2', 'MessageNode3', condition='Yes')
G.add_edge('ConditionNode2', 'MessageNode4', condition='No')
G.add_edge('MessageNode3', 'End Node')
G.add_edge('MessageNode4', 'End Node')

# Find all simple paths from the start node to the end node
paths = list(nx.all_simple_paths(G, source='Start Node', target='End Node'))
print(paths)


