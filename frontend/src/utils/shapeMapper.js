/**
 * Maps 2D shape labels to 3D geometry configurations
 */
export const shapeMapper = {
  square: {
    type: 'box',
    args: [1, 1, 1], // width, height, depth (cube)
  },
  rectangle: {
    type: 'box',
    args: [1.5, 0.8, 0.5], // elongated box
  },
  triangle: {
    type: 'cone',
    args: [0.6, 1.2, 3], // radius, height, radialSegments (3 = triangle)
  },
  circle: {
    type: 'sphere',
    args: [0.7, 32, 32], // radius, widthSegments, heightSegments
  },
};

/**
 * Convert Arduino color (RGB565) to Three.js color
 */
export const convertColor = (arduinoColor) => {
  // Arduino sends RGB565 format (e.g., 63488 = red)
  // Convert to hex color
  if (!arduinoColor) return '#ffffff';
  
  const r = ((arduinoColor >> 11) & 0x1F) * 8;
  const g = ((arduinoColor >> 5) & 0x3F) * 4;
  const b = (arduinoColor & 0x1F) * 8;
  
  return `rgb(${r}, ${g}, ${b})`;
};
