import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, LAYOUT } from "../brand/tokens";
import { Captions } from "../kit/Captions";
import { Finish } from "../kit/Finish";
import { FollowBeat, followVeil } from "../kit/FollowBeat";
import { Badge, KineticTitle, SafeZoneOverlay } from "../kit/Type";
import { cueAt, shiftWords, type EpisodeProps } from "../lib/episode";

// {{ID}}: the scenes of "{{TITLE}}". Start from Example.tsx for the
// grammar of each kind of beat (map, globe, cut-away, bars, document,
// quote, timeline, mark). Every time is a word cue: at("seg"), at("seg@k"),
// at("seg$"); never a second. Mark the cover's subject with
// data-cover-subject.
export const {{COMPONENT}}: React.FC<EpisodeProps> = ({ timeline, lead, qa, bare }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!timeline) return null;
  const at = (cue: string) => cueAt(timeline, lead, cue);
  const veil = followVeil(frame, fps, at("cta"));
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.ink }}>
      <div data-cover-subject>{/* the picture: the beats, keyed to words */}</div>
      {bare ? null : (
        <>
          <Badge part={{{NUMBER}}} opacity={1 - veil} />
          <KineticTitle text="<the hook, | with *the accent phrase*>" start={-1.0} end={at("answer") - 0.1} size={96}
            style={{ position: "absolute", left: 100, right: 120, top: LAYOUT.top }} />
          <FollowBeat cta={at("cta")} tap={at("cta@4")} next={at("next")} part={{{NEXT}}} title="<the next hook, word for word>" />
          <Captions words={shiftWords(timeline, lead)} keep={timeline.keep} split={timeline.split} />
        </>
      )}
      <Finish />
      {qa ? <SafeZoneOverlay /> : null}
    </AbsoluteFill>
  );
};
