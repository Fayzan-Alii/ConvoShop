import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Box, Sphere, Text, Float, MeshDistortMaterial, MeshWobbleMaterial } from '@react-three/drei';
import * as THREE from 'three';

export function FloatingDevice() {
  const sceneRef = useRef<THREE.Group>(null);
  const bubbleRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!sceneRef.current) return;
    
    // Gentle rotation for the entire scene
    sceneRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.1;
    
    // Bubble animation
    if (bubbleRef.current) {
      bubbleRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.2;
      bubbleRef.current.rotation.z = state.clock.elapsedTime * 0.1;
    }
  });

  const shoppingItems = [
    { position: [-2, 1, 0], scale: 0.4, color: '#EC4899' },
    { position: [2, -1, 1], scale: 0.3, color: '#8B5CF6' },
    { position: [-1, -2, -1], scale: 0.5, color: '#6366F1' },
    { position: [1.5, 2, -0.5], scale: 0.35, color: '#F43F5E' },
  ];

  const chatBubbles = [
    { position: [0, 1.5, -1], scale: 0.8 },
    { position: [-1.5, -0.5, -0.5], scale: 0.6 },
    { position: [1, -1, -1], scale: 0.7 },
  ];

  return (
    <group ref={sceneRef}>
      {/* Background atmosphere */}
      <mesh position={[0, 0, -4]} scale={8}>
        <sphereGeometry args={[1, 32, 32]} />
        <MeshDistortMaterial
          color="#4F46E5"
          speed={0.5}
          distort={0.3}
          radius={1}
          opacity={0.1}
          transparent
        />
      </mesh>

      {/* Shopping items */}
      {shoppingItems.map((item, index) => (
        <Float
          key={index}
          speed={(1 + index * 0.2)}
          rotationIntensity={1}
          floatIntensity={2}
          position={item.position}
        >
          <Box args={[1, 1, 1]} scale={item.scale}>
            <MeshWobbleMaterial
              color={item.color}
              factor={0.3}
              speed={1}
              metalness={0.8}
              roughness={0.2}
            />
          </Box>
        </Float>
      ))}

      {/* Chat bubbles */}
      {chatBubbles.map((bubble, index) => (
        <Float
          key={`bubble-${index}`}
          speed={1}
          rotationIntensity={1}
          floatIntensity={1.5}
          position={bubble.position}
        >
          <group scale={bubble.scale}>
            <mesh>
              <sphereGeometry args={[0.5, 32, 32]} />
              <meshPhongMaterial
                color="#FFFFFF"
                opacity={0.6}
                transparent
                shininess={100}
              />
            </mesh>
            <Text
              position={[0, 0, 0.2]}
              fontSize={0.2}
              color="#4F46E5"
              anchorX="center"
              anchorY="middle"
            >
              {index % 2 === 0 ? '?' : '!'}
            </Text>
          </group>
        </Float>
      ))}

      {/* Central connecting lines */}
      {shoppingItems.map((item, index) => (
        <group key={`line-${index}`}>
          <mesh>
            <cylinderGeometry args={[0.02, 0.02, 4, 8]} />
            <meshPhongMaterial
              color="#6366F1"
              opacity={0.2}
              transparent
              metalness={1}
            />
          </mesh>
        </group>
      ))}

      {/* Central sphere (representing AI hub) */}
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <Sphere args={[0.8, 32, 32]}>
          <MeshDistortMaterial
            color="#4F46E5"
            speed={2}
            distort={0.4}
            radius={1}
            metalness={0.8}
            roughness={0.2}
          />
        </Sphere>
      </Float>
    </group>
  );
}