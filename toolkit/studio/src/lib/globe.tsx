import { useThree } from "@react-three/fiber";
import { geoInterpolate } from "d3-geo";
import { useEffect, useMemo, useState } from "react";
import { cancelRender, continueRender, delayRender, staticFile } from "remotion";
import * as THREE from "three";
import { COLORS, THEME } from "../brand/tokens";

export type LonLat = readonly [number, number];

// three.js SphereGeometry puts u = 0 (longitude -180) on the -X axis, so an
// equirectangular texture lines up with this mapping.
export const toVec = ([lon, lat]: LonLat, r = 1): THREE.Vector3 => {
  const phi = ((lon + 180) * Math.PI) / 180;
  const la = (lat * Math.PI) / 180;
  return new THREE.Vector3(
    -Math.cos(phi) * Math.cos(la) * r,
    Math.sin(la) * r,
    Math.sin(phi) * Math.cos(la) * r,
  );
};

export type Loaded = { tex: THREE.Texture | null; handle: number };

// Loads a texture and holds the frame until <DrawTextures> inside the canvas
// has drawn it: while rendering, R3F draws only when Remotion's frame
// changes, so a texture that arrives later would never reach the canvas and
// the frame would show the atmosphere with no planet.
export const useTexture = (file: string, linear = false): Loaded => {
  const [handle] = useState(() => delayRender(`texture ${file}`));
  const [tex, setTex] = useState<THREE.Texture | null>(null);
  useEffect(() => {
    new THREE.TextureLoader().load(
      staticFile(file),
      (t) => {
        // Colour maps are sRGB; height and roughness maps are data.
        t.colorSpace = linear ? THREE.NoColorSpace : THREE.SRGBColorSpace;
        t.anisotropy = 16;
        setTex(t);
      },
      undefined,
      (err) => cancelRender(err),
    );
  }, [file, handle, linear]);
  return { tex, handle };
};

