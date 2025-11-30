import { FC, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVectorStore } from '../store/vectorStore';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';
import { CreateCollectionModal } from '../components/vectors/CreateCollectionModal';
import { PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../utils/http';

export const VectorCollectionsPage: FC = () => {
  const navigate = useNavigate();
  const {
    collections,
    fetchCollections,
    deleteCollection,
    isLoading,
  } = useVectorStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  useEffect(() => {
    fetchCollections();
  }, [fetchCollections]);

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete collection "${name}"?`)) {
      return;
    }

    try {
      await deleteCollection(name);
      toast.success('Collection deleted');
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleViewCollection = (name: string) => {
    navigate(`/vector-collections/${name}`);
  };

  if (isLoading && collections.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader text="Loading collections..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Vector Collections</h1>
          <p className="mt-2 text-gray-600">
            Manage your document collections for semantic search
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <PlusIcon className="h-5 w-5 mr-2" />
          New Collection
        </Button>
      </div>

      {collections.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">No collections yet</p>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            Create Your First Collection
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((collection) => (
            <div
              key={collection.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {collection.name}
              </h3>
              <div className="space-y-2 mb-4">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Documents:</span> {collection.document_count}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Dimension:</span> {collection.dimension}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Created:</span>{' '}
                  {new Date(collection.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => handleViewCollection(collection.name)}
                >
                  View
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleDelete(collection.name)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Collection Modal */}
      <CreateCollectionModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};

