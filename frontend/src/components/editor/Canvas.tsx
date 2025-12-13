import { FC, MouseEvent, useEffect, useRef } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { NodeCard } from './NodeCard';
import { EdgeLine, EdgeArrowMarker } from './EdgeLine';

interface CanvasProps {
  onNodePositionChange: (nodeId: string, x: number, y: number) => void;
  onEdgeCreate: (sourceNodeId: string, targetNodeId: string) => void;
}

export const Canvas: FC<CanvasProps> = ({ onNodePositionChange, onEdgeCreate }) => {
  const {
    nodes,
    edges,
    selectedNodeId,
    dragging,
    connecting,
    selectNode,
    startDragging,
    stopDragging,
    updateNodePosition,
    startConnecting,
    finishConnecting,
    cancelConnecting,
    clearSelection,
  } = useEditorStore();

  const canvasRef = useRef<HTMLDivElement>(null);

  // Handle mouse move for dragging
  useEffect(() => {
    const handleMouseMove = (e: globalThis.MouseEvent) => {
      if (dragging && canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        const newX = e.clientX - rect.left - dragging.offsetX;
        const newY = e.clientY - rect.top - dragging.offsetY;
        
        // Constrain to canvas bounds
        const constrainedX = Math.max(0, Math.min(newX, rect.width - 200));
        const constrainedY = Math.max(0, Math.min(newY, rect.height - 100));
        
        updateNodePosition(dragging.nodeId, constrainedX, constrainedY);
      }
    };

    const handleMouseUp = () => {
      if (dragging) {
        const node = nodes.find((n) => n.id === dragging.nodeId);
        if (node) {
          onNodePositionChange(node.id, node.position_x || 0, node.position_y || 0);
        }
        stopDragging();
      }
    };

    if (dragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);

      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [dragging, nodes, onNodePositionChange, stopDragging, updateNodePosition]);

  // Handle canvas click (deselect)
  const handleCanvasClick = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === canvasRef.current) {
      clearSelection();
      if (connecting) {
        cancelConnecting();
      }
    }
  };

  // Handle connector click
  const handleConnectorClick = (nodeId: string) => {
    if (connecting) {
      // Finish connection
      if (connecting.sourceNodeId !== nodeId) {
        onEdgeCreate(connecting.sourceNodeId, nodeId);
        finishConnecting(nodeId);
      }
    } else {
      // Start connection
      startConnecting(nodeId);
    }
  };

  // Handle ESC key to cancel connecting
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && connecting) {
        cancelConnecting();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [connecting, cancelConnecting]);

  return (
    <div
      ref={canvasRef}
      className="relative w-full h-full bg-gray-50 overflow-hidden"
      onClick={handleCanvasClick}
      style={{
        backgroundImage: `
          linear-gradient(to right, #e5e7eb 1px, transparent 1px),
          linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px',
      }}
    >
      {/* SVG Layer for Edges */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ zIndex: 1 }}
      >
        <EdgeArrowMarker />
        <g className="pointer-events-auto">
          {edges.map((edge) => (
            <EdgeLine key={edge.id} edge={edge} nodes={nodes} />
          ))}
        </g>
      </svg>

      {/* Nodes Layer */}
      <div className="absolute inset-0" style={{ zIndex: 2 }}>
        {nodes.map((node) => (
          <NodeCard
            key={node.id}
            node={node}
            selected={selectedNodeId === node.id}
            onSelect={selectNode}
            onDragStart={startDragging}
            onConnectorClick={handleConnectorClick}
            isConnecting={connecting?.sourceNodeId === node.id}
          />
        ))}
      </div>

      {/* Connecting Indicator */}
      {connecting && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
          Click on another node to connect (ESC to cancel)
        </div>
      )}
    </div>
  );
};





