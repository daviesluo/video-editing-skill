import { AbsoluteFill } from "remotion";
import { COLORS } from "../brand/tokens";
import { SectionFace, Shaft, wedge } from "../kit/CutAway3D";
import { GlobeView, keyLight, type GlobeCam } from "../kit/GlobeView";
import { toVec } from "../lib/globe";

// A lab composition: the cut-away globe alone, every design choice a prop,
// so options are explored here and not inside an episode. Render one still
// per set of props and compare them side by side:
//
//   node scripts/variants.mjs CutAwayLab out/lab \
//     '[{"name":"square","props":{"turn":0}},{"name":"off-square","props":{"turn":0.6}}]'
//
// Review the stills yourself over several rounds (shape, light, material,
// edges, and how each looks in the close-up and mid-turn), and show the
// owner two or three that pass, never the first round.

export type LabProps = {
  cam: GlobeCam; // the camera
  at: [number, number]; // where the shaft goes in, lon and lat
  open: number; // 0 shut to 1 open: the wedge's half-angle is open x 45 degrees
  turn: number; // radians off square to the camera; about 0.6 reads as depth
  drill: number; // how far the shaft runs, 0 to 1 of the diameter
  radius: number; // the shaft's radius, in planet radii
  dot: boolean; // the way in as a 2D dot sized for the view
};

export const LAB_DEFAULTS: LabProps = {
  cam: { lon: -50, lat: 14, distance: 6.2 },
  at: [-73.982, 40.7519],
  open: 1,
  turn: 0.6,
  drill: 0.7,
  radius: 0.019,
  dot: true,
};

export const CutAwayLab: React.FC<Partial<LabProps>> = (p) => {
  const { cam, at, open, turn, drill, radius, dot } = { ...LAB_DEFAULTS, ...p };
  const axis = toVec(at).normalize();
  const cut = open > 0.001 ? wedge(axis, toVec([cam.lon, cam.lat]).normalize(), (Math.PI / 4) * open, turn) : null;
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.ink }}>
      <GlobeView
        cam={cam}
        shiftY={140}
        clip={cut ? cut.planes : undefined}
        clipIntersection
        scene={
          <>
            {cut ? cut.faces.map((out, i) => <SectionFace key={i} axis={axis} out={out} light={keyLight(cam)} />) : null}
            <Shaft from={at} t={drill} radius={radius} />
          </>
        }
      >
        {(project) => {
          const q = project(at);
          return dot && q.visible ? (
            <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
              <circle cx={q.x} cy={q.y} r={11} fill={COLORS.mark} stroke={COLORS.paper} strokeWidth={3.5} />
            </svg>
          ) : null;
        }}
      </GlobeView>
    </AbsoluteFill>
  );
};
