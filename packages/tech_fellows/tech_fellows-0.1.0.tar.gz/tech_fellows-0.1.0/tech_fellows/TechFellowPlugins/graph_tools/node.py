"""Node implementation for graph."""


class Node:
    """Defines a node."""

    def __init__(self, node_value: str):
        """Initializes a node.

        Parameters:
            node_value (str): Node value.

        Returns:
            None.
        """
        self.node = node_value
