import React, { useRef, useEffect, useState } from 'react';

const GPUParticles = ({ particleCount = 1000, width = 800, height = 400 }) => {
  const canvasRef = useRef(null);
  const glRef = useRef(null);
  const programRef = useRef(null);
  const animationRef = useRef(null);
  const [isGPUEnabled, setIsGPUEnabled] = useState(false);
  const [fps, setFps] = useState(60);

  // Vertex shader for particle system
  const vertexShaderSource = `
    attribute vec2 a_position;
    attribute vec2 a_velocity;
    attribute float a_life;
    attribute vec3 a_color;
    
    uniform vec2 u_resolution;
    uniform float u_time;
    uniform float u_deltaTime;
    
    varying vec3 v_color;
    varying float v_alpha;
    
    void main() {
      // Update particle position based on velocity and time
      vec2 position = a_position + a_velocity * u_deltaTime * 0.01;
      
      // Add some turbulence
      position.x += sin(u_time * 0.001 + a_position.y * 0.01) * 0.5;
      position.y += cos(u_time * 0.0015 + a_position.x * 0.008) * 0.3;
      
      // Convert to clip space
      vec2 zeroToOne = position / u_resolution;
      vec2 zeroToTwo = zeroToOne * 2.0;
      vec2 clipSpace = zeroToTwo - 1.0;
      
      gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
      gl_PointSize = 2.0 + sin(u_time * 0.002 + a_life) * 1.0;
      
      v_color = a_color;
      v_alpha = a_life;
    }
  `;

  // Fragment shader for particle rendering
  const fragmentShaderSource = `
    precision mediump float;
    uniform float u_time;
    varying vec3 v_color;
    varying float v_alpha;
    
    void main() {
      // Create circular particles
      vec2 center = gl_PointCoord - vec2(0.5);
      float distance = length(center);
      
      if (distance > 0.5) discard;
      
      // Create glow effect
      float glow = 1.0 - distance * 2.0;
      glow = pow(glow, 2.0);
      
      // Add time-based pulse
      float pulse = 0.8 + 0.2 * sin(u_time * 0.003);
      
      vec3 finalColor = v_color * pulse;
      float finalAlpha = v_alpha * glow * 0.7;
      
      gl_FragColor = vec4(finalColor, finalAlpha);
    }
  `;

  // Initialize WebGL context and shaders
  const initWebGL = () => {
    const canvas = canvasRef.current;
    if (!canvas) return false;

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
      console.warn('WebGL not supported for particles');
      return false;
    }

    glRef.current = gl;

    // Create shaders
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
      console.error('Particle shader error:', gl.getShaderInfoLog(shader));
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
      console.error('Particle program error:', gl.getProgramInfoLog(program));
      return null;
    }

    return program;
  };

  // Generate particle data
  const generateParticles = () => {
    const positions = [];
    const velocities = [];
    const colors = [];
    const lives = [];

    for (let i = 0; i < particleCount; i++) {
      // Position
      positions.push(
        Math.random() * width,
        Math.random() * height
      );

      // Velocity
      velocities.push(
        (Math.random() - 0.5) * 50,
        (Math.random() - 0.5) * 50
      );

      // Color (trading theme)
      const colorType = Math.random();
      if (colorType < 0.4) {
        // Green (profit)
        colors.push(0.2, 0.8, 0.4);
      } else if (colorType < 0.8) {
        // Blue (neutral)
        colors.push(0.3, 0.6, 0.9);
      } else {
        // Gold (premium)
        colors.push(0.9, 0.7, 0.2);
      }

      // Life (used for alpha)
      lives.push(Math.random());
    }

    return { positions, velocities, colors, lives };
  };

  // Render particles using WebGL
  const renderWebGL = () => {
    const gl = glRef.current;
    const program = programRef.current;
    if (!gl || !program) return;

    // Set viewport
    gl.viewport(0, 0, width, height);

    // Clear with transparent background
    gl.clearColor(0.0, 0.0, 0.0, 0.0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Use shader program
    gl.useProgram(program);

    // Generate particle data
    const particleData = generateParticles();

    // Create buffers
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(particleData.positions), gl.DYNAMIC_DRAW);

    const velocityBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, velocityBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(particleData.velocities), gl.STATIC_DRAW);

    const colorBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(particleData.colors), gl.STATIC_DRAW);

    const lifeBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, lifeBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(particleData.lives), gl.STATIC_DRAW);

    // Get attribute locations
    const positionLocation = gl.getAttribLocation(program, 'a_position');
    const velocityLocation = gl.getAttribLocation(program, 'a_velocity');
    const colorLocation = gl.getAttribLocation(program, 'a_color');
    const lifeLocation = gl.getAttribLocation(program, 'a_life');

    // Set up attributes
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, velocityBuffer);
    gl.enableVertexAttribArray(velocityLocation);
    gl.vertexAttribPointer(velocityLocation, 2, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
    gl.enableVertexAttribArray(colorLocation);
    gl.vertexAttribPointer(colorLocation, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, lifeBuffer);
    gl.enableVertexAttribArray(lifeLocation);
    gl.vertexAttribPointer(lifeLocation, 1, gl.FLOAT, false, 0, 0);

    // Set uniforms
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    const timeLocation = gl.getUniformLocation(program, 'u_time');
    const deltaTimeLocation = gl.getUniformLocation(program, 'u_deltaTime');

    gl.uniform2f(resolutionLocation, width, height);
    gl.uniform1f(timeLocation, Date.now());
    gl.uniform1f(deltaTimeLocation, 16.67); // Assuming 60fps

    // Enable blending
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);

    // Draw particles
    gl.drawArrays(gl.POINTS, 0, particleCount);

    // Cleanup buffers
    gl.deleteBuffer(positionBuffer);
    gl.deleteBuffer(velocityBuffer);
    gl.deleteBuffer(colorBuffer);
    gl.deleteBuffer(lifeBuffer);
  };

  // Fallback canvas 2D rendering
  const renderCanvas2D = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    const particleData = generateParticles();

    // Draw simple particles
    for (let i = 0; i < particleCount / 10; i++) { // Reduce count for performance
      const x = particleData.positions[i * 2];
      const y = particleData.positions[i * 2 + 1];
      const r = particleData.colors[i * 3];
      const g = particleData.colors[i * 3 + 1];
      const b = particleData.colors[i * 3 + 2];
      const alpha = particleData.lives[i] * 0.5;

      ctx.beginPath();
      ctx.arc(x, y, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${alpha})`;
      ctx.fill();
    }
  };

  // Animation loop with FPS counter
  let lastTime = 0;
  let frameCount = 0;
  const animate = (currentTime) => {
    const deltaTime = currentTime - lastTime;
    frameCount++;

    if (frameCount % 60 === 0) {
      setFps(Math.round(1000 / (deltaTime || 16.67)));
    }

    if (isGPUEnabled) {
      renderWebGL();
    } else {
      renderCanvas2D();
    }

    lastTime = currentTime;
    animationRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    if (!initWebGL()) {
      setIsGPUEnabled(false);
    }

    animate(0);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full"
        style={{ position: 'absolute', top: 0, left: 0, zIndex: 1 }}
      />
      
      {/* Performance overlay */}
      <div className="absolute top-2 left-2 bg-black/50 backdrop-blur-sm rounded px-2 py-1 text-xs text-white z-10">
        <div>{isGPUEnabled ? 'GPU' : 'CPU'} Particles: {isGPUEnabled ? particleCount : Math.round(particleCount / 10)}</div>
        <div>FPS: {fps}</div>
      </div>
    </div>
  );
};

export default GPUParticles;