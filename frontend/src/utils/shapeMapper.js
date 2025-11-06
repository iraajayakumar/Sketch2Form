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
 * Arduino RGB565 color definitions (exact values from your sketch)
 */
const ARDUINO_COLORS = {
  63488: '#FF0000',  // RED
  65504: '#FFFF00',  // YELLOW
  2016:  '#00FF00',  // GREEN
  2047:  '#00FFFF',  // CYAN
  31:    '#0000FF',  // BLUE
  63519: '#FF00FF',  // MAGENTA
};

/**
 * Convert Arduino RGB565 color to Three.js hex color
 * @param {number} arduinoColor - RGB565 color value from Arduino
 * @returns {string} Hex color string for Three.js
 */
export const convertColor = (arduinoColor) => {
  // If no color provided, default to white
  if (!arduinoColor && arduinoColor !== 0) {
    return '#FFFFFF';
  }

  // Check if it's one of the predefined Arduino colors
  if (ARDUINO_COLORS[arduinoColor]) {
    return ARDUINO_COLORS[arduinoColor];
  }

  // Fallback: Convert RGB565 to RGB888
  // RGB565 format: RRRRR GGGGGG BBBBB (5-6-5 bits)
  const r = ((arduinoColor >> 11) & 0x1F) * 8;  // 5 bits, scale to 0-255
  const g = ((arduinoColor >> 5) & 0x3F) * 4;   // 6 bits, scale to 0-255
  const b = (arduinoColor & 0x1F) * 8;          // 5 bits, scale to 0-255

  // Convert to hex color
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

/**
 * Get color name from Arduino color code (for debugging/display)
 */
export const getColorName = (arduinoColor) => {
  const colorNames = {
    63488: 'Red',
    65504: 'Yellow',
    2016:  'Green',
    2047:  'Cyan',
    31:    'Blue',
    63519: 'Magenta',
  };
  
  return colorNames[arduinoColor] || 'Unknown';
};
