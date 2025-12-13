import { useEffect, useState, type FC } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../store/workflowStore';
import { useEditorStore } from '../store/editorStore';
import { useExecutionStore } from '../store/executionStore';
import { Canvas } from '../components/editor/Canvas';
import { NodeSidebar } from '../components/editor/NodeSidebar';
import { RunModal } from '../components/workflows/RunModal';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';
import { nodesApi } from '../api/nodes';
import { edgesApi } from '../api/edges';
import { executionApi } from '../api/execution';
import toast from 'react-hot-toast';
import { PlusIcon, PlayIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export const WorkflowEditorPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentWorkflow, nodes, edges, fetchWorkflowData, isLoading } = useWorkflowStore();
  const {
    setNodes,
    setEdges,
    getSelectedNode,
    clearSelection,
    addEdge,
    updateNode,
    removeNode,
  } = useEditorStore();
  const { startRun, setRunData, setError, finishRun } = useExecutionStore();

  const [isAddingNode, setIsAddingNode] = useState(false);
  const [newNodeType, setNewNodeType] = useState<string>('llm_call');

  // Load workflow data
  useEffect(() => {
    if (id) {
      fetchWorkflowData(id);
    }
  }, [id]);

  // Sync workflow nodes/edges to editor store
  useEffect(() => {
    if (nodes && edges) {
      setNodes(nodes);
      setEdges(edges);
    }
  }, [nodes, edges, setNodes, setEdges]);

  // Handle node position change (save to backend)
  const handleNodePositionChange = async (nodeId: string, x: number, y: number) => {
    if (!id) return;

    try {
      const node = nodes.find((n) => n.id === nodeId);
      if (!node) return;

      await nodesApi.update(id, nodeId, {
        name: node.name,
        config: node.config,
        position_x: x,
        position_y: y,
      });
    } catch (error) {
      console.error('Failed to save node position:', error);
      toast.error('Failed to save node position');
    }
  };

  // Handle edge creation
  const handleEdgeCreate = async (sourceNodeId: string, targetNodeId: string) => {
    if (!id) return;

    try {
      const newEdge = await edgesApi.create(id, {
        source_node_id: sourceNodeId,
        target_node_id: targetNodeId,
      });
      
      addEdge(newEdge);
      toast.success('Connection created!');
      
      // Refresh to get updated edges from server
      await fetchWorkflowData(id);
    } catch (error: any) {
      console.error('Failed to create edge:', error);
      toast.error(error.response?.data?.detail || 'Failed to create connection');
    }
  };

  // Handle node save from sidebar
  const handleNodeSave = async (nodeId: string, updates: { name: string; config: any }) => {
    if (!id) return;

    try {
      const node = nodes.find((n) => n.id === nodeId);
      if (!node) return;

      await nodesApi.update(id, nodeId, {
        ...updates,
        position_x: node.position_x,
        position_y: node.position_y,
      });

      updateNode(nodeId, updates);
      toast.success('Node updated!');
      
      // Refresh workflow data
      await fetchWorkflowData(id);
    } catch (error: any) {
      console.error('Failed to update node:', error);
      toast.error(error.response?.data?.detail || 'Failed to update node');
    }
  };

  // Handle node delete
  const handleDeleteNode = async (nodeId: string) => {
    if (!id) return;

    try {
      // Delete from backend
      await nodesApi.delete(id, nodeId);
      
      // Update editor store (removes node and connected edges)
      removeNode(nodeId);
      
      // Close sidebar if this node was selected
      clearSelection();
      
      toast.success('Node deleted!');
      
      // Refresh workflow data to sync with backend
      await fetchWorkflowData(id);
    } catch (error: any) {
      console.error('Failed to delete node:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete node');
    }
  };

  // Handle add node
  const handleAddNode = async () => {
    if (!id) return;

    setIsAddingNode(true);
    try {
      // Create node at center of viewport (or random position)
      const randomX = Math.floor(Math.random() * 400) + 100;
      const randomY = Math.floor(Math.random() * 300) + 100;

      await nodesApi.create(id, {
        name: `New ${newNodeType.replace('_', ' ')}`,
        node_type: newNodeType,
        config: {},
        position_x: randomX,
        position_y: randomY,
      });

      toast.success('Node created!');
      
      // Refresh workflow data
      await fetchWorkflowData(id);
    } catch (error: any) {
      console.error('Failed to create node:', error);
      toast.error(error.response?.data?.detail || 'Failed to create node');
    } finally {
      setIsAddingNode(false);
    }
  };

  // Handle run workflow
  const handleRunWorkflow = async () => {
    if (!id) return;

    // Start the run and open modal
    startRun();
    
    try {
      // Execute the workflow
      const runData = await executionApi.runWorkflow(id, {});
      
      // Store the run data
      setRunData(runData);
      
      // Show success toast
      if (runData.status === 'success') {
        toast.success('Workflow executed successfully!');
      } else {
        toast.error('Workflow execution failed');
      }
    } catch (error: any) {
      console.error('Failed to run workflow:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to execute workflow';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      finishRun();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader text="Loading workflow..." />
      </div>
    );
  }

  if (!currentWorkflow) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-500">Workflow not found</p>
      </div>
    );
  }

  const selectedNode = getSelectedNode();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/workflows')}
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{currentWorkflow.name}</h1>
            {currentWorkflow.description && (
              <p className="text-xs text-gray-600">{currentWorkflow.description}</p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Add Node Controls */}
          <select
            value={newNodeType}
            onChange={(e) => setNewNodeType(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="llm_call">LLM Call</option>
            <option value="http_request">HTTP Request</option>
            <option value="faiss_search">FAISS Search</option>
            <option value="db_write">DB Write</option>
          </select>

          <Button
            variant="primary"
            size="sm"
            onClick={handleAddNode}
            disabled={isAddingNode}
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            {isAddingNode ? 'Adding...' : 'Add Node'}
          </Button>

          <Button variant="ghost" size="sm" onClick={handleRunWorkflow}>
            <PlayIcon className="h-4 w-4 mr-1" />
            Run
          </Button>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas */}
        <div className="flex-1">
          <Canvas
            onNodePositionChange={handleNodePositionChange}
            onEdgeCreate={handleEdgeCreate}
          />
        </div>

        {/* Sidebar (shown when node is selected) */}
        {selectedNode && (
          <NodeSidebar
            node={selectedNode}
            onClose={clearSelection}
            onSave={handleNodeSave}
            onDelete={handleDeleteNode}
          />
        )}
      </div>

      {/* Run Modal */}
      <RunModal />
    </div>
  );
};

