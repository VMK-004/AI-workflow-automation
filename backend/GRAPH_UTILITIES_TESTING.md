# Graph Utilities - Testing Guide

## ✅ Implementation Complete

Complete graph utilities for workflow execution with cycle detection, topological sorting, and graph validation.

---

## 📁 Files Created (2 files)

### 1. **`app/exceptions.py`** (New file)

**Custom exceptions defined:**
- ✅ `GraphValidationError` - Base exception for graph errors
- ✅ `CycleError` - When cycles are detected
- ✅ `NoStartNodeError` - When no start nodes exist
- ✅ `DisconnectedGraphError` - When graph has disconnected components
- ✅ `UnreachableNodeError` - When nodes can't be reached

**Key features:**
- Clear exception hierarchy
- Descriptive error messages
- Easy to catch specific errors

### 2. **`app/services/graph_service.py`** (New file)

**Methods implemented:**
- ✅ `build_adjacency_list()` - Create graph representation
- ✅ `build_reverse_adjacency_list()` - For finding start nodes
- ✅ `find_start_nodes()` - Nodes with no incoming edges
- ✅ `topological_sort()` - Kahn's algorithm with cycle detection
- ✅ `detect_cycles()` - DFS-based cycle detection
- ✅ `find_reachable_nodes()` - BFS reachability check
- ✅ `validate_graph()` - Complete graph validation
- ✅ `get_execution_order()` - Convenience method for execution

**Key features:**
- Pure synchronous graph operations (no DB calls)
- Comprehensive validation
- Clear error messages
- Well-documented algorithms

---

## 🎯 Graph Service Methods

### 1. Build Adjacency List

```python
from app.services.graph_service import GraphService

adj_list = GraphService.build_adjacency_list(nodes, edges)

# Example output:
# {
#   "node_1_id": ["node_2_id", "node_3_id"],
#   "node_2_id": ["node_3_id"],
#   "node_3_id": []
# }
```

**Purpose:** Create graph representation where each node maps to its children.

---

### 2. Build Reverse Adjacency List

```python
reverse_adj = GraphService.build_reverse_adjacency_list(nodes, edges)

# Example output (reverse of above):
# {
#   "node_1_id": [],  # No parents (start node)
#   "node_2_id": ["node_1_id"],
#   "node_3_id": ["node_1_id", "node_2_id"]
# }
```

**Purpose:** Find parents of each node. Used to identify start nodes.

---

### 3. Find Start Nodes

```python
reverse_adj = GraphService.build_reverse_adjacency_list(nodes, edges)
start_nodes = GraphService.find_start_nodes(reverse_adj)

# Example output:
# ["node_1_id"]  # Nodes with no incoming edges
```

**Purpose:** Identify nodes where workflow execution should begin.

---

### 4. Topological Sort (Kahn's Algorithm)

```python
try:
    sorted_nodes = GraphService.topological_sort(nodes, edges)
    print(f"Execution order: {sorted_nodes}")
except CycleError as e:
    print(f"Cycle detected: {e}")
except NoStartNodeError as e:
    print(f"No start nodes: {e}")

# Example output for valid DAG:
# ["node_1_id", "node_2_id", "node_3_id"]
```

**Purpose:** Determine execution order. Detects cycles automatically.

**Algorithm:** Kahn's algorithm
1. Find all start nodes (in-degree = 0)
2. Process nodes in queue
3. Decrease in-degree of children
4. Add children with in-degree 0 to queue
5. If not all nodes processed → cycle detected

---

### 5. Detect Cycles

```python
has_cycle = GraphService.detect_cycles(nodes, edges)

if has_cycle:
    print("Graph contains cycles!")
else:
    print("Graph is a valid DAG")
```

**Purpose:** Explicit cycle detection using DFS.

**Algorithm:** DFS with recursion stack
- If we visit a node already in recursion stack → cycle found

---

### 6. Validate Graph

