import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { enter, LINE_LEAD, ramp } from "../lib/anim";

export type TimelineEvent = { year: number; label: string; at: number; below?: boolean };
export type Era = { from: number; to: number; label: string; at: number };

// A timeline on a real scale: positions are proportional to time, so a gap
// that looks long was long. Events are placed at their value at once and
// fade in on their words; nothing slides along the axis, because a marker
// in motion shows a false date on every frame before it lands. Eras are
// quiet bands. Name the calendar where it matters (`calendar`). The
// default span keeps the end labels inside the safe box (x 90 to 960).
export const Timeline: React.FC<{
  from: number;
  to: number;
  step: number;
  start: number;
  end?: number;
  events: TimelineEvent[];
  eras?: Era[];
  calendar?: string;
  x?: number;
  y?: number;
  width?: number;
}> = ({ from, to, step, start, end, events, eras = [], calendar, x = 140, y = 900, width = 780 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shown = Math.min(ramp(frame, fps, start, 0.4, enter), end === undefined ? 1 : 1 - ramp(frame, fps, end - 0.3, 0.3));
  const draw = ramp(frame, fps, start, 0.7, enter);
  const X = (year: number) => ((year - from) / (to - from)) * width;
  const ticks: number[] = [];
  for (let v = Math.ceil(from / step) * step; v <= to; v += step) ticks.push(v);
  const small: React.CSSProperties = { fontFamily: DISPLAY, fontWeight: 560, fontSize: 30, color: COLORS.note, textShadow: THEME.haloStrong, whiteSpace: "nowrap" };
  return (
    <div style={{ position: "absolute", left: x, top: y, width, opacity: shown }}>
      {eras.map((e, i) => {
        const o = ramp(frame, fps, e.at - LINE_LEAD, 0.4, enter);
        return (
          <div key={i} style={{ position: "absolute", left: X(e.from), top: -70, width: X(e.to) - X(e.from), height: 140, background: COLORS.coolLight, opacity: 0.25 * o }}>
            <div style={{ ...small, position: "absolute", left: 12, top: -44, opacity: o }}>{e.label}</div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 0, top: -2, width: width * draw, height: 4, borderRadius: 2, background: COLORS.paper }} />
      {ticks.map((v) => (
        <div key={v} style={{ position: "absolute", left: X(v), top: 0, opacity: draw >= (v - from) / (to - from) ? 1 : 0 }}>
          <div style={{ position: "absolute", left: -1.5, top: -10, width: 3, height: 20, background: COLORS.paper }} />
          <div style={{ ...small, position: "absolute", top: 26, left: -60, width: 120, textAlign: "center" }}>{v}</div>
        </div>
      ))}
      {events.map((e, i) => {
        const o = ramp(frame, fps, e.at - LINE_LEAD, 0.35, enter);
        const below = e.below ?? false;
        return (
          <div key={i} style={{ position: "absolute", left: X(e.year), top: 0, opacity: o }}>
            <div style={{ position: "absolute", left: -13, top: -13, width: 26, height: 26, borderRadius: "50%", background: COLORS.accent, boxShadow: `0 0 0 5px ${COLORS.mark}` }} />
            <div
              style={{
                position: "absolute",
                left: X(e.year) > width / 2 ? -400 : -20,
                width: 420,
                textAlign: X(e.year) > width / 2 ? "right" : "left",
                top: below ? 84 : -150,
                fontFamily: DISPLAY,
                color: COLORS.paper,
                textShadow: THEME.haloStrong,
              }}
            >
              <div style={{ fontWeight: 820, fontSize: 64, lineHeight: 1, color: COLORS.accent }}>{e.year}</div>
              <div style={{ fontWeight: 650, fontSize: 36, lineHeight: 1.15, marginTop: 8 }}>{e.label}</div>
            </div>
          </div>
        );
      })}
      {calendar ? <div style={{ ...small, position: "absolute", left: 0, top: 80 }}>{calendar}</div> : null}
    </div>
  );
};
