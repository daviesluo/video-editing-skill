import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { enter, ramp } from "../lib/anim";

// A quotation set large in the house face, with curly marks, revealed word
// by word in sync with the narrator reading it, and a plain attribution
// line under it: author, work, year, and the translator if any. The words
// on screen are the source's exact words; an omission is marked with an
// ellipsis and never changes the meaning.
export const Quote: React.FC<{
  // The quoted words as printed, and the video time each is spoken (from the
  // timeline, one per word).
  words: string[];
  times: number[];
  attribution: string;
  start: number;
  end?: number;
  x?: number;
  y?: number;
  width?: number;
  size?: number;
}> = ({ words, times, attribution, start, end, x = 100, y = 640, width = 860, size = 84 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const lead = 2 / fps;
  const shown = Math.min(ramp(frame, fps, start, 0.4, enter), end === undefined ? 1 : 1 - ramp(frame, fps, end - 0.3, 0.3));
  return (
    <div style={{ position: "absolute", left: x, top: y, width, opacity: shown }}>
      <div style={{ fontFamily: DISPLAY, fontWeight: 760, fontSize: size, lineHeight: 1.08, letterSpacing: "-0.02em", color: COLORS.paper, textShadow: THEME.halo, textWrap: "balance" }}>
        <span style={{ color: COLORS.accent }}>“</span>
        {words.map((w, i) => (
          <span
            key={i}
            style={{
              opacity: interpolate(t, [times[i] - lead, times[i] - lead + 0.08], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}
          >
            {w}
            {i < words.length - 1 ? " " : ""}
          </span>
        ))}
        <span style={{ color: COLORS.accent, opacity: t >= times[times.length - 1] - lead ? 1 : 0 }}>”</span>
      </div>
      <div style={{ marginTop: 36, fontFamily: DISPLAY, fontWeight: 600, fontSize: 36, lineHeight: 1.2, color: COLORS.note, textShadow: THEME.haloStrong }}>
        {attribution}
      </div>
    </div>
  );
};
