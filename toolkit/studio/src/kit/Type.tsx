import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, LAYOUT, SAFE, SERIES, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { enter, ramp, windowed } from "../lib/anim";

// Type in the house style: one face (Archivo, normal width), sentence case,
// no boxes, chips, outlines, rules, separators, arrows, glow or blur. Small
// type is at least 29 px and wears the tight halo in the page colour, so it
// reads on any background without a box behind it.

// A headline whose words rise into place one after another, each from
// behind its own line mask, as in editorial motion graphics. Lines are
// balanced, so a headline never ends on a lone word. Wrap a word or a run of
// words in *asterisks* to set it in the accent colour ("*come out?*" spans
// two words). A lone "|" forces a line break. A title meant to be read on
// the first frame starts its reveal before frame 0 (start -1.0), so frame 0
// is never caught mid-reveal.
export const KineticTitle: React.FC<{
  text: string;
  start: number;
  end?: number;
  size?: number;
  color?: string;
  stagger?: number;
  style?: React.CSSProperties;
}> = ({ text, start, end, size = 112, color = COLORS.paper, stagger = 0.05, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = end === undefined ? 1 : 1 - ramp(frame, fps, end - 0.3, 0.3);
  const words = text.split(" ");
  let open = false;
  const accents = words.map((w) => {
    const starts = w.startsWith("*");
    const accent = open || starts;
    if (starts) open = true;
    if (/\*[?.!,:;’”]*$/.test(w) && w !== "*") open = false;
    return accent;
  });
  return (
    <div
      style={{
        fontFamily: DISPLAY,
        fontWeight: 820,
        fontStretch: "100%",
        fontSize: size,
        lineHeight: 1.02,
        letterSpacing: "-0.03em",
        color,
        opacity: out,
        textWrap: "balance",
        textShadow: THEME.halo,
        ...style,
      }}
    >
      {words.map((w, i) => {
        if (w === "|") return <br key={i} />;
        const p = ramp(frame, fps, start + i * stagger, 0.6, enter);
        const clean = w.replace(/\*/g, "");
        return (
          // The mask is padded on every side so the halo is not clipped to a
          // hard edge; the word starts far enough down to clear the padding.
          <span key={i} style={{ display: "inline-block", overflow: "hidden", verticalAlign: "top", padding: "0.14em 0.14em 0.2em", margin: "-0.14em -0.14em -0.2em" }}>
            <span style={{ display: "inline-block", translate: `0px ${(1 - p) * 140}%`, color: accents[i] ? COLORS.accent : undefined }}>
              {clean}
              {i < words.length - 1 && words[i + 1] !== "|" ? " " : ""}
            </span>
          </span>
        );
      })}
    </div>
  );
};

// A number with what it measures and, if it has one, its source. The number
// is shown at its value at once: a counting animation shows a false number
// on every frame before it lands, and a paused frame or a cover can catch
// it there.
export const Stat: React.FC<{
  value: string;
  start: number;
  end?: number;
  label: string;
  source?: string;
  color?: string;
  size?: number;
  style?: React.CSSProperties;
}> = ({ value, start, end, label, source, color = COLORS.accent, size = 136, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const vis = end === undefined ? ramp(frame, fps, start, 0.35) : windowed(frame, fps, start, end);
  return (
    <div style={{ opacity: vis, translate: `0px ${(1 - vis) * 24}px`, ...style }}>
      <div style={{ fontFamily: DISPLAY, fontWeight: 880, fontSize: size, lineHeight: 0.9, letterSpacing: "-0.04em", color, textShadow: THEME.halo }}>
        {value}
      </div>
      <div
        style={{
          marginTop: 14,
          fontFamily: DISPLAY,
          fontWeight: 600,
          fontSize: Math.max(36, Math.round(size * 0.31)),
          lineHeight: 1.1,
          color: COLORS.paper,
          textShadow: THEME.haloStrong,
          textWrap: "balance",
        }}
      >
        {label}
      </div>
      {source ? <SourceTag text={source} style={{ marginTop: 16 }} /> : null}
    </div>
  );
};

// "Source: NOAA", in plain words: no brackets, dots or arrows.
export const SourceTag: React.FC<{ text: string; style?: React.CSSProperties }> = ({ text, style }) => (
  <div style={{ fontFamily: DISPLAY, fontWeight: 560, fontSize: 29, lineHeight: 1.2, color: COLORS.note, textShadow: THEME.haloStrong, textWrap: "balance", ...style }}>
    Source: {text}
  </div>
);

// The series badge, close under the platform's top bar: the series name,
// then "Part N" in the accent.
export const Badge: React.FC<{ part: number; opacity?: number }> = ({ part, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      left: 100,
      top: LAYOUT.badge,
      display: "flex",
      alignItems: "center",
      gap: 14,
      fontFamily: DISPLAY,
      fontSize: 36,
      fontWeight: 760,
      letterSpacing: "-0.005em",
      color: COLORS.paper,
      textShadow: THEME.haloStrong,
      opacity,
    }}
  >
    <span>{SERIES}</span>
    <span style={{ color: COLORS.accent }}>Part {part}</span>
  </div>
);

// A short kicker line above or below a headline ("Drawn in 1569, for
// sailors"): colour and weight set it apart; no box or rule.
export const Kicker: React.FC<{ text: string; color?: string; opacity?: number; style?: React.CSSProperties }> = ({ text, color = COLORS.paper, opacity = 1, style }) => (
  <div
    style={{
      fontFamily: DISPLAY,
      fontWeight: 650,
      fontSize: 34,
      lineHeight: 1.2,
      color,
      opacity,
      textShadow: THEME.haloStrong,
      textWrap: "balance",
      translate: `0px ${(1 - opacity) * 14}px`,
      ...style,
    }}
  >
    {text}
  </div>
);

// A label placed by its anchor point, beside the thing it names, never on
// a line. It moves with its shape or leaves; it never sits half-transparent
// over a moving shape.
export const MapLabel: React.FC<{
  x: number;
  y: number;
  text: string;
  align?: "left" | "right" | "center";
  dy?: number;
  size?: number;
  color?: string;
  opacity?: number;
}> = ({ x, y, text, align = "left", dy = 30, size = 40, color = COLORS.paper, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      left: align === "left" ? x - 6 : align === "right" ? x - 400 + 6 : x - 200,
      top: y + dy,
      width: 400,
      textAlign: align,
      fontFamily: DISPLAY,
      fontWeight: 720,
      fontSize: Math.max(29, size),
      lineHeight: 1.05,
      color,
      opacity,
      textShadow: THEME.haloStrong,
      whiteSpace: "pre",
    }}
  >
    {text}
  </div>
);