// Goes inside the canvas, after the meshes that use the textures.
export const DrawTextures: React.FC<{ textures: Loaded[] }> = ({ textures }) => {
  const advance = useThree((s) => s.advance);
  const ready = textures.every((t) => t.tex);
  useEffect(() => {
    if (!ready) return;
    advance(performance.now());
    for (const t of textures) continueRender(t.handle);
    // Runs once, when the last texture arrives.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready]);
  return null;
};

// The orphan scan's stand-in for <DrawTextures>: it reads text layout only,
// so the globe is not drawn and the frame waits just for the loads.
export const ReleaseTextures: React.FC<{ textures: Loaded[] }> = ({ textures }) => {
  const ready = textures.every((t) => t.tex);
  useEffect(() => {
    if (!ready) return;
    for (const t of textures) continueRender(t.handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready]);
  return null;
};

// `tint` multiplies the imagery: below white it darkens the planet so an
// overlay (population, lights) reads on top. `bump` (land relief) and
// `rough` (smooth sea, matte land) give the light themes real depth.
export const Earth: React.FC<{
  texture: THREE.Texture;
  tint?: string;
  bump?: THREE.Texture | null;
  rough?: THREE.Texture | null;
  bumpScale?: number;
  // Scales the roughness map: above 1 widens and softens the sea's glint.
  roughness?: number;
  // Cuts the planet open (see GlobeView's `clip`).
  clip?: THREE.Plane[];
  clipIntersection?: boolean;
  // Below 1 the planet turns to glass, so what is built inside it shows.
  seeThrough?: number;
}> = ({ texture, tint = "#ffffff", bump, rough, bumpScale = 1, roughness = 1, clip, clipIntersection = false, seeThrough = 1 }) => (
  <mesh renderOrder={seeThrough < 1 ? 2 : 0}>
    <sphereGeometry args={[1, 256, 256]} />
    <meshStandardMaterial
      map={texture}
      color={tint}
      bumpMap={bump ?? null}
      bumpScale={bump ? bumpScale : 0}
      roughnessMap={rough ?? null}
      roughness={rough ? roughness : 0.9}
      metalness={0}
      clippingPlanes={clip ?? null}
      clipIntersection={clipIntersection}
      transparent={seeThrough < 1}
      opacity={seeThrough}
      depthWrite={seeThrough >= 1}
    />
  </mesh>
);

// A data layer as light: a greyscale equirectangular mask, added in `color`
// on a shell just above the surface.
// It draws after the limb haze (renderOrder), so data stays clear at the edge.
export const GlowLayer: React.FC<{ mask: THREE.Texture; color: string; opacity: number }> = ({ mask, color, opacity }) => (
  <mesh scale={1.002} renderOrder={2}>
    <sphereGeometry args={[1, 128, 128]} />
    <meshBasicMaterial
      color={color}
      alphaMap={mask}
      transparent
      opacity={opacity}
      blending={THEME.glow === "add" ? THREE.AdditiveBlending : THREE.NormalBlending}
      depthWrite={false}
    />
  </mesh>
);

// Hairlines over the data layers, lit like the land: a mask drawn in `color`
// on a shell just above the glow, e.g. the skin's own borders laid back over
// a data layer that would otherwise cover them.
export const LineLayer: React.FC<{ mask: THREE.Texture; color: string; opacity: number }> = ({ mask, color, opacity }) => (
  <mesh scale={1.003} renderOrder={3}>
    <sphereGeometry args={[1, 128, 128]} />
    <meshStandardMaterial color={color} alphaMap={mask} transparent opacity={opacity} roughness={0.92} metalness={0} depthWrite={false} />
  </mesh>
);

// A back-side fresnel shell reads as atmosphere without a bloom pass, which
// would cost several full-screen passes on the CPU renderer. Used only by a
// theme with no `limb` settings (a dark look).
const atmosphereShader = {
  vertexShader: `
    varying vec3 vNormal;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 glowColor;
    uniform float strength;
    varying vec3 vNormal;
    void main() {
      float i = pow(0.62 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
      gl_FragColor = vec4(glowColor, 1.0) * i * strength;
    }`,
};

// Both light-theme atmosphere shells work out, per pixel, the view ray's
// closest approach `b` to the planet's centre (in planet radii), so the
// look follows the real geometry at any camera distance.
const rayVertex = `
  #include <clipping_planes_pars_vertex>
  varying vec3 vView;
  varying vec3 vCentre;
  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vView = mvPosition.xyz;
    vCentre = (modelViewMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
    gl_Position = projectionMatrix * mvPosition;
    #include <clipping_planes_vertex>
  }`;
const rayCommon = `
  #include <clipping_planes_pars_fragment>
  uniform vec3 lightDir;
  uniform vec3 haze;
  uniform vec3 shade;
  uniform float strength;
  varying vec3 vView;
  varying vec3 vCentre;
  float lit(vec3 n) {
    vec3 l = normalize((viewMatrix * vec4(lightDir, 0.0)).xyz);
    return smoothstep(-0.25, 0.6, dot(n, l));
  }`;

// The sky seen past the planet's edge: density falls off with height as in
// a real atmosphere, brighter on the sunlit limb. Normal blending, so it
// reads as a blue rim on a light page, where additive light would vanish.
const haloShader = {
  vertexShader: rayVertex,
  fragmentShader: `
    ${rayCommon}
    void main() {
      #include <clipping_planes_fragment>
      vec3 d = normalize(vView);
      vec3 p = d * dot(vCentre, d);
      float h = length(p - vCentre) - 1.0;
      if (h < 0.0) discard;
      float k = lit(normalize(p - vCentre));
      float a = exp(-h / 0.011) * mix(0.18, 1.0, k) * strength;
      gl_FragColor = vec4(haze, a);
    }`,
};

// The atmosphere seen against the planet: the path through a thin shell
// lengthens toward the edge, so the limb gathers a blue haze on the lit side
// and a cool shadow on the far side. This is what gives a sphere its edge.
const limbShader = {
  vertexShader: rayVertex,
  fragmentShader: `
    ${rayCommon}
    uniform float shadeStrength;
    void main() {
      #include <clipping_planes_fragment>
      vec3 d = normalize(vView);
      float t = dot(vCentre, d);
      float b2 = dot(vCentre, vCentre) - t * t;
      const float T = 0.06;
      float path = sqrt(max((1.0 + T) * (1.0 + T) - b2, 0.0)) - sqrt(max(1.0 - b2, 0.0));
      float o = clamp(path / sqrt(2.0 * T + T * T), 0.0, 1.0);
      vec3 hit = d * (t - sqrt(max(1.0 - b2, 0.0)));
      float k = lit(normalize(hit - vCentre));
      vec3 c = mix(shade, haze, k);
      float a = pow(o, 2.4) * mix(shadeStrength, strength, k);
      gl_FragColor = vec4(c, a);
    }`,
};

// A thin, desaturated limb glow, as on a photograph from orbit; the earlier
// saturated cyan halo read as a CG render.
export const Atmosphere: React.FC<{
  color?: string;
  strength?: number;
  lightDir?: THREE.Vector3;
  // The planet's cut (GlobeView's `clip`): the haze over the surface is cut
  // with it, so none hangs over an opening.
  clip?: THREE.Plane[];
  clipIntersection?: boolean;
}> = ({ color = THEME.globe.atmosphere, strength = THEME.globe.atmosphereStrength, lightDir, clip, clipIntersection = false }) => {
  const limb = THEME.globe.limb;
  const uniforms = useMemo(
    () => ({
      glowColor: { value: new THREE.Color(color) },
      strength: { value: strength },
      haze: { value: new THREE.Color(limb?.haze ?? color) },
      shade: { value: new THREE.Color(limb?.shade ?? "#000000") },
      shadeStrength: { value: limb?.shadeStrength ?? 0 },
      lightDir: { value: (lightDir ?? new THREE.Vector3(0, 0, 1)).clone().normalize() },
    }),
    [color, strength, limb, lightDir],
  );
  if (limb) {
    return (
      <>
        <mesh scale={1.001} renderOrder={1}>
          <sphereGeometry args={[1, 256, 256]} />
          <shaderMaterial
            args={[{ ...limbShader, uniforms: { ...uniforms, strength: { value: limb.limbStrength } } }]}
            transparent
            depthWrite={false}
            clipping
            clippingPlanes={clip ?? null}
            clipIntersection={clipIntersection}
          />
        </mesh>
        <mesh scale={1.08} renderOrder={3}>
          <sphereGeometry args={[1, 128, 128]} />
          <shaderMaterial
            args={[{ ...haloShader, uniforms: { ...uniforms, strength: { value: limb.haloStrength } } }]}
            side={THREE.BackSide}
            transparent
            depthWrite={false}
            clipping
            clippingPlanes={clip ?? null}
            clipIntersection={clipIntersection}
          />
        </mesh>
      </>
    );
  }
  return (
    <mesh scale={1.07}>
      <sphereGeometry args={[1, 64, 64]} />
      <shaderMaterial
        args={[{ ...atmosphereShader, uniforms }]}
        side={THREE.BackSide}
        blending={THREE.AdditiveBlending}
        transparent
        depthWrite={false}
      />
    </mesh>
  );
};

// The great circle between two points, lifted off the surface by a sine of
// progress so it reads as a flight, drawn on up to `progress` (0..1). It is
// an unlit tube built in the scene, with a light casing behind it as
// printed maps case their roads, and a bright head; no glow.
export const GreatCircleArc: React.FC<{
  from: LonLat;
  to: LonLat;
  progress: number;
  color: string;
  lift?: number;
  radius?: number;
}> = ({ from, to, progress, color, lift = 0.08, radius = 0.006 }) => {
  const curve = useMemo(() => {
    const interp = geoInterpolate(from as [number, number], to as [number, number]);
    const pts: THREE.Vector3[] = [];
    const n = 160;
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      pts.push(toVec(interp(t) as LonLat, 1.002 + lift * Math.sin(Math.PI * t)));
    }
    return pts;
  }, [from, to, lift]);
  const visible = Math.max(2, Math.round(curve.length * Math.min(1, progress)));
  const geo = useMemo(() => {
    if (progress <= 0) return null;
    const path = new THREE.CatmullRomCurve3(curve.slice(0, visible));
    return {
      core: new THREE.TubeGeometry(path, visible * 2, radius, 12, false),
      halo: new THREE.TubeGeometry(path, visible * 2, radius * 1.9, 12, false),
      head: curve[visible - 1],
    };
  }, [curve, visible, radius, progress]);
  if (!geo) return null;
  return (
    <group>
      <mesh geometry={geo.halo}>
        <meshBasicMaterial color={COLORS.mark} transparent opacity={0.85} depthWrite={false} />
      </mesh>
      <mesh geometry={geo.core}>
        <meshBasicMaterial color={color} />
      </mesh>
      <mesh position={geo.head}>
        <sphereGeometry args={[radius * 3, 16, 16]} />
        <meshBasicMaterial color={COLORS.mark} />
      </mesh>
    </group>
  );
};

// Points the camera at a look-at direction on the globe from a distance.
// `shiftY` moves the picture that many pixels down by offsetting the view,
// so the whole frame is still drawn.
export const CameraRig: React.FC<{
  target: THREE.Vector3;
  distance: number;
  up?: readonly [number, number, number];
  shiftY?: number;
}> = ({ target, distance, up, shiftY = 0 }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const size = useThree((s) => s.size);
  const pos = target.clone().normalize().multiplyScalar(distance);
  camera.position.copy(pos);
  camera.up.set(...(up ?? ([0, 1, 0] as const)));
  camera.lookAt(0, 0, 0);
  if (shiftY) camera.setViewOffset(size.width, size.height, 0, -shiftY, size.width, size.height);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
  return null;
};
