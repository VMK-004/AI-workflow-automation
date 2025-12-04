import { FC, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useVectorStore } from '../store/vectorStore';
import { AddDocumentsModal } from '../components/vectors/AddDocumentsModal';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Loader } from '../components/common/Loader';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../utils/http';

export const VectorCollectionDetailPage: FC = () => {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const {
    currentCollection,
    searchResults,
    isLoading,
    fetchCollectionDetails,
    search: searchCollection,
    clearSearchResults,
  } = useVectorStore();

  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [topK, setTopK] = useState(5);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  useEffect(() => {
    if (name) {
      fetchCollectionDetails(name);
    }
    return () => {
      clearSearchResults();
    };
  }, [name, fetchCollectionDetails, clearSearchResults]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    if (!name) return;

    setIsSearching(true);
    try {
      await searchCollection(name, query.trim(), topK);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddSuccess = async () => {
    if (name) {
      await fetchCollectionDetails(name);
    }
  };

  if (isLoading && !currentCollection) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader text="Loading collection..." />
      </div>
    );
  }

  if (!currentCollection) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Collection not found
          </h1>
          <Button onClick={() => navigate('/vectors')}>
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Collections
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/vectors')}
          className="mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Back to Collections
        </Button>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {currentCollection.name}
            </h1>
            <div className="mt-4 space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Documents:</span>{' '}
                {currentCollection.document_count}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Dimension:</span>{' '}
                {currentCollection.dimension}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Created:</span>{' '}
                {new Date(currentCollection.created_at).toLocaleString()}
              </p>
            </div>
          </div>
          <Button onClick={() => setIsAddModalOpen(true)}>
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Documents
          </Button>
        </div>
      </div>

      {/* Search Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Search Collection
        </h2>
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query..."
                disabled={isSearching}
              />
            </div>
            <div className="w-24">
              <Input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                placeholder="Top K"
                min={1}
                max={50}
                disabled={isSearching}
              />
            </div>
            <Button type="submit" disabled={isSearching || !query.trim()}>
              <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
              {isSearching ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Search Results
            </h2>
            <span className="text-sm text-gray-500">
              Found {searchResults.total_results} result(s)
            </span>
          </div>

          {searchResults.results.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No results found for "{searchResults.query}"
            </p>
          ) : (
            <div className="space-y-4">
              {searchResults.results.map((result, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-medium text-gray-500">
                      Result #{index + 1}
                    </span>
                    <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      Score: {result.score.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-gray-900 mb-3 whitespace-pre-wrap">
                    {result.text}
                  </p>
                  {result.metadata && Object.keys(result.metadata).length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-500 mb-1">
                        Metadata:
                      </p>
                      <pre className="text-xs bg-gray-50 rounded p-2 overflow-x-auto">
                        {JSON.stringify(result.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!searchResults && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Search the Collection
          </h3>
          <p className="text-gray-600">
            Enter a query above to search for similar documents using semantic
            search
          </p>
        </div>
      )}

      {/* Add Documents Modal */}
      <AddDocumentsModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        collectionName={currentCollection.name}
        onSuccess={handleAddSuccess}
      />
    </div>
  );
};


