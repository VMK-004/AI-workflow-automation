import { create } from 'zustand';
import type { Node } from '../api/nodes';
import type { Edge } from '../api/edges';

interface DragState {
  nodeId: string;
  offsetX: number;
  offsetY: number;
}

interface ConnectingState {
  sourceNodeId: string;
}

interface EditorState {
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  dragging: DragState | null;
  connecting: ConnectingState | null;
  
  // State setters
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  
  // Node operations
  selectNode: (nodeId: string | null) => void;
  updateNodePosition: (nodeId: string, x: number, y: number) => void;
  updateNode: (nodeId: string, updates: Partial<Node>) => void;
  removeNode: (nodeId: string) => void;
  
  // Dragging
  startDragging: (nodeId: string, offsetX: number, offsetY: number) => void;
  stopDragging: () => void;
  
  // Connecting
  startConnecting: (sourceNodeId: string) => void;
  finishConnecting: (targetNodeId: string) => void;
  cancelConnecting: () => void;
  
  // Edge operations
  addEdge: (edge: Edge) => void;
  removeEdge: (edgeId: string) => void;
  
  // Utilities
  getSelectedNode: () => Node | null;
  clearSelection: () => void;
}

export const useEditorStore = create<EditorState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  dragging: null,
  connecting: null,

  setNodes: (nodes) => {
    set({ nodes });
  },

  setEdges: (edges) => {
    set({ edges });
  },

  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId });
  },

  updateNodePosition: (nodeId, x, y) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? { ...node, position_x: x, position_y: y }
          : node
      ),
    }));
  },

  updateNode: (nodeId, updates) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId ? { ...node, ...updates } : node
      ),
    }));
  },

  removeNode: (nodeId) => {
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== nodeId),
      edges: state.edges.filter(
        (edge) => edge.source_node_id !== nodeId && edge.target_node_id !== nodeId
      ),
      selectedNodeId: state.selectedNodeId === nodeId ? null : state.selectedNodeId,
    }));
  },

  startDragging: (nodeId, offsetX, offsetY) => {
    set({ dragging: { nodeId, offsetX, offsetY } });
  },

  stopDragging: () => {
    set({ dragging: null });
  },

  startConnecting: (sourceNodeId) => {
    set({ connecting: { sourceNodeId } });
  },

  finishConnecting: (targetNodeId) => {
    const state = get();
    if (state.connecting && state.connecting.sourceNodeId !== targetNodeId) {
      // Edge will be created by the parent component via API
      set({ connecting: null });
    }
  },

  cancelConnecting: () => {
    set({ connecting: null });
  },

  addEdge: (edge) => {
    set((state) => ({
      edges: [...state.edges, edge],
    }));
  },

  removeEdge: (edgeId) => {
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== edgeId),
    }));
  },

  getSelectedNode: () => {
    const state = get();
    return state.nodes.find((node) => node.id === state.selectedNodeId) || null;
  },

  clearSelection: () => {
    set({ selectedNodeId: null });
  },
}));

