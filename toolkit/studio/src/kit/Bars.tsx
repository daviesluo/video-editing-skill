import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { enter, LINE_LEAD, ramp } from "../lib/anim";

export type BarRow = {
  label: string;
  // The value that sets the length, and how it is written ("86%").
  value: number;
  text: string;
  // Video time of the word that names this row; the bar starts LINE_LEAD
  // before it, so it already reads when the word begins.
  at: number;
  // When the row's name shows, if before its bar ("Here are three bars"
  // names the rows before any number is said).
  labelAt?: number;
  color?: string;
};

// Horizontal bars in the house style. A bar is as long as its value and
// nothing more: no empty track, box or frame runs past it, because an empty
// track makes a small value read as a big box. The longest value spans the
// whole width, every row comes with its own number, and the number shows
// at its value once the bar is drawn (no counting).
export const Bars: React.FC<{ rows: BarRow[]; x?: number; y?: number; width?: number; rowGap?: number; thickness?: number }> = ({
  rows,
  x = 100,
  y = 700,
  width = 860,
  rowGap = 150,
  thickness = 56,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const max = Math.max(...rows.map((r) => r.value));
  return (
    <div style={{ position: "absolute", left: x, top: y, width }}>
      {rows.map((r, i) => {
        const named = ramp(frame, fps, (r.labelAt ?? r.at) - LINE_LEAD, 0.3, enter);
        const grow = ramp(frame, fps, r.at - LINE_LEAD, 0.45, enter);
        const shown = ramp(frame, fps, r.at - LINE_LEAD + 0.35, 0.2, enter);
        const len = (r.value / max) * width;
        return (
          <div key={i} style={{ position: "absolute", left: 0, top: i * rowGap, width }}>
            <div style={{ opacity: named, fontFamily: DISPLAY, fontWeight: 650, fontSize: 36, lineHeight: 1.1, color: COLORS.paper, textShadow: THEME.haloStrong }}>
              {r.label}
            </div>
            <div style={{ marginTop: 12, height: thickness, width: len * grow, borderRadius: 4, background: r.color ?? COLORS.accent }} />
            <div
              style={{
                position: "absolute",
                top: 44 + thickness / 2 - 30,
                left: Math.min(len + 16, width - 160),
                fontFamily: DISPLAY,
                fontWeight: 820,
                fontSize: 52,
                lineHeight: 1.1,
                color: len + 16 > width - 160 ? COLORS.mark : COLORS.paper,
                opacity: shown,
                textShadow: len + 16 > width - 160 ? "none" : THEME.haloStrong,
              }}
            >
              {r.text}
            </div>
          </div>
        );
      })}
    </div>
  );
};
