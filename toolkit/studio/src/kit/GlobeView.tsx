import { ThreeCanvas } from "@remotion/three";
import { geoInterpolate, geoPath, geoProjection } from "d3-geo";
import { AbsoluteFill, getInputProps, useVideoConfig } from "remotion";
import * as THREE from "three";
import { THEME } from "../brand/tokens";
import { Atmosphere, CameraRig, DrawTextures, Earth, GlowLayer, LineLayer, ReleaseTextures, toVec, useTexture } from "../lib/globe";
import type { LonLat } from "./MapView";

// `up` is the world direction that should point up on screen; it defaults to
// the north axis (+Y). Set it to roll the view, e.g. to lay a route level.
export type GlobeCam = { lon: number; lat: number; distance: number; up?: readonly [number, number, number] };
// `radius` above 1 lifts the point off the surface (1 = Earth's radius), e.g.
// an orbit; it is hidden only where the planet is in the way.
export type GlobeProject = (p: LonLat, radius?: number) => { x: number; y: number; visible: boolean };

const FOV = 30;

// Camera basis exactly as three.js builds it for lookAt(0,0,0) with up +Y.
const basis = (cam: GlobeCam) => {
  const c = toVec([cam.lon, cam.lat], cam.distance);
  const f = c.clone().negate().normalize();
  const up = cam.up ? new THREE.Vector3(...cam.up) : new THREE.Vector3(0, 1, 0);
  const r = new THREE.Vector3().crossVectors(f, up).normalize();
  const u = new THREE.Vector3().crossVectors(r, f);
  return { c, f, r, u };
};

// The key light: from the camera's upper left, so the visible face is
// always lit. Objects in `scene` that shade themselves use the same one.
export const keyLight = (cam: GlobeCam) => {
  const { c, r, u } = basis(cam);
  return c.clone().add(r.clone().multiplyScalar(-3)).add(u.clone().multiplyScalar(2.5));
};

// Lon/lat to screen pixels through the same perspective camera the globe
// uses, so SVG overlays sit exactly on the rendered sphere.
// `shiftY` puts the planet's centre that far below the frame's centre.
export const makeGlobeProject = (cam: GlobeCam, width: number, height: number, shiftY = 0): GlobeProject => {
  const { c, f, r, u } = basis(cam);
  const focal = height / 2 / Math.tan((FOV * Math.PI) / 360);
  const chat = c.clone().normalize();
  return (p, radius = 1) => {
    const v3 = toVec(p, radius);
    const d = v3.clone().sub(c);
    const z = d.dot(f);
    let visible: boolean;
    if (radius <= 1) visible = v3.dot(chat) > 1 / cam.distance + 0.002;
    else {
      // The sight line c + t*d (t in 0..1) must miss the unit sphere.
      const a = d.dot(d);
      const b = 2 * c.dot(d);
      const disc = b * b - 4 * a * (c.dot(c) - 1);
      visible = disc < 0 || (-b - Math.sqrt(disc)) / (2 * a) > 1;
    }
    return {
      x: width / 2 + (d.dot(r) / z) * focal,
      y: height / 2 + shiftY - (d.dot(u) / z) * focal,
      visible,
    };
  };
};

// Filled shapes on the globe: a d3 path through the same perspective camera
// (the vertical perspective, or satellite, projection from cam.distance
// radii), clipped at the horizon the camera sees, so a polygon that runs
// over the edge stays one closed fill. Rolled cameras (cam.up) are not
// supported: their overlays would not line up.
const perspectiveRaw = (P: number) => (lambda: number, phi: number): [number, number] => {
  const cp = Math.cos(phi);
  const k = (P - 1) / (P - cp * Math.cos(lambda));
  return [k * cp * Math.sin(lambda), k * Math.sin(phi)];
};
export const makeGlobePath = (cam: GlobeCam, width: number, height: number, shiftY = 0) => {
  const focal = height / 2 / Math.tan((FOV * Math.PI) / 360);
  const d = cam.distance;
  const projection = geoProjection(perspectiveRaw(d))
    .scale(focal / (d - 1))
    .translate([width / 2, height / 2 + shiftY])
    .rotate([-cam.lon, -cam.lat, 0])
    .clipAngle((Math.acos(1 / d) * 180) / Math.PI - 0.05)
    .precision(0.4);
  return geoPath(projection);
};

// Interpolates a camera between two views along the great circle joining
// their look-at points; distance is eased separately by the caller (in log
// space, so a move out and in reads as one smooth pull).
export const lerpCam = (a: GlobeCam, b: GlobeCam, t: number, distance?: number): GlobeCam => {
  const [lon, lat] = geoInterpolate([a.lon, a.lat], [b.lon, b.lat])(t);
  const ua = new THREE.Vector3(...(a.up ?? [0, 1, 0]));
  const ub = new THREE.Vector3(...(b.up ?? [0, 1, 0]));
  const u = ua.lerp(ub, t).normalize();
  return { lon, lat, distance: distance ?? a.distance + (b.distance - a.distance) * t, up: [u.x, u.y, u.z] };
};

// QA only: the orphan scan (input prop `orphans`) reads text layout, not
// the planet, so it skips the 3D drawing, nearly all of a frame's time on
// SwiftShader. The overlays still get the same projection.
const TEXT_ONLY = Boolean((getInputProps() as { orphans?: boolean }).orphans);