// A gradient in the page colour behind headlines, kept light (scrimScale).
export const Scrim: React.FC<{ from?: number; to?: number; strength?: number; bottom?: boolean }> = ({ from = 0, to = 900, strength = 0.82, bottom = false }) => {
  const k = strength * THEME.scrimScale;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: from,
        height: to - from,
        background: `linear-gradient(${bottom ? "0deg" : "180deg"}, rgba(${THEME.scrim},${k}) 0%, rgba(${THEME.scrim},${k * 0.6}) 45%, rgba(${THEME.scrim},0) 100%)`,
      }}
    />
  );
};

// SVG defs for a mask that fades anything drawn under it out above the
// caption band, so a line that sweeps during a camera move can never cross
// a caption. Put <CaptionClearDefs /> in the scene's <svg> and draw lines
// and their labels in <g mask="url(#captionClear)">.
export const CaptionClearDefs: React.FC<{ id?: string }> = ({ id = "captionClear" }) => (
  <defs>
    <linearGradient id={`${id}Fade`} gradientUnits="userSpaceOnUse" x1="0" y1={LAYOUT.captions - 90} x2="0" y2={LAYOUT.captions - 20}>
      <stop offset="0" stopColor="#fff" />
      <stop offset="1" stopColor="#000" />
    </linearGradient>
    <mask id={id} maskUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1920">
      <rect x="0" y="0" width="1080" height="1920" fill={`url(#${id}Fade)`} />
    </mask>
  </defs>
);

// QA stills only: the safe box and the caption band over a frame. The red
// bands are what the platform's interface covers.
export const SafeZoneOverlay: React.FC = () => (
  <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
    <rect x={0} y={0} width={1080} height={SAFE.top} fill="rgba(255,0,0,0.18)" />
    <rect x={0} y={SAFE.bottom} width={1080} height={1920 - SAFE.bottom} fill="rgba(255,0,0,0.18)" />
    <rect x={SAFE.right} y={SAFE.top} width={1080 - SAFE.right} height={SAFE.bottom - SAFE.top} fill="rgba(255,0,0,0.12)" />
    <rect x={SAFE.railX} y={SAFE.railY} width={SAFE.right - SAFE.railX} height={SAFE.bottom - SAFE.railY} fill="rgba(255,0,0,0.12)" />
    <rect x={SAFE.left} y={SAFE.top} width={SAFE.right - SAFE.left} height={SAFE.bottom - SAFE.top} fill="none" stroke="#00FF88" strokeWidth={3} strokeDasharray="12 10" />
    <rect x={200} y={LAYOUT.captions} width={680} height={150} fill="none" stroke="#00C8FF" strokeWidth={3} strokeDasharray="8 8" />
  </svg>
);
