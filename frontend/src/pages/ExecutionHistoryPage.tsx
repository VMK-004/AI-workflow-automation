import { FC, useEffect } from 'react';
import { useExecutionStore } from '../store/executionStore';
import { ExecutionRunModal } from '../components/execution/ExecutionRunModal';
import { Button } from '../components/common/Button';
import { Loader } from '../components/common/Loader';

const STATUS_BADGE_CLASSES = {
  success: 'bg-green-100 text-green-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  running: 'bg-yellow-100 text-yellow-800',
  pending: 'bg-gray-100 text-gray-800',
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const formatDuration = (seconds: number | null | undefined): string => {
  if (!seconds) return '-';
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  if (seconds < 60) return `${seconds.toFixed(2)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
};

export const ExecutionHistoryPage: FC = () => {
  const {
    runs,
    isLoadingRuns,
    runsError,
    totalRuns,
    fetchRuns,
    openRunModal,
    fetchRunDetails,
    isRunModalOpen,
    selectedRun,
    closeRunModal,
  } = useExecutionStore();

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  const handleViewDetails = async (runId: string) => {
    await fetchRunDetails(runId);
    // Modal will be opened automatically by fetchRunDetails
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Execution History</h1>
        <p className="mt-2 text-gray-600">
          View your workflow execution history and results
        </p>
      </div>

      {/* Error State */}
      {runsError && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4">
          <p className="text-sm text-red-700">{runsError}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoadingRuns ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Loader text="Loading execution history..." />
        </div>
      ) : runs.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600">No workflow runs found.</p>
          <p className="text-sm text-gray-500 mt-2">
            Execute a workflow to see execution history here.
          </p>
        </div>
      ) : (
        <>
          {/* Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Workflow Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Started At
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {runs.map((run) => (
                    <tr key={run.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {run.workflow_name}
                        </div>
                        {run.final_output_preview && (
                          <div className="text-xs text-gray-500 mt-1 max-w-md truncate">
                            {run.final_output_preview}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            STATUS_BADGE_CLASSES[
                              run.status as keyof typeof STATUS_BADGE_CLASSES
                            ] || STATUS_BADGE_CLASSES.pending
                          }`}
                        >
                          {run.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(run.started_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(run.duration_seconds)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewDetails(run.id)}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Total Count */}
          <div className="mt-4 text-sm text-gray-500">
            Showing {runs.length} of {totalRuns} runs
          </div>
        </>
      )}

      {/* Run Details Modal */}
      {isRunModalOpen && selectedRun && (
        <ExecutionRunModal
          isOpen={isRunModalOpen}
          onClose={closeRunModal}
          run={selectedRun}
        />
      )}
    </div>
  );
};

