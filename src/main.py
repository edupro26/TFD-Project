from node import Node

def main():
    n_nodes = 5
    nodes = []
    base_port = 8000

    for i in range(n_nodes):
        node = Node(id=i, port=base_port + i)
        node.start()
        nodes.append(node)

if __name__ == '__main__':
    main()
