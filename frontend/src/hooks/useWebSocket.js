import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    // Create WebSocket connection
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📩 Received:', data);
        setLastMessage(data);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  return { isConnected, lastMessage, sendMessage };
};
