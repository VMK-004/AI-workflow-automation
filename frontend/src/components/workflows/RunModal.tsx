import { type FC } from 'react';
import { XMarkIcon, CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { useExecutionStore } from '../../store/executionStore';
import { Loader } from '../common/Loader';
import { Button } from '../common/Button';

const STATUS_COLORS = {
  pending: 'text-gray-400',
  running: 'text-blue-500 animate-pulse',
  success: 'text-green-500',
  failed: 'text-red-500',
};

const STATUS_BG = {
  pending: 'bg-gray-50',
  running: 'bg-blue-50',
  success: 'bg-green-50',
  failed: 'bg-red-50',
};

export const RunModal: FC = () => {
  const { isModalOpen, isRunning, runData, error, closeModal, reset } = useExecutionStore();

  const handleClose = () => {
    closeModal();
    setTimeout(reset, 300);
  };

  if (!isModalOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={handleClose} />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-3xl bg-white rounded-2xl shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              {isRunning ? 'Executing Workflow...' : 'Workflow Execution Results'}
            </h3>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

                {/* Content */}
                <div className="max-h-[600px] overflow-y-auto px-6 py-4">
                  {/* Loading State */}
                  {isRunning && (
                    <div className="flex flex-col items-center justify-center py-12">
                      <Loader text="Running workflow..." />
                      <p className="mt-4 text-sm text-gray-500">
                        This may take a few moments...
                      </p>
                    </div>
                  )}

                  {/* Error State */}
                  {error && !isRunning && (
                    <div className="rounded-lg bg-red-50 border border-red-200 p-4">
                      <div className="flex">
                        <XCircleIcon className="h-6 w-6 text-red-500 mr-3 flex-shrink-0" />
                        <div>
                          <h4 className="text-sm font-semibold text-red-900 mb-1">
                            Execution Failed
                          </h4>
                          <p className="text-sm text-red-700">{error}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Success State with Results */}
                  {runData && !isRunning && (
                    <div className="space-y-6">
                      {/* Overall Status */}
                      <div className={`rounded-lg border p-4 ${
                        runData.status === 'success' 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-red-50 border-red-200'
                      }`}>
                        <div className="flex items-center">
                          {runData.status === 'success' ? (
                            <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3" />
                          ) : (
                            <XCircleIcon className="h-6 w-6 text-red-500 mr-3" />
                          )}
                          <div>
                            <h4 className={`text-sm font-semibold ${
                              runData.status === 'success' ? 'text-green-900' : 'text-red-900'
                            }`}>
                              {runData.status === 'success' 
                                ? 'Workflow Completed Successfully' 
                                : 'Workflow Failed'}
                            </h4>
                            {runData.error_message && (
                              <p className="text-sm text-red-700 mt-1">{runData.error_message}</p>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Node Executions */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-3">
                          Node Executions
                        </h4>
                        <div className="space-y-3">
                          {runData.node_executions && runData.node_executions.length > 0 ? (
                            runData.node_executions.map((nodeExec) => (
                                <div
                                  key={nodeExec.id}
                                  className={`rounded-lg border p-4 ${STATUS_BG[nodeExec.status]}`}
                                >
                                  <div className="flex items-start">
                                    {/* Status Icon */}
                                    {nodeExec.status === 'success' && (
                                      <CheckCircleIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeExec.status]}`} />
                                    )}
                                    {nodeExec.status === 'failed' && (
                                      <XCircleIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeExec.status]}`} />
                                    )}
                                    {(nodeExec.status === 'pending' || nodeExec.status === 'running') && (
                                      <ClockIcon className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${STATUS_COLORS[nodeExec.status]}`} />
                                    )}
                                    
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center justify-between mb-2">
                                        <h5 className="text-sm font-medium text-gray-900">
                                          {nodeExec.node_name || `Node ${nodeExec.node_id}`}
                                        </h5>
                                        <span className={`text-xs font-medium uppercase px-2 py-1 rounded ${
                                          nodeExec.status === 'success' 
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
                                          <pre className="text-xs bg-white border border-gray-200 rounded p-2 overflow-x-auto">
                                            {JSON.stringify(nodeExec.output_data, null, 2)}
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))
                          ) : (
                            <p className="text-sm text-gray-500 text-center py-4">
                              No node executions recorded
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Final Output */}
                      {runData.output_data && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-3">
                            Final Output
                          </h4>
                          <pre className="text-sm bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto">
                            {JSON.stringify(runData.output_data, null, 2)}
                          </pre>
                        </div>
                      )}

                      {/* Execution Time */}
                      <div className="text-xs text-gray-500">
                        <p>Started: {new Date(runData.started_at).toLocaleString()}</p>
                        {runData.completed_at && (
                          <p>Completed: {new Date(runData.completed_at).toLocaleString()}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
            <Button variant="ghost" onClick={handleClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

