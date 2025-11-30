import client from './client';

export interface Edge {
  id: string;
  workflow_id: string;
  source_node_id: string;
  target_node_id: string;
  created_at: string;
}

export interface CreateEdgeRequest {
  source_node_id: string;
  target_node_id: string;
}

export const edgesApi = {
  list: async (workflowId: string): Promise<Edge[]> => {
    const response = await client.get(`/workflows/${workflowId}/edges`);
    return response.data;
  },

  create: async (workflowId: string, data: CreateEdgeRequest): Promise<Edge> => {
    const response = await client.post(`/workflows/${workflowId}/edges`, data);
    return response.data;
  },

  get: async (workflowId: string, edgeId: string): Promise<Edge> => {
    const response = await client.get(`/workflows/${workflowId}/edges/${edgeId}`);
    return response.data;
  },

  delete: async (workflowId: string, edgeId: string): Promise<void> => {
    await client.delete(`/workflows/${workflowId}/edges/${edgeId}`);
  },
};

