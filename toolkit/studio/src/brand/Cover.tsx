import { AbsoluteFill, Freeze, staticFile, useVideoConfig, type CalculateMetadataFunction } from "remotion";
import { COLORS, FRAME, SERIES, THEME } from "./tokens";
import { DISPLAY } from "./fonts";
import { cueAt, type EpisodeProps, type Timeline } from "../lib/episode";
import { Scrim } from "../kit/Type";
import { CoverProbe } from "../kit/CoverProbe";
import { EPISODES } from "../episodes";

export type CoverProps = EpisodeProps & {
  // The episode drawn, and the part number on the badge.
  ep: keyof typeof EPISODES;
  part: number;
  // The frame shown, as a cue plus seconds. Pick a moment where nothing is
  // mid-fade or mid-move: a cover frozen as names faded out showed
  // half-transparent type.
  cue: string;
  offset: number;
  // `*word*` is set in the accent colour; "|" breaks the line, as in the
  // episode's own title.
  title: string;
  // Title size, px (96 to 108); a smaller size keeps a long title clear of
  // the picture.
  size?: number;
};

// A cover, 1080x1920: a frozen, bare frame of the episode (picture only,
// full bleed, no captions or labels) with the badge and the title over the
// theme's light scrim, never a panel. The profile grid shows only the
// middle 3:4 (y 240 to 1680), which is the real design surface:
// pipeline/covercheck.py holds the rules, and scripts/covers.mjs renders,
// measures and checks every cover. Mark the picture's subject with
// data-cover-subject in the episode, so the probe can measure it.
export const Cover: React.FC<CoverProps> = (props) => {
  const { fps } = useVideoConfig();
  const { timeline, lead, ep, part, cue, offset, title, size = 108 } = props;
  if (!timeline) return null;
  const Ep = EPISODES[ep];
  const frame = Math.round((cueAt(timeline, lead, cue) + offset) * fps);
  const words = title.split(/(\*[^*]+\*)/).filter(Boolean);
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.ink }}>
      <Freeze frame={frame}>
        <Ep {...props} qa={false} bare />
      </Freeze>
      <Scrim to={760} strength={0.9} />
      <div data-cover-title style={{ position: "absolute", left: 100, right: 120, top: 300 }}>
        <div style={{ fontFamily: DISPLAY, fontWeight: 760, fontSize: 36, letterSpacing: "-0.005em", color: COLORS.paper, textShadow: THEME.haloStrong }}>
          {SERIES}
          <span style={{ color: COLORS.accent, marginLeft: 14 }}>Part {part}</span>
        </div>
        <div
          style={{
            marginTop: 28,
            fontFamily: DISPLAY,
            fontWeight: 880,
            fontSize: size,
            lineHeight: 0.98,
            letterSpacing: "-0.035em",
            color: COLORS.paper,
            textShadow: THEME.haloSoft,
            textWrap: "balance",
          }}
        >
          {words.map((w, i) =>
            w.startsWith("*") ? (
              <span key={i} style={{ color: COLORS.accent }}>
                {w.slice(1, -1)}
              </span>
            ) : (
              <span key={i}>{w.split("|").map((part, j) => (j ? [<br key={j} />, part.trimStart()] : part))}</span>
            ),
          )}
        </div>
      </div>
      <CoverProbe />
    </AbsoluteFill>
  );
};

export const coverMetadata: CalculateMetadataFunction<CoverProps> = async ({ props }) => {
  const res = await fetch(staticFile(`episodes/${props.id}/timeline.json`));
  if (!res.ok) throw new Error(`No timeline for ${props.id}`);
  const timeline = (await res.json()) as Timeline;
  const lead = timeline.lead ?? props.lead;
  const tail = timeline.tail ?? props.tail;
  // As long as the episode: Remotion clamps every frame, frozen ones too,
  // to the composition's range, so a one-frame composition would always
  // show the episode's frame 0. The cover itself is frame 0.
  return { durationInFrames: Math.ceil((lead + timeline.duration + tail) * FRAME.fps), props: { ...props, lead, tail, timeline } };
};
