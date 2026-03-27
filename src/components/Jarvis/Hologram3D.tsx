import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom, Noise } from '@react-three/postprocessing';
import { VRButton, ARButton, XR, Controllers, Hands } from '@react-three/xr';

// 🎨 Holographic material with scan lines
const HolographicMaterial = React.forwardRef(({ color = '#00d4ff', intensity = 1.5 }, ref) => {
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  React.useImperativeHandle(ref, () => materialRef.current);

  const uniforms = useMemo(() => ({
    time: { value: 0 },
    color: { value: new THREE.Color(color) },
    intensity: { value: intensity },
    scanLineCount: { value: 50 },
    glitchIntensity: { value: 0.02 },
    opacity: { value: 0.85 }
  }), [color, intensity]);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.elapsedTime;
    }
  });

  const vertexShader = `
    varying vec2 vUv;
    varying vec3 vPosition;
    void main() {
      vUv = uv;
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float time;
    uniform vec3 color;
    uniform float intensity;
    uniform float scanLineCount;
    uniform float glitchIntensity;
    uniform float opacity;
    varying vec2 vUv;
    varying vec3 vPosition;
    
    float random(vec2 st) {
      return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
    }
    
    void main() {
      float scanLine = sin(vUv.y * scanLineCount + time * 2.0) * 0.5 + 0.5;
      scanLine = mix(0.9, 1.0, scanLine);
      
      float glitch = random(vec2(time * 0.1, vUv.y * 100.0)) * glitchIntensity;
      
      float flicker = sin(time * 30.0) * 0.02 + 0.98;
      
      float fade = smoothstep(-1.0, 1.0, vPosition.y + 0.5);
      
      vec3 finalColor = color * scanLine * (1.0 + glitch) * flicker * intensity;
      float finalOpacity = opacity * fade * scanLine;
      
      gl_FragColor = vec4(finalColor, finalOpacity);
    }
  `;

  return (
    <shaderMaterial
      ref={materialRef}
      uniforms={uniforms}
      vertexShader={vertexShader}
      fragmentShader={fragmentShader}
      transparent
      side={THREE.DoubleSide}
      depthWrite={false}
    />
  );
});

// 🔮 Jarvis Core - central holographic sphere
function JarvisCore({ emotion = 'neutral' }: { emotion?: string }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Group>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  const emotionColors = {
    neutral: '#00d4ff',
    happy: '#00ff88',
    thinking: '#ffaa00',
    warning: '#ff4444',
    processing: '#aa00ff'
  };
  
  const color = emotionColors[emotion as keyof typeof emotionColors] || emotionColors.neutral;

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
      
      // Hover effect
      const targetScale = isHovered ? 1.2 : 1;
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 5);
    }
    if (ringRef.current) {
      ringRef.current.rotation.z = state.clock.elapsedTime * 0.2;
      ringRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    }
    if (materialRef.current) {
        const targetIntensity = isHovered ? 2.5 : 1.5;
        materialRef.current.uniforms.intensity.value = THREE.MathUtils.lerp(
            materialRef.current.uniforms.intensity.value,
            targetIntensity,
            delta * 5
        );
    }
  });

  return (
    <group>
      {/* Core sphere */}
      <mesh 
        ref={meshRef}
        onPointerEnter={() => setIsHovered(true)}
        onPointerLeave={() => setIsHovered(false)}
      >
        <sphereGeometry args={[0.5, 32, 32]} />
        <HolographicMaterial ref={materialRef} color={color} intensity={1.5} />
      </mesh>
      
      {/* Rotating rings */}
      <group ref={ringRef}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.8, 0.02, 16, 100]} />
          <HolographicMaterial color={color} intensity={1} />
        </mesh>
        <mesh rotation={[0, Math.PI / 2, 0]}>
          <torusGeometry args={[1.0, 0.015, 16, 100]} />
          <HolographicMaterial color={color} intensity={0.8} />
        </mesh>
        <mesh rotation={[Math.PI / 4, 0, 0]}>
          <torusGeometry args={[1.2, 0.01, 16, 100]} />
          <HolographicMaterial color={color} intensity={0.6} />
        </mesh>
      </group>
      
      {/* Energy particles */}
      <Sparkles
        count={100}
        scale={3}
        size={3}
        speed={0.5}
        color={color}
      />
    </group>
  );
}

// ... (HologramWave and DataRings can remain the same)

// 🎭 Main Hologram Scene
function HologramScene({ emotion = 'neutral' }: { emotion?: string }) {
  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#00d4ff" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#ff00aa" />
      
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <JarvisCore emotion={emotion} />
      </Float>
      
      <HologramWave />
      <DataRings />
      
      <OrbitControls 
        enableZoom={false} 
        autoRotate 
        autoRotateSpeed={0.5}
        maxPolarAngle={Math.PI / 2}
      />
      
      <EffectComposer>
        <Bloom 
          intensity={1.5} 
          width={300} 
          height={300} 
          kernelSize={5}
          luminanceThreshold={0.1}
          luminanceSmoothing={0.9}
        />
        <Noise opacity={0.05} />
      </EffectComposer>

      <Hands />
      <Controllers />
    </>
  );
}

// 🖼️ Main Component
export function JarvisHologram3D({ 
  emotion = 'neutral',
  width = '100%',
  height = '400px',
  enableVR = false,
  enableAR = false
}: { 
  emotion?: string;
  width?: string;
  height?: string;
  enableVR?: boolean;
  enableAR?: boolean;
}) {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <div style={{ width, height, position: 'relative', background: 'radial-gradient(circle at center, #001122 0%, #000000 100%)' }}>
      {enableVR && <VRButton />}
      {enableAR && <ARButton />}
      {isLoading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#00d4ff',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          Initializing hologram...
        </div>
      )}
      
      <Canvas
        camera={{ position: [0, 0, 4], fov: 45 }}
        onCreated={() => setIsLoading(false)}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        <XR>
          <HologramScene emotion={emotion} />
        </XR>
      </Canvas>
      
      {/* ... (overlay effects can remain the same) */}
    </div>
  );
}
