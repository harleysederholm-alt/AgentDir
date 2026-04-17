import { Canvas, useFrame, type ThreeEvent } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import type { AppState } from "../lib/types";

interface Props {
  appState: AppState;
}

/**
 * Event-driven Achii mascot. Strict rules:
 *  - No infinite animation loops. Every `useFrame` tick damps toward a target;
 *    when the target is reached, the lerp is a no-op.
 *  - Visual signals are keyed off `appState` (IDLE / PROCESSING / ERROR / SUCCESS).
 *  - Head rotation pehmeästi seuraa kursorin (state.mouse) sijaintia.
 */
export function AchiiCanvas({ appState }: Props) {
  return (
    <div className="h-full w-full rounded-lg border border-panel_oxidized/50 bg-base_bg/70 shadow-panel backdrop-blur-md">
      <Canvas
        dpr={[1, 2]}
        camera={{ position: [0, 0.2, 3.2], fov: 40 }}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={["#0F0F0F"]} />
        <ambientLight intensity={0.35} />
        <directionalLight position={[3, 4, 5]} intensity={0.9} color="#F39C12" />
        <directionalLight position={[-4, -2, 2]} intensity={0.45} color="#2C3E50" />
        <AchiiRig appState={appState} />
      </Canvas>
    </div>
  );
}

const EYE_COLOR: Record<AppState, string> = {
  IDLE: "#F39C12",
  PROCESSING: "#F39C12",
  SUCCESS: "#4ADE80",
  ERROR: "#EF4444",
};

const EYE_INTENSITY: Record<AppState, number> = {
  IDLE: 0.6,
  PROCESSING: 1.6,
  SUCCESS: 1.3,
  ERROR: 2.2,
};

