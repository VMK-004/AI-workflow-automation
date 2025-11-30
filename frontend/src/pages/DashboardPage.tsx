import { FC, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWorkflowStore } from '../store/workflowStore';
import { useVectorStore } from '../store/vectorStore';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';
import {
  RectangleStackIcon,
  CircleStackIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';

export const DashboardPage: FC = () => {
  const { workflows, fetchWorkflows, isLoading: workflowsLoading } = useWorkflowStore();
  const { collections, fetchCollections, isLoading: collectionsLoading } = useVectorStore();

  useEffect(() => {
    fetchWorkflows();
    fetchCollections();
  }, []);

  if (workflowsLoading || collectionsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to AI Workflow Builder
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Workflows Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <RectangleStackIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Workflows</h2>
                <p className="text-sm text-gray-500">
                  {workflows.length} workflow{workflows.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <Link to="/workflows">
              <Button size="sm" variant="ghost">
                View All
              </Button>
            </Link>
          </div>
          
          <div className="space-y-2 mb-4">
            {workflows.slice(0, 3).map((workflow) => (
              <Link
                key={workflow.id}
                to={`/workflows/${workflow.id}`}
                className="block p-3 rounded-md hover:bg-gray-50 transition-colors"
              >
                <p className="font-medium text-gray-900">{workflow.name}</p>
                {workflow.description && (
                  <p className="text-sm text-gray-500 truncate">{workflow.description}</p>
                )}
              </Link>
            ))}
            {workflows.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                No workflows yet
              </p>
            )}
          </div>

          <Link to="/workflows">
            <Button variant="primary" className="w-full">
              <PlusIcon className="h-5 w-5 mr-2" />
              Create Workflow
            </Button>
          </Link>
        </div>

        {/* Vector Collections Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <CircleStackIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Vector Collections</h2>
                <p className="text-sm text-gray-500">
                  {collections.length} collection{collections.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <Link to="/vectors">
              <Button size="sm" variant="ghost">
                View All
              </Button>
            </Link>
          </div>

          <div className="space-y-2 mb-4">
            {collections.slice(0, 3).map((collection) => (
              <div
                key={collection.id}
                className="block p-3 rounded-md bg-gray-50"
              >
                <p className="font-medium text-gray-900">{collection.name}</p>
                <p className="text-sm text-gray-500">
                  {collection.document_count} documents
                </p>
              </div>
            ))}
            {collections.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                No collections yet
              </p>
            )}
          </div>

          <Link to="/vectors">
            <Button variant="primary" className="w-full">
              <PlusIcon className="h-5 w-5 mr-2" />
              Create Collection
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/workflows">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all cursor-pointer">
              <h3 className="font-medium text-gray-900">Create Workflow</h3>
              <p className="text-sm text-gray-500 mt-1">
                Build an AI-powered workflow
              </p>
            </div>
          </Link>
          <Link to="/vectors">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all cursor-pointer">
              <h3 className="font-medium text-gray-900">Add Documents</h3>
              <p className="text-sm text-gray-500 mt-1">
                Create a vector collection
              </p>
            </div>
          </Link>
          <Link to="/runs">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all cursor-pointer">
              <h3 className="font-medium text-gray-900">View History</h3>
              <p className="text-sm text-gray-500 mt-1">
                Check execution results
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

