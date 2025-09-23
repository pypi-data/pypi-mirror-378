from graphs_AustynGriegoMSU import sp
import sys

def read_graph_file(filename):
    """Read graph from file and return properly formatted graph"""
    graph = {}
    nodes = set()
    
    with open(filename, 'rt') as f:
        num_nodes = int(f.readline().strip())  # Read number of nodes
        
        # Initialize all nodes
        for i in range(num_nodes):
            graph[i] = {}
            nodes.add(i)
        
        # Read edges
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                s, d, w = line.split()
                s = int(s)
                d = int(d)
                w = int(w)
                graph[s][d] = w
                nodes.add(s)
                nodes.add(d)
    
    return graph, nodes

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} graph_file')
        print('Graph file format:')
        print('  First line: number of nodes')
        print('  Following lines: source destination weight')
        sys.exit(1)

    try:
        graph, nodes = read_graph_file(sys.argv[1])
        print(f"Loaded graph with {len(nodes)} nodes")
        print(f"Graph structure: {graph}")
        
        source = 0
        if source not in nodes:
            print(f"Error: Source node {source} not found in graph")
            print(f"Available nodes: {sorted(nodes)}")
            sys.exit(1)
        
        dist, path = sp.dijkstra(graph, source)
        print(f'\nShortest distances from node {source}:')
        print(dist)
        print('\nShortest paths:')
        for d in path: 
            print(f'Path to node {d}: {path[d]}')
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{sys.argv[1]}'")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid file format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)