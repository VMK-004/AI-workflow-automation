import client from './client';

export interface Node {
  id: string;
  workflow_id: string;
  name: string;
  node_type: 'llm_call' | 'http_request' | 'faiss_search' | 'db_write';
  config: Record<string, any>;
  position_x?: number;
  position_y?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateNodeRequest {
  name: string;
  node_type: string;
  config: Record<string, any>;
  position_x?: number;
  position_y?: number;
}

export interface UpdateNodeRequest {
  name?: string;
  config?: Record<string, any>;
  position_x?: number;
  position_y?: number;
}

export const nodesApi = {
  list: async (workflowId: string): Promise<Node[]> => {
    const response = await client.get(`/workflows/${workflowId}/nodes`);
    return response.data;
  },

  create: async (workflowId: string, data: CreateNodeRequest): Promise<Node> => {
    const response = await client.post(`/workflows/${workflowId}/nodes`, data);
    return response.data;
  },

  get: async (workflowId: string, nodeId: string): Promise<Node> => {
    const response = await client.get(`/workflows/${workflowId}/nodes/${nodeId}`);
    return response.data;
  },

  update: async (workflowId: string, nodeId: string, data: UpdateNodeRequest): Promise<Node> => {
    const response = await client.put(`/workflows/${workflowId}/nodes/${nodeId}`, data);
    return response.data;
  },

  delete: async (workflowId: string, nodeId: string): Promise<void> => {
    await client.delete(`/workflows/${workflowId}/nodes/${nodeId}`);
  },
};


