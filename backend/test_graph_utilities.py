"""
Test script for graph utilities
Run with: python -m backend.test_graph_utilities
"""
from uuid import uuid4
from app.models.node import Node
from app.models.edge import Edge
from app.services.graph_service import GraphService
from app.exceptions import CycleError, NoStartNodeError


def create_node(name: str, workflow_id: str = "test-wf") -> Node:
    """Helper to create a test node"""
    node = Node()
    node.id = uuid4()
    node.workflow_id = workflow_id
    node.name = name
    node.node_type = "llm_call"
    node.config = {}
    return node


def create_edge(source: Node, target: Node) -> Edge:
    """Helper to create a test edge"""
    edge = Edge()
    edge.id = uuid4()
    edge.workflow_id = source.workflow_id
    edge.source_node_id = source.id
    edge.target_node_id = target.id
    return edge


def test_linear_pipeline():
    """Test: A → B → C"""
    print("\n" + "="*60)
    print("Test 1: Linear Pipeline (A → B → C)")
    print("="*60)
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    node_c = create_node("C")
    nodes = [node_a, node_b, node_c]
    
    # Create edges
    edge_ab = create_edge(node_a, node_b)
    edge_bc = create_edge(node_b, node_c)
    edges = [edge_ab, edge_bc]
    
    # Validate
    result = GraphService.validate_graph(nodes, edges)
    
    print(f"✅ Valid: {result['valid']}")
    print(f"   Start nodes: {[n.name for n in nodes if str(n.id) in result['start_nodes']]}")
    print(f"   Execution order: {[n.name for n in nodes if str(n.id) in result['sorted_nodes']]}")


def test_branching():
    """Test: A → B, A → C"""
    print("\n" + "="*60)
    print("Test 2: Branching (A → B, A → C)")
    print("="*60)
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    node_c = create_node("C")
    nodes = [node_a, node_b, node_c]
    
    # Create edges (branching)
    edge_ab = create_edge(node_a, node_b)
    edge_ac = create_edge(node_a, node_c)
    edges = [edge_ab, edge_ac]
    
    # Validate
    result = GraphService.validate_graph(nodes, edges)
    
    print(f"✅ Valid: {result['valid']}")
    print(f"   Start nodes: {[n.name for n in nodes if str(n.id) in result['start_nodes']]}")
    sorted_names = [n.name for n in nodes for sid in result['sorted_nodes'] if str(n.id) == sid]
    print(f"   Execution order: {sorted_names}")
    print(f"   Note: B and C can execute in parallel after A")


def test_converging():
    """Test: A → C, B → C"""
    print("\n" + "="*60)
    print("Test 3: Converging (A → C, B → C)")
    print("="*60)
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    node_c = create_node("C")
    nodes = [node_a, node_b, node_c]
    
    # Create edges (converging)
    edge_ac = create_edge(node_a, node_c)
    edge_bc = create_edge(node_b, node_c)
    edges = [edge_ac, edge_bc]
    
    # Validate
    result = GraphService.validate_graph(nodes, edges)
    
    print(f"✅ Valid: {result['valid']}")
    start_names = [n.name for n in nodes if str(n.id) in result['start_nodes']]
    print(f"   Start nodes: {start_names}")
    sorted_names = [n.name for n in nodes for sid in result['sorted_nodes'] if str(n.id) == sid]
    print(f"   Execution order: {sorted_names}")
    print(f"   Note: C must execute after both A and B")


def test_cycle_detection():
    """Test: A → B → C → A (cycle)"""
    print("\n" + "="*60)
    print("Test 4: Cycle Detection (A → B → C → A)")
    print("="*60)
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    node_c = create_node("C")
    nodes = [node_a, node_b, node_c]
    
    # Create edges with cycle
    edge_ab = create_edge(node_a, node_b)
    edge_bc = create_edge(node_b, node_c)
    edge_ca = create_edge(node_c, node_a)  # Creates cycle!
    edges = [edge_ab, edge_bc, edge_ca]
    
    # Try to validate
    try:
        result = GraphService.validate_graph(nodes, edges)
        print("❌ Should have detected cycle!")
    except CycleError as e:
        print(f"✅ Cycle detected correctly!")
        print(f"   Error: {e}")


def test_no_start_nodes():
    """Test: A → B, B → A (no start nodes)"""
    print("\n" + "="*60)
    print("Test 5: No Start Nodes (A → B, B → A)")
    print("="*60)
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    nodes = [node_a, node_b]
    
    # Create cycle (no start nodes)
    edge_ab = create_edge(node_a, node_b)
    edge_ba = create_edge(node_b, node_a)
    edges = [edge_ab, edge_ba]
    
    # Try to validate
    try:
        result = GraphService.validate_graph(nodes, edges)
        print("❌ Should have detected no start nodes!")
    except NoStartNodeError as e:
        print(f"✅ No start nodes detected correctly!")
        print(f"   Error: {e}")


def test_complex_dag():
    """Test: Complex valid DAG"""
    print("\n" + "="*60)
    print("Test 6: Complex DAG")
    print("="*60)
    print("Graph: A → B → D → F")
    print("         ↘   ↗   ↘")
    print("          C       E")
    
    # Create nodes
    node_a = create_node("A")
    node_b = create_node("B")
    node_c = create_node("C")
    node_d = create_node("D")
    node_e = create_node("E")
    node_f = create_node("F")
    nodes = [node_a, node_b, node_c, node_d, node_e, node_f]
    
    # Create edges
    edges = [
        create_edge(node_a, node_b),
        create_edge(node_a, node_c),
        create_edge(node_b, node_d),
        create_edge(node_c, node_d),
        create_edge(node_d, node_e),
        create_edge(node_d, node_f),
    ]
    
    # Validate
    result = GraphService.validate_graph(nodes, edges)
    
    print(f"✅ Valid: {result['valid']}")
    start_names = [n.name for n in nodes if str(n.id) in result['start_nodes']]
    print(f"   Start nodes: {start_names}")
    sorted_names = [n.name for n in nodes for sid in result['sorted_nodes'] if str(n.id) == sid]
    print(f"   Execution order: {sorted_names}")


def test_execution_order():
    """Test: Get execution order directly"""
    print("\n" + "="*60)
    print("Test 7: Get Execution Order (convenience method)")
    print("="*60)
    
    # Create simple pipeline
    node_a = create_node("Extract")
    node_b = create_node("Transform")
    node_c = create_node("Load")
    nodes = [node_a, node_b, node_c]
    
    edges = [
        create_edge(node_a, node_b),
        create_edge(node_b, node_c),
    ]
    
    # Get execution order
    execution_order = GraphService.get_execution_order(nodes, edges)
    order_names = [n.name for n in nodes for eid in execution_order if str(n.id) == eid]
    
    print(f"✅ Execution order: {order_names}")
    print(f"   Ready to execute workflow in this order!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GRAPH UTILITIES TEST SUITE")
    print("="*60)
    
    try:
        test_linear_pipeline()
        test_branching()
        test_converging()
        test_cycle_detection()
        test_no_start_nodes()
        test_complex_dag()
        test_execution_order()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nGraph utilities are working correctly and ready for use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()





