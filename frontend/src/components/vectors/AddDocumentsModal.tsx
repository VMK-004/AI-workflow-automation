import { FC, useState, useRef } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { vectorsApi, type DocumentInput } from '../../api/vectors';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../../utils/http';
import { DocumentArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface AddDocumentsModalProps {
  isOpen: boolean;
  onClose: () => void;
  collectionName: string;
  onSuccess?: () => void;
}

export const AddDocumentsModal: FC<AddDocumentsModalProps> = ({
  isOpen,
  onClose,
  collectionName,
  onSuccess,
}) => {
  const [documentsText, setDocumentsText] = useState('');
  const [metadataJson, setMetadataJson] = useState('{}');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadMode, setUploadMode] = useState<'text' | 'files'>('text');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    
    // Validate file types
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.md'];
    const invalidFiles = files.filter(
      (file) => !allowedTypes.some((ext) => file.name.toLowerCase().endsWith(ext))
    );
    
    if (invalidFiles.length > 0) {
      toast.error(`Invalid file type(s): ${invalidFiles.map((f) => f.name).join(', ')}. Supported: PDF, DOCX, TXT, MD`);
      return;
    }
    
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (uploadMode === 'files') {
      // Handle file upload
      if (selectedFiles.length === 0) {
        toast.error('Please select at least one file');
        return;
      }

      // Parse metadata JSON
      let sharedMetadata: Record<string, any> = {};
      if (metadataJson.trim()) {
        try {
          sharedMetadata = JSON.parse(metadataJson);
          if (typeof sharedMetadata !== 'object' || Array.isArray(sharedMetadata)) {
            throw new Error('Metadata must be an object');
          }
        } catch (error) {
          toast.error('Invalid metadata JSON format');
          return;
        }
      }

      setIsSubmitting(true);
      try {
        const result = await vectorsApi.uploadFiles(
          collectionName,
          selectedFiles,
          Object.keys(sharedMetadata).length > 0 ? sharedMetadata : undefined
        );

        const successMsg = `Uploaded ${result.files_processed || selectedFiles.length} file(s), added ${result.documents_added} document(s)!`;
        toast.success(successMsg);
        
        if (result.errors && result.errors.length > 0) {
          toast.error(`Some files failed: ${result.errors.join('; ')}`, { duration: 5000 });
        }

        setSelectedFiles([]);
        setMetadataJson('{}');
        if (onSuccess) {
          onSuccess();
        }
        onClose();
      } catch (error) {
        toast.error(getErrorMessage(error));
      } finally {
        setIsSubmitting(false);
      }
      return;
    }

    // Handle text input (existing logic)
    if (!documentsText.trim()) {
      toast.error('At least one document is required');
      return;
    }

    // Parse metadata JSON
    let sharedMetadata: Record<string, any> = {};
    if (metadataJson.trim()) {
      try {
        sharedMetadata = JSON.parse(metadataJson);
        if (typeof sharedMetadata !== 'object' || Array.isArray(sharedMetadata)) {
          throw new Error('Metadata must be an object');
        }
      } catch (error) {
        toast.error('Invalid metadata JSON format');
        return;
      }
    }

    // Parse documents from textarea
    let documents: DocumentInput[];
    try {
      // Try parsing as JSON array first
      const parsed = JSON.parse(documentsText);
      if (Array.isArray(parsed)) {
        documents = parsed.map((doc: any) => {
          if (typeof doc === 'string') {
            return {
              text: doc,
              metadata: { ...sharedMetadata },
            };
          }
          return {
            text: doc.text || doc.content || doc.document || String(doc),
            metadata: { ...sharedMetadata, ...(doc.metadata || {}) },
          };
        });
      } else {
        throw new Error('Not an array');
      }
    } catch {
      // If not JSON, treat each line as a separate document
      documents = documentsText
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line.length > 0)
        .map((line) => ({
          text: line,
          metadata: { ...sharedMetadata },
        }));
    }

    if (documents.length === 0) {
      toast.error('No valid documents found');
      return;
    }

    setIsSubmitting(true);
    try {
      await vectorsApi.addDocuments(collectionName, { documents });

      toast.success(`Added ${documents.length} document(s) successfully!`);
      setDocumentsText('');
      setMetadataJson('{}');
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setDocumentsText('');
      setMetadataJson('{}');
      setSelectedFiles([]);
      setUploadMode('text');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={`Add Documents to ${collectionName}`}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Mode Selector */}
        <div className="flex space-x-4 border-b border-gray-200 pb-4">
          <button
            type="button"
            onClick={() => setUploadMode('text')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              uploadMode === 'text'
                ? 'bg-primary-100 text-primary-700 border-2 border-primary-500'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent'
            }`}
            disabled={isSubmitting}
          >
            Type Text
          </button>
          <button
            type="button"
            onClick={() => setUploadMode('files')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              uploadMode === 'files'
                ? 'bg-primary-100 text-primary-700 border-2 border-primary-500'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent'
            }`}
            disabled={isSubmitting}
          >
            Upload Files
          </button>
        </div>

        {/* File Upload Mode */}
        {uploadMode === 'files' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Upload Files *
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-primary-400 transition-colors">
                <div className="space-y-1 text-center">
                  <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                    >
                      <span>Select files</span>
                      <input
                        id="file-upload"
                        ref={fileInputRef}
                        name="file-upload"
                        type="file"
                        className="sr-only"
                        multiple
                        accept=".pdf,.docx,.doc,.txt,.md"
                        onChange={handleFileSelect}
                        disabled={isSubmitting}
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">PDF, DOCX, TXT, MD up to 10MB each</p>
                </div>
              </div>

              {/* Selected Files List */}
              {selectedFiles.length > 0 && (
                <div className="mt-3 space-y-2">
                  {selectedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-md"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(index)}
                        className="ml-3 text-gray-400 hover:text-red-600 transition-colors"
                        disabled={isSubmitting}
                      >
                        <XMarkIcon className="h-5 w-5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {/* Text Input Mode */}
        {uploadMode === 'text' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Documents *
            </label>
          <textarea
            value={documentsText}
            onChange={(e) => setDocumentsText(e.target.value)}
            placeholder={`Enter documents (one per line):
Python is a programming language
FastAPI is a web framework

Or JSON array format:
[
  {"text": "Document 1", "metadata": {"source": "book"}},
  {"text": "Document 2"}
]`}
            className="w-full h-48 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y"
            required
            disabled={isSubmitting}
          />
          <p className="mt-1 text-xs text-gray-500">
            Enter one document per line, or use JSON array format
          </p>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Shared Metadata (Optional)
          </label>
          <textarea
            value={metadataJson}
            onChange={(e) => setMetadataJson(e.target.value)}
            placeholder='{"category": "tech", "source": "docs"}'
            className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isSubmitting}
          />
          <p className="mt-1 text-xs text-gray-500">
            JSON object with metadata to apply to all documents (will be merged with document-specific metadata)
          </p>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? uploadMode === 'files'
                ? 'Uploading...'
                : 'Adding...'
              : uploadMode === 'files'
              ? 'Upload Files'
              : 'Add Documents'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