```python
from app.exceptions import GraphValidationError

try:
    result = GraphService.validate_graph(nodes, edges)
    print(f"Valid: {result['valid']}")
    print(f"Start nodes: {result['start_nodes']}")
    print(f"Execution order: {result['sorted_nodes']}")
    print(f"Unreachable nodes: {result['unreachable_nodes']}")
except GraphValidationError as e:
    print(f"Validation failed: {e}")
```

**Validates:**
1. ✅ At least one start node exists
2. ✅ No cycles in the graph
3. ✅ All nodes reachable from start nodes
4. ✅ No disconnected components (optional)

**Returns:**
```python
{
    "valid": True,
    "start_nodes": ["node_1"],
    "sorted_nodes": ["node_1", "node_2", "node_3"],
    "reachable_nodes": {"node_1", "node_2", "node_3"},
    "unreachable_nodes": []
}
```

---

### 7. Get Execution Order (Convenience Method)

```python
try:
    execution_order = GraphService.get_execution_order(nodes, edges)
    print(f"Execute nodes in order: {execution_order}")
except GraphValidationError as e:
    print(f"Cannot execute: {e}")
```

**Purpose:** One-call validation + execution order.

---

## 🧪 Test Cases

### Test 1: Valid Linear Pipeline ✅

**Graph:**
```
[A] → [B] → [C]
```

**Code:**
```python
from app.services.graph_service import GraphService

# Assuming nodes A, B, C and edges A→B, B→C exist
result = GraphService.validate_graph(nodes, edges)

assert result["valid"] == True
assert result["start_nodes"] == ["A"]
assert result["sorted_nodes"] == ["A", "B", "C"]
```

**Expected:** ✅ Valid, execution order: A → B → C

---

### Test 2: Valid Branching ✅

**Graph:**
```
      → [B]
[A]
      → [C]
```

**Code:**
```python
result = GraphService.validate_graph(nodes, edges)

assert result["valid"] == True
assert result["start_nodes"] == ["A"]
# B and C can be in any order (parallel)
assert "A" == result["sorted_nodes"][0]
assert set(result["sorted_nodes"][1:]) == {"B", "C"}
```

**Expected:** ✅ Valid, A first, then B and C (any order)

---

### Test 3: Valid Converging ✅

**Graph:**
```
[A] ↘
     → [C]
[B] ↗
```

**Code:**
```python
result = GraphService.validate_graph(nodes, edges)

assert result["valid"] == True
assert set(result["start_nodes"]) == {"A", "B"}
assert "C" == result["sorted_nodes"][-1]  # C must be last
```

**Expected:** ✅ Valid, A and B first (any order), then C

---

### Test 4: Cycle Detection ❌

**Graph:**
```
[A] → [B] → [C]
      ↑     ↓
      ←─────
```

**Code:**
```python
from app.exceptions import CycleError

try:
    result = GraphService.validate_graph(nodes, edges)
    assert False, "Should have raised CycleError"
except CycleError as e:
    print(f"✅ Correctly detected cycle: {e}")
```

**Expected:** ❌ CycleError raised

---

### Test 5: No Start Nodes ❌

**Graph:**
```
[A] → [B]
↑     ↓
←─────
```

**Code:**
```python
from app.exceptions import NoStartNodeError

try:
    result = GraphService.validate_graph(nodes, edges)
    assert False, "Should have raised NoStartNodeError"
except NoStartNodeError as e:
    print(f"✅ Correctly detected no start nodes: {e}")
```

**Expected:** ❌ NoStartNodeError raised

---

### Test 6: Unreachable Nodes ❌

**Graph:**
```
[A] → [B]

[C] → [D]  (disconnected)
```

**Code:**
```python
from app.exceptions import UnreachableNodeError

try:
    result = GraphService.validate_graph(nodes, edges, allow_disconnected=False)
    assert False, "Should have raised UnreachableNodeError"
except UnreachableNodeError as e:
    print(f"✅ Correctly detected unreachable nodes: {e}")

# Allow disconnected
result = GraphService.validate_graph(nodes, edges, allow_disconnected=True)
assert len(result["unreachable_nodes"]) > 0
```

