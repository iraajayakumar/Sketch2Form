import React, { useRef, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Box, Sphere, Cone } from '@react-three/drei';
import { shapeMapper, convertColor } from '../utils/shapeMapper';

// Individual 3D Shape Component with animation
const Shape3D = ({ shapeData, position }) => {
  const meshRef = useRef();
  const [scale, setScale] = useState(0);

  // Spawn animation - separate useEffect
  useEffect(() => {
    let animationFrame;
    const animate = () => {
      if (scale < 1) {
        setScale((prev) => Math.min(prev + 0.05, 1));
        animationFrame = requestAnimationFrame(animate);
      }
    };
    animate();
    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [scale]);

  // Rotation animation - separate useEffect
  useEffect(() => {
    const interval = setInterval(() => {
      if (meshRef.current) {
        meshRef.current.rotation.y += 0.01;
      }
    }, 16);
    return () => clearInterval(interval);
  }, []);

  const { type, args } = shapeMapper[shapeData.label] || shapeMapper.circle;
  const color = shapeData.color || '#00bfff';

  return (
    <group position={position} scale={[scale, scale, scale]}>
      {type === 'box' && (
        <Box ref={meshRef} args={args}>
          <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
        </Box>
      )}
      {type === 'sphere' && (
        <Sphere ref={meshRef} args={args}>
          <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
        </Sphere>
      )}
      {type === 'cone' && (
        <Cone ref={meshRef} args={args}>
          <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
        </Cone>
      )}
    </group>
  );
};

// Main Canvas Component
export const Canvas3D = ({ shapeData }) => {
  const [shapes, setShapes] = useState([]);

  // Add new shape when data arrives - SINGLE useEffect
  useEffect(() => {
    if (shapeData && shapeData.label && shapeData.points) {
      // Get color from any point (they should all be the same color)
      const colorCode = shapeData.points.find(p => p.c)?.c;
      
      const newShape = {
        id: Date.now(),
        label: shapeData.label,
        color: convertColor(colorCode),
        colorCode: colorCode,
        position: [
          (Math.random() - 0.5) * 6, // Random X
          Math.random() * 3 + 1,      // Random Y (above ground)
          (Math.random() - 0.5) * 6,  // Random Z
        ],
      };
      
      console.log('🎨 Spawning shape:', {
        label: newShape.label,
        colorCode: colorCode,
        hexColor: newShape.color
      });
      
      setShapes((prev) => [...prev, newShape]);

      // Remove shape after 15 seconds
      const timeoutId = setTimeout(() => {
        setShapes((prev) => prev.filter((s) => s.id !== newShape.id));
      }, 15000);

      // Cleanup timeout on unmount
      return () => clearTimeout(timeoutId);
    }
  }, [shapeData]); // Only depends on shapeData

  return (
    <Canvas
      camera={{ position: [5, 5, 5], fov: 60 }}
      style={{ background: '#0a0a0a' }}
    >
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <pointLight position={[-10, -10, -5]} intensity={0.5} />

      {/* Grid Floor - CAD style */}
      <Grid
        args={[20, 20]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor={'#1a1a1a'}
        sectionSize={2}
        sectionThickness={1}
        sectionColor={'#2a2a2a'}
        fadeDistance={30}
        fadeStrength={1}
        followCamera={false}
        infiniteGrid={true}
      />

      {/* Render all spawned shapes */}
      {shapes.map((shape) => (
        <Shape3D key={shape.id} shapeData={shape} position={shape.position} />
      ))}

      {/* Camera Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={3}
        maxDistance={20}
      />
    </Canvas>
  );
};
