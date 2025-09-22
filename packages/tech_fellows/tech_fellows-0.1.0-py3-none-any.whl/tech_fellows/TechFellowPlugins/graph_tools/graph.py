"""Graph implementation."""

from collections import deque

from .node import Node


class Graph:
    """Defines a graph."""

    def __init__(self, directed: bool = False) -> None:
        """Initializes a graph.

        Parameters:
            directed (bool): Denotes of the graph is directed or not.

        Returns:
            None.
        """
        self.graph = {}
        self.directed = directed

    def add_node(self, node: Node) -> None:
        """Add the given node to the graph.

        Parameters:
            node: Node to be added.

        Returns:
            None.
        """
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, node1: Node, node2: Node):
        """Create an edge between given nodes.

        Parameters:
            node1 (Node): First node.
            node2 (Node): Second node.

        Returns:
            None.
        """
        if node1 not in self.graph:
            self.add_node(node1)

        if node2 not in self.graph:
            self.add_node(node2)

        self.graph[node1].append(node2)

        if not self.directed:
            self.graph[node2].append(node1)

    def display(self) -> None:
        """Display the graph.

        Returns:
            None.
        """
        for node, neighbors in self.graph.items():
            print(f"{node.node} -> {[x.node for x in neighbors]}")

    def find_shortest_path(self, start_node: Node, end_node: Node) -> None:
        """To find shortest path from one node to another node.

        Parameters:
            start_node (Node): Start node.
            end_node (Node): End node.

        Returns:
            None.
        """
        queue = deque([(start_node, [start_node])])
        visited = set()

        while queue:
            current_node, path = queue.popleft()
            if current_node == end_node:
                print("-> ".join([node.node for node in path]))
                return

            if current_node not in visited:
                visited.add(current_node)
                for neighbor in self.graph.get(current_node, []):
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
        print("No path found!!")

    def bfs(self, start_node: Node) -> None:
        """Breadth first search of graph.

        Parameters:
            start_node (Node): Node from which the search starts.

        Returns:
            None.
        """
        visited = set()
        queue = [start_node]
        result = []

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                result.append(node)
                queue.extend(neighbor for neighbor in self.graph[node] if neighbor not in visited)

        print("-> ".join([node.node for node in result]))

    def __perform_dfs(self, start_node: Node, visited=None):
        """Performs depth first search of graph.

        Parameters:
            start_node (Node): Node from which the search starts.
            visited (set): Set of nodes visited.

        Returns:
            None.
        """
        if visited is None:
            visited = set()
        visited.add(start_node)
        result = [start_node]

        for neighbor in self.graph[start_node]:
            if neighbor not in visited:
                result.extend(self.__perform_dfs(neighbor, visited))

        return result

    def dfs(self, start_node: Node):
        """Get dfs of the graph from start_node.

        Parameters:
            start_node (Node): Starting node.
        """
        result_path = self.__perform_dfs(start_node=start_node)

        print("-> ".join([node.node for node in result_path]))