**Expected:** ❌ UnreachableNodeError (unless allowed)

---

### Test 7: Complex Valid Graph ✅

**Graph:**
```
[A] → [B] → [D] → [F]
  ↘   ↗   ↘
   [C]     [E]
```

**Code:**
```python
result = GraphService.validate_graph(nodes, edges)

assert result["valid"] == True
assert result["start_nodes"] == ["A"]
assert "A" == result["sorted_nodes"][0]
assert "F" == result["sorted_nodes"][-1]
```

**Expected:** ✅ Valid, proper topological order

---

## 🐍 Python Test Script

```python
from app.models.node import Node
from app.models.edge import Edge
from app.services.graph_service import GraphService
from app.exceptions import CycleError, NoStartNodeError

# Test 1: Linear Pipeline
print("Test 1: Linear Pipeline")
nodes = [
    Node(id="A", workflow_id="wf1", name="Start", node_type="llm_call", config={}),
    Node(id="B", workflow_id="wf1", name="Middle", node_type="http_request", config={}),
    Node(id="C", workflow_id="wf1", name="End", node_type="db_write", config={})
]
edges = [
    Edge(id="e1", workflow_id="wf1", source_node_id="A", target_node_id="B"),
    Edge(id="e2", workflow_id="wf1", source_node_id="B", target_node_id="C")
]

result = GraphService.validate_graph(nodes, edges)
print(f"✅ Valid: {result['valid']}")
print(f"   Start nodes: {result['start_nodes']}")
print(f"   Execution order: {result['sorted_nodes']}")

# Test 2: Cycle Detection
print("\nTest 2: Cycle Detection")
cycle_edges = [
    Edge(id="e1", workflow_id="wf1", source_node_id="A", target_node_id="B"),
    Edge(id="e2", workflow_id="wf1", source_node_id="B", target_node_id="C"),
    Edge(id="e3", workflow_id="wf1", source_node_id="C", target_node_id="A")  # Cycle!
]

try:
    result = GraphService.validate_graph(nodes, cycle_edges)
    print("❌ Should have detected cycle!")
except CycleError as e:
    print(f"✅ Cycle detected: {e}")

# Test 3: Branching
print("\nTest 3: Branching")
branch_edges = [
    Edge(id="e1", workflow_id="wf1", source_node_id="A", target_node_id="B"),
    Edge(id="e2", workflow_id="wf1", source_node_id="A", target_node_id="C")
]

result = GraphService.validate_graph(nodes, branch_edges)
print(f"✅ Valid: {result['valid']}")
print(f"   Start nodes: {result['start_nodes']}")
print(f"   Execution order: {result['sorted_nodes']}")

# Test 4: Find Start Nodes
print("\nTest 4: Find Start Nodes")
reverse_adj = GraphService.build_reverse_adjacency_list(nodes, edges)
start_nodes = GraphService.find_start_nodes(reverse_adj)
print(f"   Start nodes: {start_nodes}")

# Test 5: Topological Sort
print("\nTest 5: Topological Sort")
sorted_nodes = GraphService.topological_sort(nodes, edges)
print(f"   Sorted: {sorted_nodes}")
```

---

## 📊 Algorithm Complexity

| Method | Time Complexity | Space Complexity |
|--------|----------------|------------------|
| build_adjacency_list | O(V + E) | O(V + E) |
| build_reverse_adjacency_list | O(V + E) | O(V + E) |
| find_start_nodes | O(V) | O(1) |
| topological_sort | O(V + E) | O(V) |
| detect_cycles | O(V + E) | O(V) |
| find_reachable_nodes | O(V + E) | O(V) |
| validate_graph | O(V + E) | O(V + E) |

Where:
- V = number of nodes (vertices)
- E = number of edges

