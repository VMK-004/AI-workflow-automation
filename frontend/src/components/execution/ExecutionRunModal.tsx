import { FC } from 'react';
import { XMarkIcon, CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import type { WorkflowRun } from '../../api/execution';
import { Button } from '../common/Button';

interface ExecutionRunModalProps {
  isOpen: boolean;
  onClose: () => void;
  run: WorkflowRun;
}

const STATUS_COLORS = {
  pending: 'text-gray-400',
  running: 'text-blue-500 animate-pulse',
  success: 'text-green-500',
  completed: 'text-green-500',
  failed: 'text-red-500',
};

const STATUS_BG = {
  pending: 'bg-gray-50',
  running: 'bg-blue-50',
  success: 'bg-green-50',
  completed: 'bg-green-50',
  failed: 'bg-red-50',
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

export const ExecutionRunModal: FC<ExecutionRunModalProps> = ({ isOpen, onClose, run }) => {
  if (!isOpen) {
    return null;
  }

  const statusKey = run.status as keyof typeof STATUS_COLORS;
  const statusColor = STATUS_COLORS[statusKey] || STATUS_COLORS.pending;
  const statusBg = STATUS_BG[statusKey] || STATUS_BG.pending;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-4xl bg-white rounded-2xl shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Execution Run Details</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="max-h-[600px] overflow-y-auto px-6 py-4">
            <div className="space-y-6">
              {/* Run Summary */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Run Summary</h4>
                <div className={`rounded-lg border p-4 ${
                  run.status === 'success' || run.status === 'completed'
                    ? 'bg-green-50 border-green-200'
                    : run.status === 'failed'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs font-medium text-gray-700">Status</p>
                      <div className="mt-1 flex items-center">
                        {(run.status === 'success' || run.status === 'completed') && (
                          <CheckCircleIcon className={`h-5 w-5 mr-2 ${statusColor}`} />
                        )}
                        {run.status === 'failed' && (
                          <XCircleIcon className={`h-5 w-5 mr-2 ${statusColor}`} />
                        )}
                        {(run.status === 'pending' || run.status === 'running') && (
                          <ClockIcon className={`h-5 w-5 mr-2 ${statusColor}`} />
                        )}
                        <span className={`text-sm font-medium ${
                          run.status === 'success' || run.status === 'completed'
                            ? 'text-green-900'
                            : run.status === 'failed'
                            ? 'text-red-900'
                            : 'text-gray-900'
                        }`}>
                          {run.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-700">Started At</p>
                      <p className="mt-1 text-sm text-gray-900">{formatDate(run.started_at)}</p>
                    </div>
                    {run.completed_at && (
                      <div>
                        <p className="text-xs font-medium text-gray-700">Completed At</p>
                        <p className="mt-1 text-sm text-gray-900">{formatDate(run.completed_at)}</p>
                      </div>
                    )}
                    {run.completed_at && run.started_at && (
                      <div>
                        <p className="text-xs font-medium text-gray-700">Duration</p>
                        <p className="mt-1 text-sm text-gray-900">
                          {((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(2)}s
                        </p>
                      </div>
                    )}
                  </div>
                  {run.error_message && (
                    <div className="mt-4 pt-4 border-t border-red-200">
                      <p className="text-xs font-medium text-red-900 mb-1">Error Message</p>
                      <p className="text-sm text-red-700">{run.error_message}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Node Executions */}
              {run.node_executions && run.node_executions.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Node Executions</h4>
                  <div className="space-y-3">
                    {run.node_executions
                      .sort((a, b) => (a.execution_order || 0) - (b.execution_order || 0))
                      .map((nodeExec) => {
                        const nodeStatusKey = nodeExec.status as keyof typeof STATUS_COLORS;
                        const nodeStatusBg = STATUS_BG[nodeStatusKey] || STATUS_BG.pending;
                        return (
                          <div
                            key={nodeExec.id}
                            className={`rounded-lg border p-4 ${nodeStatusBg}`}
                          >
                            <div className="flex items-start">
                              {nodeExec.status === 'success' || nodeExec.status === 'completed' ? (
                                <CheckCircleIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeStatusKey] || STATUS_COLORS.pending}`} />
                              ) : nodeExec.status === 'failed' ? (
                                <XCircleIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeStatusKey] || STATUS_COLORS.pending}`} />
                              ) : (
                                <ClockIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeStatusKey] || STATUS_COLORS.pending}`} />
                              )}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-2">
                                  <h5 className="text-sm font-medium text-gray-900">
                                    {nodeExec.node_name || `Node ${nodeExec.node_id}`}
                                  </h5>
                                  <span className={`text-xs font-medium uppercase px-2 py-1 rounded ${
                                    nodeExec.status === 'success' || nodeExec.status === 'completed'
                                      ? 'bg-green-100 text-green-800'
                                      : nodeExec.status === 'failed'
                                      ? 'bg-red-100 text-red-800'
                                      : 'bg-gray-100 text-gray-800'
                                  }`}>
                                    {nodeExec.status}
                                  </span>
                                </div>

                                {/* Error Message */}
                                {nodeExec.error_message && (
                                  <div className="mb-2 text-sm text-red-700">
                                    <strong>Error:</strong> {nodeExec.error_message}
                                  </div>
                                )}

                                {/* Output Data */}
                                {nodeExec.output_data && (
                                  <div>
                                    <div className="text-xs font-medium text-gray-700 mb-1">
                                      Output:
                                    </div>
                                    <pre className="text-xs bg-white border border-gray-200 rounded p-2 overflow-x-auto max-h-40 overflow-y-auto">
                                      {JSON.stringify(nodeExec.output_data, null, 2)}
                                    </pre>
                                  </div>
                                )}

                                {/* Timing */}
                                {nodeExec.started_at && (
                                  <div className="mt-2 text-xs text-gray-500">
                                    <p>Started: {formatDate(nodeExec.started_at)}</p>
                                    {nodeExec.completed_at && (
                                      <p>Completed: {formatDate(nodeExec.completed_at)}</p>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}

              {/* Final Output */}
              {run.output_data && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Final Output</h4>
                  <pre className="text-sm bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto max-h-60 overflow-y-auto">
                    {JSON.stringify(run.output_data, null, 2)}
                  </pre>
                </div>
              )}

              {/* Input Data */}
              {run.input_data && Object.keys(run.input_data).length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Input Data</h4>
                  <pre className="text-sm bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto max-h-60 overflow-y-auto">
                    {JSON.stringify(run.input_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

