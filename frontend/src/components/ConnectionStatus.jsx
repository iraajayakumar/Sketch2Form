import React from 'react';

export const ConnectionStatus = ({ isConnected }) => {
  return (
    <div style={{
      position: 'absolute',
      top: '20px',
      left: '20px',
      padding: '10px 20px',
      background: 'rgba(0, 0, 0, 0.7)',
      border: `2px solid ${isConnected ? '#00ff00' : '#ff0000'}`,
      borderRadius: '8px',
      color: '#fff',
      fontFamily: 'monospace',
      fontSize: '14px',
      zIndex: 1000,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: isConnected ? '#00ff00' : '#ff0000',
          animation: isConnected ? 'pulse 2s infinite' : 'none',
        }} />
        <span>{isConnected ? 'Connected to Backend' : 'Disconnected'}</span>
      </div>
    </div>
  );
};