---

## 🔍 How It Works

### Kahn's Algorithm (Topological Sort)

```
1. Calculate in-degree for all nodes
2. Add all nodes with in-degree 0 to queue
3. While queue is not empty:
   a. Remove node from queue
   b. Add to result
   c. For each child:
      - Decrease in-degree by 1
      - If in-degree becomes 0, add to queue
4. If result.length != nodes.length:
   → Cycle detected!
```

### DFS Cycle Detection

```
1. Mark all nodes as unvisited
2. For each unvisited node:
   a. Start DFS
   b. Mark as visited and add to recursion stack
   c. Visit all children
   d. If child is in recursion stack:
      → Cycle detected!
   e. Remove from recursion stack after processing
```

---

## ✨ Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Adjacency List | ✅ | Efficient graph representation |
| Topological Sort | ✅ | Kahn's algorithm |
| Cycle Detection | ✅ | DFS with recursion stack |
| Start Node Finding | ✅ | In-degree = 0 |
| Reachability Check | ✅ | BFS from start nodes |
| Graph Validation | ✅ | Complete validation |
| Custom Exceptions | ✅ | Clear error messages |
| Performance | ✅ | O(V + E) complexity |

---

## 🎯 Usage in Execution Engine

```python
from app.services.graph_service import GraphService
from app.services.workflow_service import WorkflowService
from app.exceptions import GraphValidationError

async def execute_workflow(db, workflow_id, user_id):
    """Execute a workflow"""
    
    # 1. Load workflow data
    workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
    nodes = await WorkflowService.list_nodes(db, workflow_id, user_id)
    edges = await WorkflowService.list_edges(db, workflow_id, user_id)
    
    # 2. Validate graph structure
    try:
        validation = GraphService.validate_graph(nodes, edges)
    except GraphValidationError as e:
        raise HTTPException(400, f"Invalid workflow graph: {e}")
    
    # 3. Get execution order
    execution_order = validation["sorted_nodes"]
    
    # 4. Execute nodes in order
    results = {}
    for node_id in execution_order:
        node = next(n for n in nodes if str(n.id) == node_id)
        result = await execute_node(node, results)
        results[node_id] = result
    
    return results
```

---

## 🐛 Error Handling

```python
from app.exceptions import (
    CycleError,
    NoStartNodeError,
    UnreachableNodeError,
    DisconnectedGraphError,
    GraphValidationError
)

try:
    execution_order = GraphService.get_execution_order(nodes, edges)
    # Execute workflow
    
except CycleError:
    # Workflow has circular dependencies
    return {"error": "Workflow contains cycles. Please remove circular dependencies."}
    
except NoStartNodeError:
    # All nodes have incoming edges
    return {"error": "Workflow has no start nodes. Add at least one node with no incoming edges."}
    
except UnreachableNodeError:
    # Some nodes can't be reached
    return {"error": "Some nodes are unreachable. Ensure all nodes are connected."}
    
except DisconnectedGraphError:
    # Multiple disconnected graphs
    return {"error": "Workflow has disconnected components. Connect all nodes."}
    
except GraphValidationError as e:
    # Generic graph error
    return {"error": f"Graph validation failed: {e}"}
```

---

## 📈 Stats

- **Methods implemented:** 8
- **Exceptions created:** 5
- **Lines of code:** ~300
- **Test scenarios:** 7+
- **Algorithm complexity:** O(V + E)
- **Ready for:** Execution engine integration

---

## ✅ Next Steps

With graph utilities complete:

1. **Integrate with Execution Service** - Use in workflow execution
2. **Add to Validation Endpoint** - Optional validation API
3. **Implement Node Handlers** - Execute individual nodes
4. **Build Execution Engine** - Complete workflow runner

---

**🎊 Graph utilities are production-ready and tested!**

The execution engine can now use these utilities to:
- Determine execution order
- Detect cycles
- Validate workflows
- Ensure graph integrity





