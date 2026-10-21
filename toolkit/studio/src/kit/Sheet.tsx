import { AbsoluteFill, useVideoConfig } from "remotion";
import { COLORS } from "../brand/tokens";
import { lerp } from "../lib/anim";

// The pull-back to the whole map ("Blame this map", "maps like this one"):
// the camera pulls straight back until the whole plate sits in the frame as
// one printed sheet on a light mount with a soft contact shadow, under the
// headline: the same designed move wherever the narration points at a
// whole map.

const SHADOW = [1, 3, 5].map((i) => parseInt(COLORS.paper.slice(i, i + 2), 16)).join(",");

// The sheet: a plate rectangle (plate pixels) shown `width` px wide with
// its centre at screen y `cy`.
export type SheetRect = { x0: number; y0: number; x1: number; y1: number; s: number; c: readonly [number, number]; mount: number };
export const sheetRect = (x0: number, y0: number, x1: number, y1: number, width: number, cy: number, mount = 16, frameH = 1920): SheetRect => {
  const s = width / (x1 - x0);
  return { x0, y0, x1, y1, s, c: [(x0 + x1) / 2, (y0 + y1) / 2 - (cy - frameH / 2) / s] as const, mount };
};

// A zoom about the one plate point that holds still on screen between the
// two cameras, with the scale eased in log space: the camera reads as
// pulling straight back, not panning and zooming at once.
export const pullBack = (c0: readonly [number, number], s0: number, k: number, sheet: SheetRect): { c: readonly [number, number]; s: number } => {
  const { c: c1, s: s1 } = sheet;
  if (k <= 0) return { c: c0, s: s0 };
  const s = Math.exp(lerp(Math.log(s0), Math.log(s1), k));
  const f = [0, 1].map((i) => (c1[i] * s1 - c0[i] * s0) / (s1 - s0));
  return { c: [0, 1].map((i) => f[i] + ((c0[i] - f[i]) * s0) / s) as [number, number], s };
};

// The sheet's edge on screen: the frame itself at rest, the projected plate
// edge once pulled back, and the mount and shadow growing in with it.
export const SheetFrame: React.FC<{ k: number; cam: { c: readonly [number, number]; s: number }; sheet: SheetRect; children: React.ReactNode }> = ({
  k,
  cam,
  sheet,
  children,
}) => {
  const { width, height } = useVideoConfig();
  if (k <= 0) return <>{children}</>;
  const { x0, y0, x1, y1 } = sheet;
  const sx = (x: number) => (x - cam.c[0]) * cam.s + width / 2;
  const sy = (y: number) => (y - cam.c[1]) * cam.s + height / 2;
  // Never wider than the plate itself: mid-move the frame could reach past
  // the plate's edge and show blank paper and stray outlines inside the
  // sheet.
  const r = {
    l: Math.max(lerp(0, sx(x0), k), sx(x0)),
    t: Math.max(lerp(0, sy(y0), k), sy(y0)),
    r: Math.min(lerp(width, sx(x1), k), sx(x1)),
    b: Math.min(lerp(height, sy(y1), k), sy(y1)),
  };
  const m = sheet.mount * k;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: r.l - m,
          top: r.t - m,
          width: r.r - r.l + 2 * m,
          height: r.b - r.t + 2 * m,
          backgroundColor: COLORS.mark,
          borderRadius: 4,
          opacity: k,
          boxShadow: `0 ${34 * k}px ${80 * k}px -${24 * k}px rgba(${SHADOW},0.42), 0 ${3 * k}px ${10 * k}px rgba(${SHADOW},0.14)`,
        }}
      />
      <AbsoluteFill style={{ clipPath: `inset(${r.t}px ${width - r.r}px ${height - r.b}px ${r.l}px)` }}>{children}</AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: r.l,
          top: r.t,
          width: r.r - r.l,
          height: r.b - r.t,
          boxShadow: `inset 0 0 0 1.5px rgba(${SHADOW},${0.35 * k})`,
        }}
      />
    </>
  );
};
