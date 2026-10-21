import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, LAYOUT, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { GAP, paginate, SIZE, TRACK, type Word } from "./paginate.ts";

export type { Word };

// Word-by-word captions in place: each word appears as it is spoken, in
// its final position, the spoken word in the accent colour. Low in the
// frame, just above the platform's interface (LAYOUT.captions). Pages and
// words show two frames ahead of the voice, inside the accepted lead for
// captions. Nothing else may sit over this band: mask lines and labels
// above it (kit/Type.tsx CaptionClear).
export const Captions: React.FC<{ words: Word[]; y?: number; keep?: string[]; split?: string[] }> = ({ words, y = LAYOUT.captions, keep = [], split = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const pages = paginate(words, keep, split);
  const lead = 2 / fps;
  const idx = pages.findIndex((p, i) => {
    const next = pages[i + 1];
    const until = next ? next.start - lead : p.end + 0.6;
    return t >= p.start - lead && t < Math.min(until, p.end + 0.6);
  });
  if (idx < 0) return null;
  const page = pages[idx];
  const pop = interpolate(t, [page.start - lead, page.start - lead + 0.12], [1.06, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // A page with no page straight after it (the last one, or one before a
  // long pause) fades over 0.15 s rather than vanishing in one frame.
  const next = pages[idx + 1];
  const hide = page.end + 0.6;
  const gone = next && next.start - lead <= hide ? 0 : interpolate(t, [hide - 0.15, hide], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 200,
          right: 200,
          top: y,
          display: "flex",
          justifyContent: "center",
          flexWrap: "wrap",
          gap: `0 ${GAP}em`,
          fontFamily: DISPLAY,
          fontWeight: 800,
          fontStretch: "100%",
          fontSize: SIZE * page.scale,
          lineHeight: 1.05,
          letterSpacing: `${TRACK}em`,
          textAlign: "center",
          scale: String(pop),
          opacity: 1 - gone,
          // The tight outline small type wears, so a caption reads even in
          // its own colour over a tint of that colour.
          textShadow: `${THEME.haloStrong}, ${THEME.haloSoft}`,
        }}
      >
        {page.words.map((w, i) => {
          const next = page.words[i + 1];
          const active = t >= w.start && t < (next ? next.start : page.end + 0.6);
          // Each word appears as it is spoken, in its final place, so the
          // line never runs ahead of the voice and never reflows. A page's
          // first word is there at once: the old page has just gone, and a
          // fade from nothing left the caption band empty for a frame at
          // every page change.
          const shown =
            i === 0
              ? 1
              : interpolate(t, [w.start - lead, w.start - lead + 0.07], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                });
          return (
            <span key={i} style={{ color: active ? COLORS.accent : COLORS.paper, opacity: shown }}>
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
