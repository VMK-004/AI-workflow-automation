import { create } from 'zustand';
import type { WorkflowRun, WorkflowRunListItem } from '../api/execution';

interface ExecutionState {
  // Current run execution state
  isRunning: boolean;
  runData: WorkflowRun | null;
  error: string | null;
  isModalOpen: boolean;

  // Run history state
  runs: WorkflowRunListItem[];
  selectedRun: WorkflowRun | null;
  isRunModalOpen: boolean;
  isLoadingRuns: boolean;
  runsError: string | null;
  totalRuns: number;

  // Current run actions
  startRun: () => void;
  setRunData: (runData: WorkflowRun) => void;
  setError: (error: string) => void;
  finishRun: () => void;
  clearError: () => void;
  openModal: () => void;
  closeModal: () => void;
  reset: () => void;

  // Run history actions
  fetchRuns: (limit?: number, offset?: number) => Promise<void>;
  fetchRunDetails: (runId: string) => Promise<void>;
  openRunModal: (run: WorkflowRun) => void;
  closeRunModal: () => void;
  clearRuns: () => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  // Current run execution state
  isRunning: false,
  runData: null,
  error: null,
  isModalOpen: false,

  // Run history state
  runs: [],
  selectedRun: null,
  isRunModalOpen: false,
  isLoadingRuns: false,
  runsError: null,
  totalRuns: 0,

  // Current run actions
  startRun: () => {
    set({ isRunning: true, error: null, runData: null, isModalOpen: true });
  },

  setRunData: (runData: WorkflowRun) => {
    set({ runData, isRunning: false });
  },

  setError: (error: string) => {
    set({ error, isRunning: false });
  },

  finishRun: () => {
    set({ isRunning: false });
  },

  clearError: () => {
    set({ error: null });
  },

  openModal: () => {
    set({ isModalOpen: true });
  },

  closeModal: () => {
    set({ isModalOpen: false });
  },

  reset: () => {
    set({ isRunning: false, runData: null, error: null, isModalOpen: false });
  },

  // Run history actions
  fetchRuns: async (limit: number = 100, offset: number = 0) => {
    set({ isLoadingRuns: true, runsError: null });
    try {
      const { executionApi } = await import('../api/execution');
      const response = await executionApi.listAllRuns(limit, offset);
      set({
        runs: response.runs,
        totalRuns: response.total,
        isLoadingRuns: false,
        runsError: null,
      });
    } catch (error: any) {
      set({
        isLoadingRuns: false,
        runsError: error?.message || 'Failed to fetch runs',
      });
    }
  },

  fetchRunDetails: async (runId: string) => {
    try {
      const { executionApi } = await import('../api/execution');
      const run = await executionApi.getRunDetails(runId);
      set({ selectedRun: run, isRunModalOpen: true });
    } catch (error: any) {
      set({ runsError: error?.message || 'Failed to fetch run details' });
    }
  },

  openRunModal: (run: WorkflowRun) => {
    set({ selectedRun: run, isRunModalOpen: true });
  },

  closeRunModal: () => {
    set({ isRunModalOpen: false, selectedRun: null });
  },

  clearRuns: () => {
    set({ runs: [], totalRuns: 0, selectedRun: null });
  },
}));

