import { geoGraticule10, geoMercator, geoPath } from "d3-geo";
import { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, LAYOUT } from "../brand/tokens";
import { Bars } from "../kit/Bars";
import { Captions } from "../kit/Captions";
import { Finish } from "../kit/Finish";
import { FOLLOW_CARD, FollowBeat, followVeil } from "../kit/FollowBeat";
import { Stroke } from "../kit/Stroke";
import { Badge, CaptionClearDefs, KineticTitle, MapLabel, SafeZoneOverlay } from "../kit/Type";
import { fade, LINE_LEAD, move, ramp, windowed } from "../lib/anim";
import { cueAt, shiftWords, type EpisodeProps } from "../lib/episode";
import { COUNTRIES, country, slide, slider } from "../lib/geo";

// A small, complete example of the grammar, not an episode: a kinetic title
// on screen from frame 0, a map beat whose picture follows the words, a
// chart beat sequenced after it (never cross-dissolved), word-by-word
// captions, and the follow beat into the end card. Every time comes from a
// word cue; no second is hard-coded.

const GREENLAND = country("Greenland");
const TARGET: [number, number] = [-35, 2];

export const Example: React.FC<EpisodeProps> = ({ timeline, lead, qa, bare, pictureY = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const projection = useMemo(() => geoMercator().scale(300).center([-30, 30]).translate([540, 1130 + pictureY]), [pictureY]);
  if (!timeline) return null;
  const at = (cue: string) => cueAt(timeline, lead, cue);
  const path = geoPath(projection);

  // The map beat: on screen from the first frame (the hook is spoken over
  // it), the shape named on "this", moving from "slide" (a reveal leads its
  // word; a move starts on it with the move ease), the equator drawn with
  // its label on "equator". The map is gone before the bars arrive.
  const mapOut = 1 - ramp(frame, fps, at("bars") - 0.6, 0.35, fade);
  const named = ramp(frame, fps, at("map@1") - LINE_LEAD, 0.3);
  const t = ramp(frame, fps, at("map@3"), 1.4, move);
  const moved = slide(GREENLAND, TARGET, t, true);
  // The name rides with the shape, above its northern tip, never on a line.
  const labelAt = projection(slider(GREENLAND, TARGET, t, true)([-40, 83.5]) as [number, number]) ?? [0, 0];
  const equator = ramp(frame, fps, at("map@6") - LINE_LEAD, 0.45);
  const eq = path({ type: "LineString", coordinates: [[-100, 0], [40, 0]] }) ?? "";

  const barsOn = windowed(frame, fps, at("bars") - 0.2, at("cta") - 0.4);
  const veil = followVeil(frame, fps, at("cta"));

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.ink }}>
      <AbsoluteFill style={{ opacity: mapOut }}>
        <svg width={1080} height={1920}>
          <CaptionClearDefs />
          <rect width={1080} height={1920} fill={COLORS.ocean} />
          <path d={path(geoGraticule10()) ?? ""} fill="none" stroke={COLORS.graticule} strokeWidth={1} />
          {COUNTRIES.map((c, i) => (
            <path key={i} d={path(c) ?? ""} fill={COLORS.land} stroke={COLORS.landEdge} strokeWidth={0.8} />
          ))}
          <path d={path(GREENLAND) ?? ""} fill="none" stroke={COLORS.paper} strokeWidth={2} strokeDasharray="6 6" opacity={0.6 * named * Math.min(1, t * 4)} />
          {/* The cover's subject: what covercheck measures and centres. */}
          <g data-cover-subject>
            <path d={path(moved) ?? ""} fill={COLORS.accent} fillOpacity={0.85 * named} stroke={COLORS.mark} strokeWidth={2} />
            <g mask="url(#captionClear)">
              <Stroke d={eq} color={COLORS.cool} width={4} opacity={equator} />
            </g>
          </g>
        </svg>
        {bare ? null : (
          <>
            <MapLabel x={labelAt[0]} y={labelAt[1]} text="Greenland" align="center" dy={-58} opacity={named} />
            <MapLabel x={150} y={projection([-100, 0])?.[1] ?? 0} text="Equator" dy={-56} color={COLORS.cool} opacity={equator} />
          </>
        )}
      </AbsoluteFill>

      {bare ? null : (
        <>
          <AbsoluteFill style={{ opacity: barsOn }}>
            <KineticTitle text="Each bar as long | as its *value*" start={at("bars") - 0.4} size={88} style={{ position: "absolute", left: 100, right: 120, top: LAYOUT.top + 60 }} />
            <Bars
              y={820}
              rowGap={200}
              thickness={72}
              rows={[
                { label: "First", value: 40, text: "40", at: at("bars@5"), labelAt: at("bars@2") },
                { label: "Second", value: 75, text: "75", at: at("bars@6"), labelAt: at("bars@2") },
                { label: "Third", value: 100, text: "100", at: at("bars@8"), labelAt: at("bars@2") },
              ]}
            />
          </AbsoluteFill>
          <Badge part={1} opacity={1 - veil} />
          <KineticTitle
            text="Can one script drive *every word* you see?"
            start={-1.0}
            end={at("map@1") - 0.1}
            size={96}
            style={{ position: "absolute", left: 100, right: 120, top: LAYOUT.top }}
          />
          <FollowBeat
            cta={at("cta")}
            tap={at("cta@4")}
            next={at("next")}
            part={2}
            title="What makes a *cover* work?"
            card={
              // "Videos like this" points at the video: its last picture stays
              // in view, small, above the profile.
              <Bars
                x={FOLLOW_CARD.x}
                y={FOLLOW_CARD.y + 10}
                width={FOLLOW_CARD.w - 40}
                rowGap={115}
                thickness={44}
                rows={[
                  { label: "First", value: 40, text: "40", at: 0 },
                  { label: "Second", value: 75, text: "75", at: 0 },
                  { label: "Third", value: 100, text: "100", at: 0 },
                ]}
              />
            }
          />
          <Captions words={shiftWords(timeline, lead)} keep={timeline.keep} split={timeline.split} />
        </>
      )}
      <Finish />
      {qa ? <SafeZoneOverlay /> : null}
    </AbsoluteFill>
  );
};
