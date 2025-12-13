import { useState, useEffect, type FC } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { Node } from '../../api/nodes';
import { Button } from '../common/Button';
import { Input } from '../common/Input';

interface NodeSidebarProps {
  node: Node | null;
  onClose: () => void;
  onSave: (nodeId: string, updates: { name: string; config: any }) => void;
  onDelete?: (nodeId: string) => void;
}

const NODE_TYPE_LABELS = {
  llm_call: 'LLM Call',
  http_request: 'HTTP Request',
  faiss_search: 'FAISS Search',
  db_write: 'DB Write',
};

export const NodeSidebar: FC<NodeSidebarProps> = ({ node, onClose, onSave, onDelete }) => {
  const [name, setName] = useState('');
  const [configJson, setConfigJson] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (node) {
      setName(node.name);
      setConfigJson(JSON.stringify(node.config || {}, null, 2));
      setJsonError(null);
    }
  }, [node]);

  if (!node) {
    return null;
  }

  const handleSave = async () => {
    // Validate JSON
    try {
      const parsedConfig = JSON.parse(configJson);
      setJsonError(null);
      
      setIsSaving(true);
      await onSave(node.id, {
        name,
        config: parsedConfig,
      });
      setIsSaving(false);
    } catch (error) {
      setJsonError('Invalid JSON format');
    }
  };

  const handleJsonChange = (value: string) => {
    setConfigJson(value);
    // Clear error when user is typing
    if (jsonError) {
      setJsonError(null);
    }
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 shadow-lg flex flex-col h-full max-h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 flex-shrink-0">
        <h3 className="text-lg font-semibold text-gray-900">Edit Node</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {/* Node Type (Read-only) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <div className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700">
            {NODE_TYPE_LABELS[node.node_type as keyof typeof NODE_TYPE_LABELS] || node.node_type}
          </div>
        </div>

        {/* Node Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <Input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter node name"
          />
        </div>

        {/* Configuration JSON */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Configuration (JSON)
          </label>
          <textarea
            value={configJson}
            onChange={(e) => handleJsonChange(e.target.value)}
            className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="{}"
            spellCheck={false}
          />
          {jsonError && (
            <p className="mt-1 text-sm text-red-600">{jsonError}</p>
          )}
          
          {/* Config Hints */}
          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-xs font-medium text-blue-900 mb-1">Configuration Examples:</p>
            <div className="text-xs text-blue-700 space-y-1">
              {node.node_type === 'llm_call' && (
                <div>
                  <code>{"{ \"prompt_template\": \"Say hello in {language}\", \"temperature\": 0.3, \"max_tokens\": 200 }"}</code>
                </div>
              )}
              {node.node_type === 'http_request' && (
                <div>
                  <code>{"{ \"url\": \"...\", \"method\": \"GET\" }"}</code>
                </div>
              )}
              {node.node_type === 'faiss_search' && (
                <div>
                  <code>{"{ \"collection\": \"...\", \"top_k\": 5 }"}</code>
                </div>
              )}
              {node.node_type === 'db_write' && (
                <div>
                  <code>{"{ \"table\": \"...\", \"operation\": \"INSERT\" }"}</code>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-200 space-y-2 flex-shrink-0">
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={isSaving || !!jsonError}
          className="w-full"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          {onDelete && (
            <Button
              variant="danger"
              onClick={() => {
                if (node && confirm(`Are you sure you want to delete "${node.name}"? This will also remove all connections to this node.`)) {
                  onDelete(node.id);
                }
              }}
              className="flex-1"
            >
              Delete
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