export const GlobeView: React.FC<{
  cam: GlobeCam;
  texture?: string;
  opacity?: number;
  // Moves the globe and its overlays together on screen, e.g. up and clear
  // of the captions. The camera's view is offset rather than the layer
  // moved, so a planet bigger than the frame still reaches its top edge
  // (moving the layer once cut the planet with a straight edge near the top
  // in every close-up).
  shiftY?: number;
  tint?: string;
  // A greyscale mask in public/ drawn as light over the surface.
  glow?: { mask: string; color: string; opacity: number };
  // A greyscale mask in public/ drawn as fine lines above the glow, e.g.
  // borders.
  lines?: { mask: string; color: string; opacity: number };
  children?: (project: GlobeProject) => React.ReactNode;
  // Objects built in the 3D scene itself (a shaft through the planet, its
  // cut-away interior: kit/CutAway3D.tsx), lit by the same light as the
  // planet. Anything that stands for a 3D thing goes here, never in the 2D
  // overlay.
  scene?: React.ReactNode;
  // Planes that cut the planet open (three.js clipping): with
  // `clipIntersection` only what lies behind every plane is removed, e.g. a
  // wedge between two planes.
  clip?: THREE.Plane[];
  clipIntersection?: boolean;
  // Below 1 the planet turns to glass, so what is built inside it shows.
  seeThrough?: number;
}> = ({ cam, texture = THEME.globe.texture, opacity = 1, shiftY = 0, tint = THEME.globe.tint, glow, lines, children, scene, clip, clipIntersection = false, seeThrough = 1 }) => {
  const { width, height } = useVideoConfig();
  const earth = useTexture(texture);
  const glowMap = useTexture(glow?.mask ?? texture);
  const bump = useTexture(THEME.globe.bump ?? texture, true);
  const rough = useTexture(THEME.globe.rough ?? texture, true);
  const lineMap = useTexture(lines?.mask ?? texture, true);
  const tex = earth.tex;
  const glowTex = glowMap.tex;
  const light = keyLight(cam);
  const target = toVec([cam.lon, cam.lat]);
  return (
    <AbsoluteFill style={{ opacity }}>
      {THEME.globe.shadow ? <ContactShadow cam={cam} width={width} height={height} shiftY={shiftY} /> : null}
      {TEXT_ONLY ? (
        <ReleaseTextures textures={[earth, glowMap, bump, rough, lineMap]} />
      ) : (
      <ThreeCanvas
        width={width}
        height={height}
        camera={{ fov: FOV, near: 0.05, far: 100 }}
        // Light themes keep the palette's colours: neutral tone mapping, not
        // ACES, which pulled the pale sea toward grey.
        onCreated={(st) => {
          st.gl.toneMapping = THEME.light ? THREE.NeutralToneMapping : THREE.ACESFilmicToneMapping;
          st.gl.toneMappingExposure = THEME.globe.exposure ?? 1;
          st.gl.localClippingEnabled = true;
        }}
      >
        <ambientLight intensity={THEME.globe.ambient} />
        {THEME.globe.sky ? <hemisphereLight args={[...(THEME.globe.skyColors ?? ["#ffffff", "#C9D6DA"]), THEME.globe.sky]} /> : null}
        <directionalLight position={[light.x, light.y, light.z]} intensity={THEME.globe.key} />
        <CameraRig target={target} distance={cam.distance} up={cam.up} shiftY={shiftY} />
        {tex ? (
          <Earth
            texture={tex}
            tint={tint}
            bump={THEME.globe.bump ? bump.tex : null}
            rough={THEME.globe.rough ? rough.tex : null}
            bumpScale={THEME.globe.bumpScale}
            roughness={THEME.globe.roughness}
            clip={clip}
            clipIntersection={clipIntersection}
            seeThrough={seeThrough}
          />
        ) : null}
        {glow && glowTex && glow.opacity > 0 ? <GlowLayer mask={glowTex} color={glow.color} opacity={glow.opacity} /> : null}
        {lines && lineMap.tex && lines.opacity > 0 ? <LineLayer mask={lineMap.tex} color={lines.color} opacity={lines.opacity} /> : null}
        <Atmosphere lightDir={light} clip={clip} clipIntersection={clipIntersection} />
        {scene}
        <DrawTextures textures={[earth, glowMap, bump, rough, lineMap]} />
      </ThreeCanvas>
      )}
      {children ? children(makeGlobeProject(cam, width, height, shiftY)) : null}
    </AbsoluteFill>
  );
};

// A soft shadow on the page under the planet, so it sits on the paper like
// an object rather than floating as a cut-out.
const ContactShadow: React.FC<{ cam: GlobeCam; width: number; height: number; shiftY: number }> = ({ cam, width, height, shiftY }) => {
  const focal = height / 2 / Math.tan((FOV * Math.PI) / 360);
  const R = focal * Math.tan(Math.asin(1 / cam.distance));
  const cy = height / 2 + shiftY + R * 0.96;
  return (
    <div
      style={{
        position: "absolute",
        left: width / 2 - R * 0.95,
        top: cy - R * 0.12,
        width: R * 1.9,
        height: R * 0.24,
        borderRadius: "50%",
        background: "radial-gradient(ellipse at center, rgba(18,42,49,0.22) 0%, rgba(18,42,49,0.08) 45%, rgba(18,42,49,0) 72%)",
        filter: "blur(14px)",
      }}
    />
  );
};

// Splits projected points into visible runs and returns an SVG path string.
export const pathOnGlobe = (pts: LonLat[], project: GlobeProject, radius = 1): string => {
  let d = "";
  let pen = false;
  for (const p of pts) {
    const q = project(p, radius);
    if (!q.visible) {
      pen = false;
      continue;
    }
    d += `${pen ? "L" : "M"}${q.x.toFixed(1)},${q.y.toFixed(1)}`;
    pen = true;
  }
  return d;
};
