import { Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { fade, ramp } from "../lib/anim";

// A company's mark shown to identify it, never to decorate or endorse:
// unaltered, at its own colours and proportions, beside the company's name,
// from the company's own press-kit file (`src` in public/), and animated
// only by opacity. No morphing, recolouring, spinning or placing it to
// imply a sponsorship. `mark` takes a drawn placeholder instead of a file,
// for templates and examples: never a real company's mark redrawn.
export const Logo: React.FC<{
  name: string;
  at: number;
  end?: number;
  src?: string;
  mark?: React.ReactNode;
  size?: number;
  credit?: string;
  x?: number;
  y?: number;
}> = ({ name, at, end, src, mark, size = 220, credit, x = 110, y = 760 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = Math.min(ramp(frame, fps, at - 0.25, 0.45, fade), end === undefined ? 1 : 1 - ramp(frame, fps, end - 0.3, 0.3, fade));
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: o }}>
      <div style={{ display: "flex", alignItems: "center", gap: 44 }}>
        <div style={{ width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {src ? <Img src={staticFile(src)} style={{ maxWidth: size, maxHeight: size, objectFit: "contain" }} /> : mark}
        </div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 760, fontSize: 64, lineHeight: 1.05, letterSpacing: "-0.02em", color: COLORS.paper, textShadow: THEME.halo }}>
          {name}
        </div>
      </div>
      {credit ? (
        <div style={{ marginTop: 40, fontFamily: DISPLAY, fontWeight: 560, fontSize: 29, lineHeight: 1.2, color: COLORS.note, textShadow: THEME.haloStrong }}>{credit}</div>
      ) : null}
    </div>
  );
};

// A neutral placeholder mark for examples and templates: two overlapping
// rounded squares in the accent and the comparison colour.
export const PlaceholderMark: React.FC<{ size?: number }> = ({ size = 220 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="8" y="8" width="58" height="58" rx="14" fill={COLORS.cool} />
    <rect x="34" y="34" width="58" height="58" rx="14" fill={COLORS.accent} opacity={0.92} />
  </svg>
);
