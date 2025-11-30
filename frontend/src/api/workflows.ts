import client from './client';

export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkflowRequest {
  name: string;
  description?: string;
}

export interface UpdateWorkflowRequest {
  name?: string;
  description?: string;
}

export interface ExecuteWorkflowRequest {
  input_data?: Record<string, any>;
}

export interface WorkflowExecutionResult {
  workflow_run_id: string;
  status: string;
  output: any;
  node_outputs: Record<string, any>;
}

export const workflowsApi = {
  list: async (): Promise<Workflow[]> => {
    const response = await client.get('/workflows');
    return response.data;
  },

  create: async (data: CreateWorkflowRequest): Promise<Workflow> => {
    const response = await client.post('/workflows', data);
    return response.data;
  },

  get: async (id: string): Promise<Workflow> => {
    const response = await client.get(`/workflows/${id}`);
    return response.data;
  },

  update: async (id: string, data: UpdateWorkflowRequest): Promise<Workflow> => {
    const response = await client.put(`/workflows/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/workflows/${id}`);
  },

  execute: async (id: string, data: ExecuteWorkflowRequest): Promise<WorkflowExecutionResult> => {
    const response = await client.post(`/workflows/${id}/execute`, data);
    return response.data;
  },
};

