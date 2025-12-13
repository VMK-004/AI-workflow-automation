import { FC, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Modal } from '../components/common/Modal';
import { PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../utils/http';

export const WorkflowListPage: FC = () => {
  const { workflows, fetchWorkflows, createWorkflow, deleteWorkflow, isLoading } = useWorkflowStore();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error('Name is required');
      return;
    }

    setIsCreating(true);
    try {
      await createWorkflow(name, description);
      toast.success('Workflow created successfully');
      setIsCreateModalOpen(false);
      setName('');
      setDescription('');
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (id: string, workflowName: string) => {
    if (!confirm(`Are you sure you want to delete "${workflowName}"?`)) {
      return;
    }

    try {
      await deleteWorkflow(id);
      toast.success('Workflow deleted');
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader text="Loading workflows..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-2 text-gray-600">
            Create and manage your AI workflows
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <PlusIcon className="h-5 w-5 mr-2" />
          New Workflow
        </Button>
      </div>

      {workflows.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">No workflows yet</p>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            Create Your First Workflow
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <Link to={`/workflows/${workflow.id}`}>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 hover:text-primary-600">
                  {workflow.name}
                </h3>
              </Link>
              {workflow.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {workflow.description}
                </p>
              )}
              <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
                <Link to={`/workflows/${workflow.id}`}>
                  <Button size="sm" variant="primary">
                    Edit
                  </Button>
                </Link>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleDelete(workflow.id, workflow.name)}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Workflow Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Workflow"
      >
        <div className="space-y-4">
          <Input
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My Workflow"
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does this workflow do?"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              variant="ghost"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              isLoading={isCreating}
            >
              Create
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};





