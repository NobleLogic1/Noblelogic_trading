import React, { useRef, useEffect, useState } from 'react';

const GPUChart = ({ data, width = 800, height = 400, symbol = 'BTC' }) => {
  const canvasRef = useRef(null);
  const glRef = useRef(null);
  const programRef = useRef(null);
  const animationRef = useRef(null);
  const [isGPUEnabled, setIsGPUEnabled] = useState(false);

  // Vertex shader for GPU-accelerated rendering
  const vertexShaderSource = `
    attribute vec2 a_position;
    attribute vec3 a_color;
    uniform vec2 u_resolution;
    uniform float u_time;
    varying vec3 v_color;
    
    void main() {
      // Convert from pixels to 0.0 to 1.0
      vec2 zeroToOne = a_position / u_resolution;
      
      // Convert from 0->1 to 0->2
      vec2 zeroToTwo = zeroToOne * 2.0;
      
      // Convert from 0->2 to -1->+1 (clipspace)
      vec2 clipSpace = zeroToTwo - 1.0;
      
      // Add subtle animation based on time
      float wave = sin(u_time * 0.001 + a_position.x * 0.01) * 0.02;
      
      gl_Position = vec4(clipSpace * vec2(1, -1) + vec2(0, wave), 0, 1);
      v_color = a_color;
    }
  `;

  // Fragment shader for advanced visual effects
  const fragmentShaderSource = `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec3 v_color;
    
    void main() {
      vec2 uv = gl_FragCoord.xy / u_resolution.xy;
      
      // Create gradient effect
      float gradient = smoothstep(0.0, 1.0, uv.y);
      
      // Add subtle glow effect
      float glow = 1.0 + 0.3 * sin(u_time * 0.002);
      
      // Combine color with effects
      vec3 finalColor = v_color * gradient * glow;
      
      // Add subtle transparency for glass morphism effect
      gl_FragColor = vec4(finalColor, 0.85);
    }
  `;

  // Initialize WebGL
  const initWebGL = () => {
    const canvas = canvasRef.current;
    if (!canvas) return false;

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
      console.warn('WebGL not supported, falling back to canvas 2D');
      return false;
    }

    glRef.current = gl;

    // Create and compile shaders
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

    if (!vertexShader || !fragmentShader) return false;

    // Create program
    const program = createProgram(gl, vertexShader, fragmentShader);
    if (!program) return false;

    programRef.current = program;
    setIsGPUEnabled(true);
    return true;
  };

  const createShader = (gl, type, source) => {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error('Error compiling shader:', gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }

    return shader;
  };

  const createProgram = (gl, vertexShader, fragmentShader) => {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Error linking program:', gl.getProgramInfoLog(program));
      return null;
    }

    return program;
  };

  // Generate chart data points for GPU rendering
  const generateChartData = () => {
    if (!data || data.length === 0) {
      // Generate sample data if none provided
      const sampleData = [];
      for (let i = 0; i < 200; i++) {
        sampleData.push({
          price: 45000 + Math.sin(i * 0.1) * 5000 + Math.random() * 1000,
          volume: Math.random() * 1000000,
          timestamp: Date.now() - (200 - i) * 60000
        });
      }
      return sampleData;
    }
    return data;
  };

  // Render chart using WebGL
  const renderWebGL = () => {
    const gl = glRef.current;
    const program = programRef.current;
    if (!gl || !program) return;

    const chartData = generateChartData();
    
    // Set viewport
    gl.viewport(0, 0, width, height);
    
    // Clear canvas
    gl.clearColor(0.0, 0.0, 0.0, 0.0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Use program
    gl.useProgram(program);

    // Create vertices for price line
    const vertices = [];
    const colors = [];
    
    const maxPrice = Math.max(...chartData.map(d => d.price));
    const minPrice = Math.min(...chartData.map(d => d.price));
    const priceRange = maxPrice - minPrice;

    chartData.forEach((point, index) => {
      const x = (index / (chartData.length - 1)) * width;
      const y = ((point.price - minPrice) / priceRange) * height * 0.6 + height * 0.2;
      
      vertices.push(x, y);
      
      // Color based on price movement
      const priceChange = index > 0 ? point.price - chartData[index - 1].price : 0;
      if (priceChange > 0) {
        colors.push(0.2, 0.8, 0.4); // Green for up
      } else if (priceChange < 0) {
        colors.push(0.9, 0.3, 0.3); // Red for down
      } else {
        colors.push(0.5, 0.5, 0.9); // Blue for neutral
      }
    });

    // Create and bind position buffer
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);

    // Create and bind color buffer
    const colorBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);

    // Get attribute locations
    const positionLocation = gl.getAttribLocation(program, 'a_position');
    const colorLocation = gl.getAttribLocation(program, 'a_color');

    // Enable attributes
    gl.enableVertexAttribArray(positionLocation);
    gl.enableVertexAttribArray(colorLocation);

    // Bind position buffer and set attribute
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    // Bind color buffer and set attribute
    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
    gl.vertexAttribPointer(colorLocation, 3, gl.FLOAT, false, 0, 0);

    // Set uniforms
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    const timeLocation = gl.getUniformLocation(program, 'u_time');
    
    gl.uniform2f(resolutionLocation, width, height);
    gl.uniform1f(timeLocation, Date.now());

    // Enable blending for transparency
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    // Draw the line
    gl.drawArrays(gl.LINE_STRIP, 0, vertices.length / 2);

    // Clean up
    gl.deleteBuffer(positionBuffer);
    gl.deleteBuffer(colorBuffer);
  };

  // Fallback canvas 2D rendering
  const renderCanvas2D = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const chartData = generateChartData();

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (chartData.length === 0) return;

    const maxPrice = Math.max(...chartData.map(d => d.price));
    const minPrice = Math.min(...chartData.map(d => d.price));
    const priceRange = maxPrice - minPrice;

    // Draw gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Draw price line
    ctx.beginPath();
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;

    chartData.forEach((point, index) => {
      const x = (index / (chartData.length - 1)) * width;
      const y = height - ((point.price - minPrice) / priceRange) * height * 0.8 - height * 0.1;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();
  };

  // Animation loop
  const animate = () => {
    if (isGPUEnabled) {
      renderWebGL();
    } else {
      renderCanvas2D();
    }
    animationRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    if (!initWebGL()) {
      // Fallback to canvas 2D
      setIsGPUEnabled(false);
    }

    // Start animation loop
    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [data]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">
          {symbol} Price Chart {isGPUEnabled && <span className="text-green-400 text-sm">(GPU Accelerated)</span>}
        </h3>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 rounded text-xs ${isGPUEnabled ? 'bg-green-600 text-white' : 'bg-amber-600 text-white'}`}>
            {isGPUEnabled ? 'WebGL' : '2D Canvas'}
          </span>
        </div>
      </div>
      
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="w-full h-auto border border-slate-600/30 rounded-lg bg-slate-800/30"
          style={{ maxWidth: '100%' }}
        />
        
        {/* Overlay for additional info */}
        <div className="absolute top-2 right-2 bg-slate-800/80 backdrop-blur-sm rounded-lg p-2 text-sm text-slate-300">
          <div>WebGL Support: {isGPUEnabled ? 'Yes' : 'No'}</div>
          <div>Data Points: {generateChartData().length}</div>
          <div>Refresh Rate: 60fps</div>
        </div>
      </div>
    </div>
  );
};

export default GPUChart;