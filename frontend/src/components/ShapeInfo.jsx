import React from 'react';

export const ShapeInfo = ({ label, confidence }) => {
  if (!label) return null;

  return (
    <div style={{
      position: 'absolute',
      top: '80px',
      left: '20px',
      padding: '15px 20px',
      background: 'rgba(0, 0, 0, 0.7)',
      border: '2px solid #00bfff',
      borderRadius: '8px',
      color: '#fff',
      fontFamily: 'monospace',
      fontSize: '14px',
      zIndex: 1000,
      minWidth: '200px',
    }}>
      <div style={{ marginBottom: '10px', color: '#00bfff', fontSize: '12px' }}>
        DETECTED SHAPE
      </div>
      <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
        {label.toUpperCase()}
      </div>
      <div style={{ fontSize: '12px', color: '#aaa' }}>
        Confidence: {(confidence * 100).toFixed(1)}%
      </div>
      <div style={{
        marginTop: '10px',
        height: '4px',
        background: '#333',
        borderRadius: '2px',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: `${confidence * 100}%`,
          background: confidence > 0.7 ? '#00ff00' : '#ffaa00',
          transition: 'width 0.3s ease',
        }} />
      </div>
    </div>
  );
};