function AchiiRig({ appState }: Props) {
  const headRef = useRef<THREE.Group>(null);
  const bodyRef = useRef<THREE.Mesh>(null);
  const leftEyeRef = useRef<THREE.MeshStandardMaterial>(null);
  const rightEyeRef = useRef<THREE.MeshStandardMaterial>(null);
  const wrenchRef = useRef<THREE.Group>(null);

  // Event-driven animation "recipe" — an array of keyframes that run once per
  // state change and then settle. No infinite loops.
  const [recipe, setRecipe] = useState<{ kind: "idle" | "tap" | "point" | "nod"; t0: number }>(
    { kind: "idle", t0: performance.now() },
  );

  useEffect(() => {
    const now = performance.now();
    if (appState === "PROCESSING") setRecipe({ kind: "tap", t0: now });
    else if (appState === "ERROR") setRecipe({ kind: "point", t0: now });
    else if (appState === "SUCCESS") setRecipe({ kind: "nod", t0: now });
    else setRecipe({ kind: "idle", t0: now });
  }, [appState]);

  // Hover interaktio — kun kursori viipyy maskotin päällä, pää "kurkkii" hiukan
  // enemmän. Ei omaa loop, vain state flag.
  const [hovered, setHovered] = useState(false);
  const onEnter = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(true);
  };
  const onLeave = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(false);
  };

  useFrame((state, delta) => {
    if (!headRef.current || !bodyRef.current) return;

    // --- Procedural LookAt ---
    const targetYaw = THREE.MathUtils.clamp(state.pointer.x * 0.5, -0.45, 0.45);
    const targetPitch = THREE.MathUtils.clamp(-state.pointer.y * 0.35, -0.3, 0.3);
    const damp = hovered ? 8 : 4;
    headRef.current.rotation.y = THREE.MathUtils.damp(
      headRef.current.rotation.y,
      targetYaw,
      damp,
      delta,
    );
    headRef.current.rotation.x = THREE.MathUtils.damp(
      headRef.current.rotation.x,
      targetPitch,
      damp,
      delta,
    );

    // --- Event-driven recipe playhead (capped, event-driven — ei loputon). ---
    const elapsed = (performance.now() - recipe.t0) / 1000;

    let targetBodyTilt = 0;
    let targetWrenchRot = 0;
    let targetArmLift = 0;

    if (recipe.kind === "tap" && elapsed < 1.2) {
      // Yksi nopea koputus, keston jälkeen jämäkkä paluu lepotilaan.
      targetWrenchRot = Math.sin(elapsed * Math.PI * 2) * 0.6;
      targetBodyTilt = 0.08;
    } else if (recipe.kind === "point" && elapsed < 2.0) {
      // Osoita hälytysnuoli ylös-oikealle — tällä hetkellä tilasta kiinni
      // kunnes state palaa IDLE-tilaan.
      targetArmLift = 1.0;
      targetBodyTilt = -0.05;
    } else if (recipe.kind === "nod" && elapsed < 0.9) {
      // Lyhyt nyökkäys.
      targetBodyTilt = Math.sin(elapsed * Math.PI) * 0.18;
    }

    bodyRef.current.rotation.x = THREE.MathUtils.damp(
      bodyRef.current.rotation.x,
      targetBodyTilt,
      6,
      delta,
    );
    if (wrenchRef.current) {
      wrenchRef.current.rotation.z = THREE.MathUtils.damp(
        wrenchRef.current.rotation.z,
        targetWrenchRot,
        10,
        delta,
      );
      wrenchRef.current.position.y = THREE.MathUtils.damp(
        wrenchRef.current.position.y,
        targetArmLift * 0.3 + -0.05,
        6,
        delta,
      );
    }

    // --- Eye material — drive emissive on state change only. ---
    const color = new THREE.Color(EYE_COLOR[appState]);
    const intensity = EYE_INTENSITY[appState];
    if (leftEyeRef.current) {
      leftEyeRef.current.emissive.lerp(color, 0.25);
      leftEyeRef.current.emissiveIntensity = THREE.MathUtils.damp(
        leftEyeRef.current.emissiveIntensity,
        intensity,
        8,
        delta,
      );
    }
    if (rightEyeRef.current) {
      rightEyeRef.current.emissive.lerp(color, 0.25);
      rightEyeRef.current.emissiveIntensity = THREE.MathUtils.damp(
        rightEyeRef.current.emissiveIntensity,
        intensity,
        8,
        delta,
      );
    }
  });

  const metalBody = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#2C3E50",
        metalness: 0.85,
        roughness: 0.32,
      }),
    [],
  );

  const copperAccent = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#D35400",
        metalness: 0.75,
        roughness: 0.45,
      }),
    [],
  );

  return (
    <group position={[0, -0.2, 0]} onPointerOver={onEnter} onPointerOut={onLeave}>
      {/* Body — oxidized metal torso */}
      <mesh
        ref={bodyRef}
        position={[0, -0.5, 0]}
        material={metalBody}
        castShadow
        receiveShadow
      >
        <capsuleGeometry args={[0.55, 0.9, 6, 14]} />
      </mesh>

      {/* Copper belt — premium reveal */}
      <mesh position={[0, -0.15, 0]} material={copperAccent}>
        <torusGeometry args={[0.58, 0.04, 16, 48]} />
      </mesh>

      {/* Head rig */}
      <group ref={headRef} position={[0, 0.55, 0]}>
        <mesh material={metalBody}>
          <sphereGeometry args={[0.5, 32, 32]} />
        </mesh>
        {/* Eyes */}
        <mesh position={[-0.18, 0.05, 0.45]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial
            ref={leftEyeRef}
            color="#0F0F0F"
            emissive={"#F39C12"}
            emissiveIntensity={0.6}
            roughness={0.2}
          />
        </mesh>
        <mesh position={[0.18, 0.05, 0.45]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial
            ref={rightEyeRef}
            color="#0F0F0F"
            emissive={"#F39C12"}
            emissiveIntensity={0.6}
            roughness={0.2}
          />
        </mesh>
        {/* Antenna */}
        <mesh position={[0, 0.6, 0]} material={copperAccent}>
          <cylinderGeometry args={[0.02, 0.02, 0.3, 8]} />
        </mesh>
        <mesh position={[0, 0.78, 0]} material={copperAccent}>
          <sphereGeometry args={[0.06, 12, 12]} />
        </mesh>
      </group>

      {/* Right arm + wrench — tap animation target */}
      <group ref={wrenchRef} position={[0.55, -0.25, 0.2]}>
        <mesh material={metalBody} position={[0, -0.2, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.4, 10]} />
        </mesh>
        <mesh material={copperAccent} position={[0, -0.42, 0]}>
          <boxGeometry args={[0.08, 0.16, 0.08]} />
        </mesh>
      </group>

      {/* Left arm — static */}
      <mesh material={metalBody} position={[-0.55, -0.45, 0.1]}>
        <cylinderGeometry args={[0.08, 0.08, 0.55, 10]} />
      </mesh>

      {/* Floor shadow disk */}
      <mesh position={[0, -1.15, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.9, 32]} />
        <meshBasicMaterial color="#000000" transparent opacity={0.35} />
      </mesh>
    </group>
  );
}
