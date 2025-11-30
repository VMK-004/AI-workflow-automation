import { create } from 'zustand';
import { workflowsApi } from '../api/workflows';
import { nodesApi } from '../api/nodes';
import { edgesApi } from '../api/edges';
import type { Workflow } from '../api/workflows';
import type { Node } from '../api/nodes';
import type { Edge } from '../api/edges';

interface WorkflowState {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  nodes: Node[];
  edges: Edge[];
  isLoading: boolean;

  // Workflows
  fetchWorkflows: () => Promise<void>;
  createWorkflow: (name: string, description?: string) => Promise<Workflow>;
  updateWorkflow: (id: string, name?: string, description?: string) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  setCurrentWorkflow: (workflow: Workflow | null) => void;

  // Nodes
  fetchNodes: (workflowId: string) => Promise<void>;
  createNode: (workflowId: string, data: any) => Promise<Node>;
  updateNode: (workflowId: string, nodeId: string, data: any) => Promise<void>;
  deleteNode: (workflowId: string, nodeId: string) => Promise<void>;

  // Edges
  fetchEdges: (workflowId: string) => Promise<void>;
  createEdge: (workflowId: string, sourceId: string, targetId: string) => Promise<Edge>;
  deleteEdge: (workflowId: string, edgeId: string) => Promise<void>;

  // Combined fetch
  fetchWorkflowData: (workflowId: string) => Promise<void>;
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  workflows: [],
  currentWorkflow: null,
  nodes: [],
  edges: [],
  isLoading: false,

  fetchWorkflows: async () => {
    set({ isLoading: true });
    try {
      const workflows = await workflowsApi.list();
      set({ workflows, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createWorkflow: async (name: string, description?: string) => {
    const workflow = await workflowsApi.create({ name, description });
    set({ workflows: [...get().workflows, workflow] });
    return workflow;
  },

  updateWorkflow: async (id: string, name?: string, description?: string) => {
    const updated = await workflowsApi.update(id, { name, description });
    set({
      workflows: get().workflows.map((w) => (w.id === id ? updated : w)),
      currentWorkflow: get().currentWorkflow?.id === id ? updated : get().currentWorkflow,
    });
  },

  deleteWorkflow: async (id: string) => {
    await workflowsApi.delete(id);
    set({
      workflows: get().workflows.filter((w) => w.id !== id),
      currentWorkflow: get().currentWorkflow?.id === id ? null : get().currentWorkflow,
    });
  },

  setCurrentWorkflow: (workflow: Workflow | null) => {
    set({ currentWorkflow: workflow });
  },

  fetchNodes: async (workflowId: string) => {
    const nodes = await nodesApi.list(workflowId);
    set({ nodes });
  },

  createNode: async (workflowId: string, data: any) => {
    const node = await nodesApi.create(workflowId, data);
    set({ nodes: [...get().nodes, node] });
    return node;
  },

  updateNode: async (workflowId: string, nodeId: string, data: any) => {
    const updated = await nodesApi.update(workflowId, nodeId, data);
    set({
      nodes: get().nodes.map((n) => (n.id === nodeId ? updated : n)),
    });
  },

  deleteNode: async (workflowId: string, nodeId: string) => {
    await nodesApi.delete(workflowId, nodeId);
    set({ nodes: get().nodes.filter((n) => n.id !== nodeId) });
  },

  fetchEdges: async (workflowId: string) => {
    const edges = await edgesApi.list(workflowId);
    set({ edges });
  },

  createEdge: async (workflowId: string, sourceId: string, targetId: string) => {
    const edge = await edgesApi.create(workflowId, {
      source_node_id: sourceId,
      target_node_id: targetId,
    });
    set({ edges: [...get().edges, edge] });
    return edge;
  },

  deleteEdge: async (workflowId: string, edgeId: string) => {
    await edgesApi.delete(workflowId, edgeId);
    set({ edges: get().edges.filter((e) => e.id !== edgeId) });
  },

  fetchWorkflowData: async (workflowId: string) => {
    set({ isLoading: true });
    try {
      const [workflow, nodes, edges] = await Promise.all([
        workflowsApi.get(workflowId),
        nodesApi.list(workflowId),
        edgesApi.list(workflowId),
      ]);
      set({
        currentWorkflow: workflow,
        nodes,
        edges,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));

