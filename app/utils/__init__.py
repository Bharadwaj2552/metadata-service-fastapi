"""Graph utilities for lineage validation and cycle detection"""

from typing import Dict, Set, List, Optional


def has_cycle(graph: Dict[int, List[int]], start_node: int, target_node: int) -> bool:
    """
    Detect if adding an edge from start_node to target_node would create a cycle.

    Uses Depth-First Search (DFS) algorithm to check if target_node can reach start_node,
    which would create a cycle if we add an edge from start_node to target_node.

    Args:
        graph: Adjacency list representation of the lineage graph
        start_node: The source dataset ID
        target_node: The destination dataset ID

    Returns:
        True if a cycle would be created, False otherwise
    """
    visited: Set[int] = set()

    def dfs(node: int) -> bool:
        """Recursive DFS to find if target can be reached from node"""
        if node == target_node:
            return True

        if node in visited:
            return False

        visited.add(node)

        # Check all downstream datasets
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True

        return False

    # Start DFS from start_node to see if we can reach target_node
    return dfs(start_node)


def get_upstream_datasets(graph: Dict[int, List[int]], dataset_id: int) -> Set[int]:
    """
    Get all upstream datasets for a given dataset.

    Args:
        graph: Adjacency list representation of the lineage graph
        dataset_id: The dataset ID to find upstream for

    Returns:
        Set of upstream dataset IDs
    """
    upstream: Set[int] = set()

    def dfs(node: int) -> None:
        """Recursive DFS to find all upstream nodes"""
        for upstream_id in graph.get(node, []):
            if upstream_id not in upstream:
                upstream.add(upstream_id)
                dfs(upstream_id)

    dfs(dataset_id)
    return upstream


def get_downstream_datasets(
    reverse_graph: Dict[int, List[int]], dataset_id: int
) -> Set[int]:
    """
    Get all downstream datasets for a given dataset.

    Args:
        reverse_graph: Reverse adjacency list representation of the lineage graph
        dataset_id: The dataset ID to find downstream for

    Returns:
        Set of downstream dataset IDs
    """
    downstream: Set[int] = set()

    def dfs(node: int) -> None:
        """Recursive DFS to find all downstream nodes"""
        for downstream_id in reverse_graph.get(node, []):
            if downstream_id not in downstream:
                downstream.add(downstream_id)
                dfs(downstream_id)

    dfs(dataset_id)
    return downstream


def build_lineage_graphs(lineages: List[tuple]) -> tuple:
    """
    Build forward and reverse adjacency lists from lineage relationships.

    Args:
        lineages: List of (upstream_dataset_id, downstream_dataset_id) tuples

    Returns:
        Tuple of (forward_graph, reverse_graph) as adjacency lists
    """
    forward_graph: Dict[int, List[int]] = {}
    reverse_graph: Dict[int, List[int]] = {}

    for upstream_id, downstream_id in lineages:
        if upstream_id not in forward_graph:
            forward_graph[upstream_id] = []
        forward_graph[upstream_id].append(downstream_id)

        if downstream_id not in reverse_graph:
            reverse_graph[downstream_id] = []
        reverse_graph[downstream_id].append(upstream_id)

    return forward_graph, reverse_graph


def validate_lineage_dag(lineages: List[tuple]) -> bool:
    """
    Validate that lineage relationships form a valid DAG (Directed Acyclic Graph).

    Args:
        lineages: List of (upstream_dataset_id, downstream_dataset_id) tuples

    Returns:
        True if valid DAG, False if cycle exists
    """
    graph, _ = build_lineage_graphs(lineages)

    # For each edge, check if adding it would create a cycle
    for upstream_id, downstream_id in lineages:
        # Remove current edge and check if cycle exists
        graph_without_edge = graph.copy()
        if upstream_id in graph_without_edge:
            graph_without_edge[upstream_id] = [
                d for d in graph_without_edge[upstream_id] if d != downstream_id
            ]

        # Check if downstream can reach upstream (which would create a cycle)
        if has_cycle(graph_without_edge, downstream_id, upstream_id):
            return False

    return True
