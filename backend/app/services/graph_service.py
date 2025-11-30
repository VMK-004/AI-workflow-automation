"""Graph utilities for workflow execution"""
from typing import List, Dict, Set
from uuid import UUID
from collections import deque

from app.models.node import Node
from app.models.edge import Edge
from app.exceptions import (
    CycleError,
    NoStartNodeError,
    UnreachableNodeError,
    DisconnectedGraphError
)


class GraphService:
    """Service for graph operations on workflow nodes and edges"""
    
    @staticmethod
    def build_adjacency_list(nodes: List[Node], edges: List[Edge]) -> Dict[str, List[str]]:
        """
        Build adjacency list representation of the graph.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        
        Returns:
            Dict mapping node_id (str) to list of child node_ids (str)
        """
        # Initialize adjacency list with all nodes (even isolated ones)
        adj_list = {str(node.id): [] for node in nodes}
        
        # Add edges
        for edge in edges:
            source = str(edge.source_node_id)
            target = str(edge.target_node_id)
            
            if source in adj_list:
                adj_list[source].append(target)
        
        return adj_list
    
    @staticmethod
    def build_reverse_adjacency_list(nodes: List[Node], edges: List[Edge]) -> Dict[str, List[str]]:
        """
        Build reverse adjacency list (parent -> child becomes child -> parent).
        Used to find nodes with no incoming edges (start nodes).
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        
        Returns:
            Dict mapping node_id (str) to list of parent node_ids (str)
        """
        # Initialize reverse adjacency list with all nodes
        reverse_adj = {str(node.id): [] for node in nodes}
        
        # Add reverse edges (target -> source)
        for edge in edges:
            source = str(edge.source_node_id)
            target = str(edge.target_node_id)
            
            if target in reverse_adj:
                reverse_adj[target].append(source)
        
        return reverse_adj
    
    @staticmethod
    def find_start_nodes(reverse_adj: Dict[str, List[str]]) -> List[str]:
        """
        Find all start nodes (nodes with no incoming edges).
        
        Args:
            reverse_adj: Reverse adjacency list
        
        Returns:
            List of node_ids that are start nodes
        """
        start_nodes = []
        
        for node_id, parents in reverse_adj.items():
            if len(parents) == 0:
                start_nodes.append(node_id)
        
        return start_nodes
    
    @staticmethod
    def topological_sort(nodes: List[Node], edges: List[Edge]) -> List[str]:
        """
        Perform topological sort using Kahn's algorithm.
        Detects cycles and raises CycleError if found.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        
        Returns:
            List of node_ids in topological order
        
        Raises:
            CycleError: If a cycle is detected in the graph
            NoStartNodeError: If no start nodes are found
        """
        if not nodes:
            return []
        
        # Build adjacency list and calculate in-degrees
        adj_list = GraphService.build_adjacency_list(nodes, edges)
        reverse_adj = GraphService.build_reverse_adjacency_list(nodes, edges)
        
        # Calculate in-degree for each node
        in_degree = {node_id: len(parents) for node_id, parents in reverse_adj.items()}
        
        # Find start nodes (in-degree = 0)
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        
        if not queue:
            raise NoStartNodeError("No start nodes found in workflow. All nodes have incoming edges.")
        
        # Kahn's algorithm
        sorted_nodes = []
        
        while queue:
            # Remove node from queue
            current = queue.popleft()
            sorted_nodes.append(current)
            
            # For each child of current node
            for child in adj_list[current]:
                # Decrease in-degree
                in_degree[child] -= 1
                
                # If in-degree becomes 0, add to queue
                if in_degree[child] == 0:
                    queue.append(child)
        
        # Check if all nodes were processed
        if len(sorted_nodes) != len(nodes):
            # Cycle detected - not all nodes could be processed
            unprocessed = [node_id for node_id in in_degree.keys() if node_id not in sorted_nodes]
            raise CycleError(
                f"Cycle detected in workflow graph. "
                f"Could not process {len(unprocessed)} nodes: {unprocessed[:3]}..."
            )
        
        return sorted_nodes
    
    @staticmethod
    def detect_cycles(nodes: List[Node], edges: List[Edge]) -> bool:
        """
        Detect if the graph contains any cycles.
        Uses DFS with recursion stack.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        
        Returns:
            True if cycle exists, False otherwise
        """
        if not nodes:
            return False
        
        adj_list = GraphService.build_adjacency_list(nodes, edges)
        
        # Track visited nodes and recursion stack
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            """DFS helper function"""
            visited.add(node_id)
            rec_stack.add(node_id)
            
            # Visit all neighbors
            for neighbor in adj_list.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Back edge found - cycle detected
                    return True
            
            # Remove from recursion stack
            rec_stack.remove(node_id)
            return False
        
        # Check from each unvisited node
        for node_id in adj_list.keys():
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False
    
    @staticmethod
    def find_reachable_nodes(start_nodes: List[str], adj_list: Dict[str, List[str]]) -> Set[str]:
        """
        Find all nodes reachable from the given start nodes using BFS.
        
        Args:
            start_nodes: List of start node IDs
            adj_list: Adjacency list representation
        
        Returns:
            Set of reachable node IDs
        """
        reachable = set()
        queue = deque(start_nodes)
        
        while queue:
            current = queue.popleft()
            
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Add all children to queue
            for child in adj_list.get(current, []):
                if child not in reachable:
                    queue.append(child)
        
        return reachable
    
    @staticmethod
    def validate_graph(nodes: List[Node], edges: List[Edge], allow_disconnected: bool = False) -> Dict:
        """
        Perform complete graph validation.
        
        Checks:
        1. At least one start node exists
        2. No cycles in the graph
        3. All nodes are reachable from start nodes
        4. No disconnected components (unless allowed)
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
            allow_disconnected: Whether to allow disconnected components
        
        Returns:
            Dict with validation results:
            {
                "valid": bool,
                "start_nodes": List[str],
                "sorted_nodes": List[str],
                "reachable_nodes": Set[str],
                "unreachable_nodes": List[str]
            }
        
        Raises:
            NoStartNodeError: If no start nodes found
            CycleError: If cycle detected
            UnreachableNodeError: If nodes are unreachable
            DisconnectedGraphError: If disconnected components exist (when not allowed)
        """
        if not nodes:
            return {
                "valid": True,
                "start_nodes": [],
                "sorted_nodes": [],
                "reachable_nodes": set(),
                "unreachable_nodes": []
            }
        
        # Build graph representations
        adj_list = GraphService.build_adjacency_list(nodes, edges)
        reverse_adj = GraphService.build_reverse_adjacency_list(nodes, edges)
        
        # 1. Check for start nodes
        start_nodes = GraphService.find_start_nodes(reverse_adj)
        if not start_nodes:
            raise NoStartNodeError(
                "Workflow has no start nodes. All nodes have incoming edges, "
                "creating an invalid graph structure."
            )
        
        # 2. Check for cycles using topological sort
        try:
            sorted_nodes = GraphService.topological_sort(nodes, edges)
        except CycleError as e:
            raise e
        
        # 3. Check reachability
        reachable = GraphService.find_reachable_nodes(start_nodes, adj_list)
        all_node_ids = set(str(node.id) for node in nodes)
        unreachable = list(all_node_ids - reachable)
        
        if unreachable:
            if not allow_disconnected:
                raise UnreachableNodeError(
                    f"Found {len(unreachable)} unreachable node(s) in workflow. "
                    f"Unreachable nodes: {unreachable[:5]}..."
                )
        
        # 4. Check for disconnected components
        if not allow_disconnected and len(reachable) != len(nodes):
            raise DisconnectedGraphError(
                f"Workflow has disconnected components. "
                f"{len(nodes) - len(reachable)} nodes are not connected to the main graph."
            )
        
        return {
            "valid": True,
            "start_nodes": start_nodes,
            "sorted_nodes": sorted_nodes,
            "reachable_nodes": reachable,
            "unreachable_nodes": unreachable
        }
    
    @staticmethod
    def get_execution_order(nodes: List[Node], edges: List[Edge]) -> List[str]:
        """
        Get the execution order for nodes in the workflow.
        This is a convenience method that validates the graph and returns the sorted order.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        
        Returns:
            List of node_ids in execution order
        
        Raises:
            GraphValidationError: If graph validation fails
        """
        validation_result = GraphService.validate_graph(nodes, edges, allow_disconnected=False)
        return validation_result["sorted_nodes"]

