import { FC, MouseEvent, useRef } from 'react';
import classNames from 'classnames';
import type { Node } from '../../api/nodes';

interface NodeCardProps {
  node: Node;
  selected: boolean;
  onSelect: (nodeId: string) => void;
  onDragStart: (nodeId: string, offsetX: number, offsetY: number) => void;
  onConnectorClick: (nodeId: string) => void;
  isConnecting: boolean;
}

const NODE_TYPE_COLORS = {
  llm_call: 'bg-blue-500 border-blue-600',
  http_request: 'bg-green-500 border-green-600',
  faiss_search: 'bg-purple-500 border-purple-600',
  db_write: 'bg-orange-500 border-orange-600',
};

const NODE_TYPE_LABELS = {
  llm_call: 'LLM Call',
  http_request: 'HTTP Request',
  faiss_search: 'FAISS Search',
  db_write: 'DB Write',
};

export const NodeCard: FC<NodeCardProps> = ({
  node,
  selected,
  onSelect,
  onDragStart,
  onConnectorClick,
  isConnecting,
}) => {
  const nodeRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    // Don't start drag if clicking on connector
    if ((e.target as HTMLElement).classList.contains('connector-dot')) {
      return;
    }

    e.preventDefault();
    onSelect(node.id);

    const rect = nodeRef.current?.getBoundingClientRect();
    if (rect) {
      const offsetX = e.clientX - rect.left;
      const offsetY = e.clientY - rect.top;
      onDragStart(node.id, offsetX, offsetY);
    }
  };

  const handleConnectorClick = (e: MouseEvent) => {
    e.stopPropagation();
    onConnectorClick(node.id);
  };

  const colorClass = NODE_TYPE_COLORS[node.node_type as keyof typeof NODE_TYPE_COLORS] || 'bg-gray-500 border-gray-600';
  const typeLabel = NODE_TYPE_LABELS[node.node_type as keyof typeof NODE_TYPE_LABELS] || node.node_type;

  return (
    <div
      ref={nodeRef}
      className={classNames(
        'absolute cursor-move bg-white rounded-lg shadow-lg border-2 transition-all',
        selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300',
        'hover:shadow-xl'
      )}
      style={{
        left: `${node.position_x || 0}px`,
        top: `${node.position_y || 0}px`,
        width: '200px',
        userSelect: 'none',
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header with type indicator */}
      <div className={classNames('px-3 py-2 rounded-t-md text-white text-sm font-medium', colorClass)}>
        {typeLabel}
      </div>

      {/* Node Name */}
      <div className="px-3 py-3">
        <p className="font-semibold text-gray-900 truncate">{node.name}</p>
      </div>

      {/* Connector Dot (for creating edges) */}
      <div
        className={classNames(
          'connector-dot absolute -right-2 top-1/2 transform -translate-y-1/2',
          'w-4 h-4 rounded-full border-2 border-white cursor-pointer',
          'transition-all hover:scale-125',
          isConnecting ? 'bg-green-500' : 'bg-gray-400 hover:bg-blue-500'
        )}
        onClick={handleConnectorClick}
        title="Click to start connecting"
      />
    </div>
  );
};

