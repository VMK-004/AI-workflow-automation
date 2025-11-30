import client from './client';

export interface NodeExecution {
  id: string;
  workflow_run_id: string;
  node_id: string;
  node_name?: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  input_data?: any;
  output_data?: any;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  execution_order?: number;
}

export interface WorkflowRun {
  id: string;
  workflow_id: string;
  user_id: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  input_data?: any;
  output_data?: any;
  error_message?: string | null;
  node_executions?: NodeExecution[];
  started_at: string;
  completed_at?: string | null;
}

export interface RunWorkflowRequest {
  input_data?: Record<string, any>;
}

export interface WorkflowRunListItem {
  id: string;
  workflow_id: string;
  workflow_name: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'completed';
  started_at: string;
  completed_at?: string | null;
  duration_seconds?: number | null;
  final_output_preview?: string | null;
}

export interface WorkflowRunListResponse {
  runs: WorkflowRunListItem[];
  total: number;
}

export const executionApi = {
  runWorkflow: async (workflowId: string, inputData: any = {}): Promise<WorkflowRun> => {
    const response = await client.post(`/workflows/${workflowId}/execute`, {
      input_data: inputData,
    });
    return response.data;
  },

  getWorkflowRun: async (workflowId: string, runId: string): Promise<WorkflowRun> => {
    const response = await client.get(`/workflows/${workflowId}/runs/${runId}`);
    return response.data;
  },

  listWorkflowRuns: async (workflowId: string): Promise<WorkflowRun[]> => {
    const response = await client.get(`/workflows/${workflowId}/runs`);
    return response.data;
  },

  // Execution History API
  listAllRuns: async (limit: number = 100, offset: number = 0): Promise<WorkflowRunListResponse> => {
    const response = await client.get(`/runs`, {
      params: { limit, offset },
    });
    return response.data;
  },

  getRunDetails: async (runId: string): Promise<WorkflowRun> => {
    const response = await client.get(`/runs/${runId}`);
    return response.data;
  },
};

