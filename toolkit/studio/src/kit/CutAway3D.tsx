import { useMemo } from "react";
import * as THREE from "three";
import { COLORS } from "../brand/tokens";
import { toVec, type LonLat } from "../lib/globe";

// A cut-away 3D object: the pattern for showing the inside of something
// solid (a planet, a building, an engine) in the house style. Everything
// is built in the 3D scene and lit by the scene's own key light, never drawn
// as a flat stroke over the render, which has no depth and looks strange.
// The example here is a shaft drilled straight through a planet: the planet
// cut open along the shaft so its layers show, and the shaft a lit tube.
// Where the shaft meets the surface is a place, not a solid: mark it with a
// 2D dot sized for the view, never a modelled hole (see lib/viewScale.ts).
//
// The design rules the pattern encodes, each learned frame by frame:
// - The cut is fixed to the object, not to the camera: as the object turns,
//   the cut turns with it, as a real cut would.
// - The opening is turned off square to the camera (`wedge`'s `turn`, about
//   0.6 rad), so one face is seen broad and the other foreshortened, which
//   reads as depth; square on, a wedge reads as a flat petal.
// - The cut is shut before the camera turns, never during the turn. Shut
//   while the camera turned, the broad face swept the planet as a band,
//   the page showed through the wedge, and a sliver of shaft showed through
//   the closing seam. Close it fast, ending as the turn starts.
// - A label tied to the cut ("the centre") leaves before the cut shuts, or
//   it is left floating over the surface.
// - The layer radii come from a cited model (below) and are logged as
//   facts when any is said or labelled.
// - Each piece has its own design pass: shape, light, material, edges and
//   motion. Seams between layers are a pixel wide at any distance, the
//   faces take the key light so two faces of a wedge differ, the fold
//   carries a little shade, and the shaft fades out above the captions in
//   screen space so it never crosses them in any camera move.
// - Rejected on the way here, so not offered: flat "petals" (a wedge square
//   on), a hairline shaft, a ring that read as a button for the way out,
//   and a see-through planet whose core showed as a grey sphere.

// The interior: the Earth's layers by radius, in planet radii (the
// Preliminary Reference Earth Model, PREM, 1981; radius 6,371 km): inner
// core 1,221.5 km, outer core 3,480 km, the 660 km discontinuity between
// lower and upper mantle, and the crust, drawn 51 km thick (continental
// crust runs 30 to 70 km). Log the figures in the episode's verification
// log if any is said or labelled. For another object, change the radii and
// colours: the shader draws concentric bands.
export const LAYERS = {
  innerCore: 1221.5 / 6371,
  outerCore: 3480 / 6371,
  lowerMantle: (6371 - 660) / 6371,
  crust: 1 - 51 / 6371,
};

// Warm and restrained, lightest at the centre, so the vermilion shaft reads
// on every layer and nothing competes with it.
const LAYER_COLORS = {
  crust: "#8C6B52",
  upperMantle: "#E8A57A",
  lowerMantleOut: "#EDAF7F",
  lowerMantleIn: "#F3C48C",
  outerCoreOut: "#F7CF86",
  outerCoreIn: "#FADD9C",
  innerCore: "#FFF3D2",
  edge: "#C98A60",
};

