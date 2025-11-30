import { FC } from 'react';
import type { Edge } from '../../api/edges';
import type { Node } from '../../api/nodes';

interface EdgeLineProps {
  edge: Edge;
  nodes: Node[];
  onDelete?: (edgeId: string) => void;
}

export const EdgeLine: FC<EdgeLineProps> = ({ edge, nodes, onDelete }) => {
  const sourceNode = nodes.find((n) => n.id === edge.source_node_id);
  const targetNode = nodes.find((n) => n.id === edge.target_node_id);

  if (!sourceNode || !targetNode) {
    return null;
  }

  // Calculate positions
  // Source: right side of source node (connector dot position)
  const sourceX = (sourceNode.position_x || 0) + 200; // node width
  const sourceY = (sourceNode.position_y || 0) + 40; // roughly middle of node

  // Target: left side of target node
  const targetX = targetNode.position_x || 0;
  const targetY = (targetNode.position_y || 0) + 40;

  // Create a curved path (cubic bezier)
  const controlPointOffset = Math.abs(targetX - sourceX) / 2;
  const path = `M ${sourceX} ${sourceY} C ${sourceX + controlPointOffset} ${sourceY}, ${targetX - controlPointOffset} ${targetY}, ${targetX} ${targetY}`;

  const handleLineClick = () => {
    if (onDelete && window.confirm('Delete this connection?')) {
      onDelete(edge.id);
    }
  };

  return (
    <g>
      {/* Main path */}
      <path
        d={path}
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="hover:stroke-blue-500 cursor-pointer transition-all"
        onClick={handleLineClick}
      />
      
      {/* Invisible wider path for easier clicking */}
      <path
        d={path}
        fill="none"
        stroke="transparent"
        strokeWidth="12"
        className="cursor-pointer"
        onClick={handleLineClick}
      />
    </g>
  );
};

// Arrow marker definition (should be added once to SVG defs)
export const EdgeArrowMarker: FC = () => (
  <defs>
    <marker
      id="arrowhead"
      markerWidth="10"
      markerHeight="10"
      refX="9"
      refY="3"
      orient="auto"
      markerUnits="strokeWidth"
    >
      <path d="M0,0 L0,6 L9,3 z" fill="#94a3b8" />
    </marker>
  </defs>
);

