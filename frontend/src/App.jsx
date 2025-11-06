import React, { useState, useEffect } from 'react';
import { Canvas3D } from './components/Canvas3D';
import { ConnectionStatus } from './components/ConnectionStatus';
import { ShapeInfo } from './components/ShapeInfo';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws');
  const [currentShape, setCurrentShape] = useState(null);

  // Update current shape when new message arrives
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'shape_result') {
      setCurrentShape({
        label: lastMessage.label,
        confidence: lastMessage.confidence,
        points: lastMessage.points,
      });
    }
  }, [lastMessage]);

  return (
    <div className="app">
      {/* Connection Status */}
      <ConnectionStatus isConnected={isConnected} />

      {/* Shape Info Panel */}
      <ShapeInfo 
        label={currentShape?.label} 
        confidence={currentShape?.confidence} 
      />

      {/* 3D Canvas */}
      <Canvas3D shapeData={currentShape} />

      {/* Instructions */}
      <div className="instructions">
        <h3>🎨 SKETCH2FORM</h3>
        <p>Draw a shape on Arduino LCD and watch it appear in 3D!</p>
        <ul>
          <li>🔴 Square → Cube</li>
          <li>🟠 Rectangle → Box</li>
          <li>🟢 Triangle → Cone</li>
          <li>🔵 Circle → Sphere</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