const sectionShader = {
  vertexShader: `
    #include <clipping_planes_pars_vertex>
    varying vec3 vWorld;
    void main() {
      vec4 w = modelMatrix * vec4(position, 1.0);
      vWorld = w.xyz;
      vec4 mvPosition = viewMatrix * w;
      gl_Position = projectionMatrix * mvPosition;
      #include <clipping_planes_vertex>
    }`,
  fragmentShader: `
    #include <clipping_planes_pars_fragment>
    uniform vec3 cCrust, cUpper, cLowerOut, cLowerIn, cOuterOut, cOuterIn, cInner, cEdge;
    uniform float rInner, rOuter, rLower, rCrust;
    uniform vec3 normalW, lightDir, axis;
    uniform float ambient, opacity;
    varying vec3 vWorld;
    // A soft line where two layers meet, a pixel or so wide at any distance.
    float seam(float r, float at) {
      float w = fwidth(r) * 1.2;
      return 1.0 - smoothstep(0.0, w, abs(r - at));
    }
    void main() {
      #include <clipping_planes_fragment>
      float r = length(vWorld);
      if (r > 1.0) discard;
      vec3 c;
      if (r < rInner) c = cInner;
      else if (r < rOuter) c = mix(cOuterIn, cOuterOut, (r - rInner) / (rOuter - rInner));
      else if (r < rLower) c = mix(cLowerIn, cLowerOut, (r - rOuter) / (rLower - rOuter));
      else if (r < rCrust) c = cUpper;
      else c = cCrust;
      // The inner core glows faintly at its heart.
      c = mix(c, vec3(1.0, 0.985, 0.94), 0.35 * (1.0 - smoothstep(0.0, rInner, r)));
      float s = max(max(seam(r, rInner), seam(r, rOuter)), seam(r, rCrust));
      c = mix(c, cEdge, 0.4 * s + 0.18 * seam(r, rLower));
      // Light on the cut face from the scene's key light, so the two faces of
      // a wedge differ as two real faces would.
      vec3 n = normalize(normalW);
      if (dot(n, cameraPosition - vWorld) < 0.0) n = -n;
      float lit = ambient + (1.0 - ambient) * max(dot(n, normalize(lightDir)), 0.0);
      // A little shade along the fold where the faces meet, and at the rim.
      float fromAxis = length(vWorld - axis * dot(vWorld, axis));
      float ao = mix(0.72, 1.0, smoothstep(0.0, 0.12, fromAxis)) * mix(0.88, 1.0, smoothstep(0.0, 0.05, 1.0 - r));
      gl_FragColor = vec4(c * lit * ao, opacity);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
};

// One flat face of the cut: the half disc spanned by the shaft's `axis` and
// the outward direction `out`, both unit vectors through the centre.
export const SectionFace: React.FC<{
  axis: THREE.Vector3;
  out: THREE.Vector3;
  light: THREE.Vector3;
  full?: boolean;
  opacity?: number;
}> = ({ axis, out, light, full = false, opacity = 1 }) => {
  const n = useMemo(() => new THREE.Vector3().crossVectors(out, axis).normalize(), [out, axis]);
  const matrix = useMemo(() => new THREE.Matrix4().makeBasis(out, axis, n), [out, axis, n]);
  const uniforms = useMemo(
    () => ({
      cCrust: { value: new THREE.Color(LAYER_COLORS.crust) },
      cUpper: { value: new THREE.Color(LAYER_COLORS.upperMantle) },
      cLowerOut: { value: new THREE.Color(LAYER_COLORS.lowerMantleOut) },
      cLowerIn: { value: new THREE.Color(LAYER_COLORS.lowerMantleIn) },
      cOuterOut: { value: new THREE.Color(LAYER_COLORS.outerCoreOut) },
      cOuterIn: { value: new THREE.Color(LAYER_COLORS.outerCoreIn) },
      cInner: { value: new THREE.Color(LAYER_COLORS.innerCore) },
      cEdge: { value: new THREE.Color(LAYER_COLORS.edge) },
      rInner: { value: LAYERS.innerCore },
      rOuter: { value: LAYERS.outerCore },
      rLower: { value: LAYERS.lowerMantle },
      rCrust: { value: LAYERS.crust },
      normalW: { value: n },
      lightDir: { value: light.clone().normalize() },
      axis: { value: axis },
      ambient: { value: 0.62 },
      opacity: { value: opacity },
    }),
    [n, light, axis, opacity],
  );
  return (
    <mesh matrixAutoUpdate={false} matrix={matrix} renderOrder={1}>
      {/* Local x = out, y = axis: the half with x >= 0, or the whole disc. */}
      <circleGeometry args={[1, 256, full ? 0 : -Math.PI / 2, full ? Math.PI * 2 : Math.PI]} />
      <shaderMaterial args={[{ ...sectionShader, uniforms }]} side={THREE.DoubleSide} transparent={opacity < 1} />
    </mesh>
  );
};

// A wedge cut along the shaft, opening toward the camera: the two cut
// planes (for GlobeView's `clip`, with clipIntersection) and the directions
// of its two faces. `half` is the half-angle in radians; at PI / 2 the
// wedge is the whole front half (one plane).
// `turn` swings the opening about the shaft away from facing the camera
// square on, so one face is seen broad and the other foreshortened, which
// is what makes a cut read as depth rather than a flat petal.
export const wedge = (axis: THREE.Vector3, camDir: THREE.Vector3, half: number, turn = 0) => {
  const b0 = camDir.clone().sub(axis.clone().multiplyScalar(camDir.dot(axis)));
  if (b0.lengthSq() < 1e-8) b0.set(1, 0, 0).sub(axis.clone().multiplyScalar(axis.x));
  b0.normalize();
  const b = b0.applyAxisAngle(axis, turn).normalize();
  const e = new THREE.Vector3().crossVectors(axis, b).normalize();
  const c = Math.cos(half);
  const s = Math.sin(half);
  // Removed: points whose angle about the axis, measured from b, lies
  // within +-half; each plane's negative side holds one bound.
  const m1 = b.clone().multiplyScalar(-s).add(e.clone().multiplyScalar(c));
  const m2 = b.clone().multiplyScalar(-s).add(e.clone().multiplyScalar(-c));
  const out1 = b.clone().multiplyScalar(c).add(e.clone().multiplyScalar(s));
  const out2 = b.clone().multiplyScalar(c).add(e.clone().multiplyScalar(-s));
  return {
    planes: [new THREE.Plane(m1, 0), new THREE.Plane(m2, 0)],
    faces: [out1, out2],
    front: b,
    side: e,
  };
};

// Fades a lit material out below a line on screen (`fadeBelow`, px from the
// top), so a 3D object never runs over the captions in any camera move.
const fadeBelowScreen = (fadeBelow: number, height = 1920) => (sh: { uniforms: Record<string, { value: unknown }>; fragmentShader: string }) => {
  sh.uniforms.fadeY = { value: height - fadeBelow };
  sh.fragmentShader =
    "uniform float fadeY;\n" +
    sh.fragmentShader.replace("#include <dithering_fragment>", "#include <dithering_fragment>\n  gl_FragColor.a *= smoothstep(fadeY, fadeY + 70.0, gl_FragCoord.y);");
};

// The shaft: a lit tube in the accent from `from`'s surface down through the
// centre, drawn to `t` of the planet's diameter. `ghost` draws the part
// hidden inside the planet faintly through it, as an X-ray.
export const Shaft: React.FC<{ from: LonLat; t: number; radius?: number; ghost?: number; stub?: number; fadeBelow?: number }> = ({
  from,
  t,
  radius = 0.019,
  ghost = 0,
  stub = 0,
  fadeBelow = 1430,
}) => {
  const a = toVec(from, 1);
  // `stub` carries the drill on out of the far side, as far as that past the
  // surface, so the way out shows the bit breaking through.
  // Through, the bit stops just under the far surface, so the way out shows
  // an opening with the shaft deep in it, not the bit standing proud.
  const len = Math.min(2 * Math.min(1, Math.max(0, t)), 2 - radius * 3.2) + stub;
  const start = a.clone().multiplyScalar(1.004);
  const end = a.clone().multiplyScalar(1 - len);
  const geom = useMemo(() => {
    if (len <= 0.002) return null;
    const g = new THREE.CylinderGeometry(radius, radius, start.distanceTo(end), 48, 1, false);
    // Cylinder along local Y: place it between start and end.
    const mid = start.clone().add(end).multiplyScalar(0.5);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), a.clone().normalize());
    g.applyQuaternion(q);
    g.translate(mid.x, mid.y, mid.z);
    return g;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [from[0], from[1], len, radius]);
  if (!geom) return null;
  return (
    <>
      <mesh geometry={geom} renderOrder={4}>
        <meshStandardMaterial
          color={COLORS.accent}
          roughness={0.3}
          metalness={0.05}
          emissive={COLORS.accent}
          emissiveIntensity={0.06}
          transparent
          onBeforeCompile={fadeBelowScreen(fadeBelow)}
          customProgramCacheKey={() => `shaft-${fadeBelow}`}
        />
      </mesh>
      {ghost > 0 ? (
        <mesh geometry={geom} renderOrder={5}>
          <meshBasicMaterial color={COLORS.accent} transparent opacity={ghost} depthTest={false} depthWrite={false} />
        </mesh>
      ) : null}
      {/* The drill's head: a short cone, point first. */}
      <mesh position={end.clone().add(a.clone().multiplyScalar(-radius * 1.4))} quaternion={new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), a.clone().negate())} renderOrder={4}>
        <coneGeometry args={[radius * 1.05, radius * 2.8, 48]} />
        <meshStandardMaterial
          color={COLORS.accent}
          roughness={0.3}
          metalness={0.05}
          emissive={COLORS.accent}
          emissiveIntensity={0.06}
          transparent
          onBeforeCompile={fadeBelowScreen(fadeBelow)}
          customProgramCacheKey={() => `shaft-${fadeBelow}`}
        />
      </mesh>
    </>
  );
};
