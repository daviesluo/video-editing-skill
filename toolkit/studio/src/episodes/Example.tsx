import { geoPath } from "d3-geo";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, LAYOUT } from "../brand/tokens";
import { Bars } from "../kit/Bars";
import { Captions } from "../kit/Captions";
import { Opening, SectionFace, Shaft, wedge } from "../kit/CutAway3D";
import { Document } from "../kit/Document";
import { Finish } from "../kit/Finish";
import { FOLLOW_CARD, FollowBeat, followVeil } from "../kit/FollowBeat";
import { GlobeView, keyLight, lerpCam, type GlobeCam } from "../kit/GlobeView";
import { Logo, PlaceholderMark } from "../kit/Logo";
import { MapView } from "../kit/MapView";
import { Quote } from "../kit/Quote";
import { Stroke } from "../kit/Stroke";
import { Timeline } from "../kit/Timeline";
import { Badge, CaptionClearDefs, KineticTitle, MapLabel, SafeZoneOverlay } from "../kit/Type";
import { enter, fade, LINE_LEAD, move, ramp, windowed } from "../lib/anim";
import { cueAt, shiftWords, type EpisodeProps } from "../lib/episode";
import { country, slide, slider } from "../lib/geo";
import { toVec } from "../lib/globe";
import { plateLook } from "../lib/plateLook";
import { PROJECTIONS } from "../lib/projections";

// A small, complete example of the grammar, not an episode. Every beat
// follows its words and every time is a word cue:
// - a kinetic title, complete on frame 0, over a relief map plate;
// - a true-size slide on the map (a rotation on the sphere), the equator
//   drawn with its label on its word;
// - a globe located wide, then moved in, with a cut-away 3D object built
//   in the scene: a wedge cut along a shaft through the planet, opened
//   turned off square to the camera and shut before the scene leaves;
// - bars, a document with its line brought forward, a quotation read in
//   sync, a timeline to scale, and a company's mark (a placeholder);
// - the follow beat into the end card.
// Beats are sequenced: each is gone before the next arrives.

const GREENLAND = country("Greenland");
const TARGET: [number, number] = [-35, 2];
const PLATE = { name: "mercator-world84", w: 4096, h: 6400 } as const;
const LOOK = plateLook(PLATE.name, PLATE.w, PLATE.h);
const CITY: [number, number] = [-73.982, 40.7519];
const CAM_WIDE: GlobeCam = { lon: -45, lat: 18, distance: 9 };
const CAM_NEAR: GlobeCam = { lon: -50, lat: 14, distance: 6.2 };

export const Example: React.FC<EpisodeProps> = ({ timeline, lead, qa, bare, pictureY = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!timeline) return null;
  const at = (cue: string) => cueAt(timeline, lead, cue);
  // A beat's window: in just before its first word, out before the next
  // beat comes in, so two beats never show at once.
  const beat = (seg: string, next: string) => windowed(frame, fps, at(seg) - 0.3, at(next) - 0.4, 0.35, 0.3);

  // Map: the shape named on "this", moving from "slide", the equator and its
  // name together on "equator".
  const mapOn = 1 - ramp(frame, fps, at("globe") - 0.7, 0.3, fade);
  const named = ramp(frame, fps, at("map@1") - LINE_LEAD, 0.3);
  const t = ramp(frame, fps, at("map@3"), 1.4, move);
  const moved = slide(GREENLAND, TARGET, t, true);
  const tip = slider(GREENLAND, TARGET, t, true)([-32, 83.4]);
  const equator = ramp(frame, fps, at("map@6") - LINE_LEAD, 0.45);

  // Globe: located wide, then in; the cut opens on "shaft", the shaft runs
  // "through the Earth", and the cut shuts before the globe leaves.
  const globeOn = beat("globe", "bars");
  const toNear = ramp(frame, fps, at("globe") - 0.2, 1.6, move);
  const logD = Math.log(CAM_WIDE.distance) + (Math.log(CAM_NEAR.distance) - Math.log(CAM_WIDE.distance)) * toNear;
  const cam = lerpCam(CAM_WIDE, CAM_NEAR, toNear, Math.exp(logD));
  const open = ramp(frame, fps, at("globe@4") - LINE_LEAD, 0.5, enter) * (1 - ramp(frame, fps, at("bars") - 1.1, 0.4, fade));
  const drill = ramp(frame, fps, at("globe@5") - LINE_LEAD, at("globe@7") - at("globe@5") + 0.4, enter);
  const axis = toVec(CITY).normalize();
  // The cut is fixed to the planet: opened toward the near camera's
  // direction and turned 0.6 rad off square, so its two faces read as depth.
  const cut = open > 0.001 ? wedge(axis, toVec([CAM_NEAR.lon, CAM_NEAR.lat]).normalize(), (Math.PI / 4) * open, 0.6) : null;
  const centre = windowed(frame, fps, at("globe@7") - LINE_LEAD, at("bars") - 1.1, 0.3, 0.3);
  const dug = ramp(frame, fps, at("globe@4") - LINE_LEAD, 0.4);

  const veil = followVeil(frame, fps, at("cta"));
  const quoteWords = ["There", "is", "grandeur", "in", "this", "view", "of", "life…"];
  // One literal cue per word, so recue.py can move each one.
  const quoteCues = ["quote@9", "quote@10", "quote@11", "quote@12", "quote@13", "quote@14", "quote@15", "quote@16"];

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.ink }}>
      {mapOn > 0 ? (
        <AbsoluteFill style={{ opacity: mapOn }}>
          <MapView
            plateKey={PLATE.name}
            makeProjection={PROJECTIONS[PLATE.name]}
            plateWidth={PLATE.w}
            plateHeight={PLATE.h}
            camera={{ center: [-30, 50.5], zoom: 2.0 }}
            raster={LOOK.raster}
            style={LOOK.style}
          >
            {(project, _scale, plate) => {
              const path = geoPath(plate.projection);
              const eqY = project([0, 0])[1] + pictureY;
              const tipAt = project([tip[0], tip[1]]);
              return (
                <>
                  <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
                    <CaptionClearDefs />
                    <g transform={`translate(0 ${pictureY}) ${plate.transform}`}>
                      <path d={path(GREENLAND) ?? ""} fill="none" stroke={COLORS.paper} strokeWidth={2} strokeDasharray="6 6" vectorEffect="non-scaling-stroke" opacity={0.6 * named * Math.min(1, t * 4)} />
                      {/* The cover's subject: what covercheck measures. */}
                      <g data-cover-subject>
                        <path d={path(moved) ?? ""} fill={COLORS.accent} fillOpacity={0.88 * named} stroke={COLORS.mark} strokeWidth={2} vectorEffect="non-scaling-stroke" />
                      </g>
                    </g>
                    <g mask="url(#captionClear)">
                      <Stroke d={`M 120 ${eqY} L 960 ${eqY}`} color={COLORS.cool} width={4} opacity={equator} />
                    </g>
                  </svg>
                  {bare ? null : (
                    <>
                      <MapLabel x={tipAt[0] + 14} y={tipAt[1] + pictureY} text="Greenland" align="left" dy={-30} opacity={named} />
                      <MapLabel x={120} y={eqY} text="Equator" dy={-58} color={COLORS.cool} opacity={equator} />
                    </>
                  )}
                </>
              );
            }}
          </MapView>
        </AbsoluteFill>
      ) : null}

      {globeOn > 0 ? (
        <GlobeView
          cam={cam}
          shiftY={140}
          opacity={globeOn}
          clip={cut ? cut.planes : undefined}
          clipIntersection
          scene={
            <>
              {cut ? cut.faces.map((out, i) => <SectionFace key={i} axis={axis} out={out} light={keyLight(cam)} />) : null}
              <Shaft from={CITY} t={drill} fadeBelow={1430} />
              <Opening at={CITY} o={dug} />
            </>
          }
        >
          {(project) => {
            const city = project(CITY);
            const c = project(CITY, 0);
            return bare ? null : (
              <>
                {city.visible ? <MapLabel x={city.x - 20} y={city.y} text="New York" align="right" dy={-48} size={36} /> : null}
                <MapLabel x={c.x + 28} y={c.y} text="Earth’s centre" align="left" dy={-22} size={34} opacity={centre} />
              </>
            );
          }}
        </GlobeView>
      ) : null}

      {bare ? null : (
        <>
          <AbsoluteFill style={{ opacity: beat("bars", "doc") }}>
            <KineticTitle text="Each bar as long | as its *value*" start={at("bars") - 0.4} size={88} style={{ position: "absolute", left: 100, right: 120, top: LAYOUT.top + 60 }} />
            {/* 780 wide, so no number reaches right of x 900 below y 1150,
                where the platform's buttons sit. */}
            <Bars
              y={820}
              width={780}
              rowGap={200}
              thickness={72}
              rows={[
                { label: "First", value: 40, text: "40", at: at("bars@5"), labelAt: at("bars@2") },
                { label: "Second", value: 75, text: "75", at: at("bars@6"), labelAt: at("bars@2") },
                { label: "Third", value: 100, text: "100", at: at("bars@8"), labelAt: at("bars@2") },
              ]}
            />
          </AbsoluteFill>

          <AbsoluteFill style={{ opacity: beat("doc", "quote") }}>
            <Document
              start={at("doc") - 0.3}
              at={at("doc@7")}
              y={430}
              heading="Chapter I"
              paragraphs={[
                "It is a truth universally acknowledged, that a single man in possession of a good fortune must be in want of a wife.",
                "However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.",
              ]}
              focus={0}
              focusY={0.3}
              credit="Jane Austen, Pride and Prejudice, 1813 (Project Gutenberg)"
            />
          </AbsoluteFill>

          <AbsoluteFill style={{ opacity: beat("quote", "timeline") }}>
            <Quote
              words={quoteWords}
              times={quoteCues.map(at)}
              attribution="Charles Darwin, On the Origin of Species, 1859"
              start={at("quote") - 0.3}
              y={560}
            />
          </AbsoluteFill>

          <AbsoluteFill style={{ opacity: beat("timeline", "logo") }}>
            <KineticTitle text="Drawn *to scale*" start={at("timeline") - 0.4} size={96} style={{ position: "absolute", left: 100, right: 120, top: LAYOUT.top + 60 }} />
            <Timeline
              from={1800}
              to={1900}
              step={25}
              start={at("timeline@2") - LINE_LEAD}
              y={980}
              events={[
                { year: 1813, label: "Pride and Prejudice", at: at("timeline@6") },
                { year: 1859, label: "On the Origin of Species", at: at("timeline@10"), below: true },
              ]}
            />
          </AbsoluteFill>

          <AbsoluteFill style={{ opacity: beat("logo", "cta") }}>
            <Logo name="Example Company" at={at("logo@2")} mark={<PlaceholderMark />} credit="A placeholder mark, not a real company" y={800} />
          </AbsoluteFill>

          <Badge part={1} opacity={1 - veil} />
          <KineticTitle
            text="Can one script | drive *every word* | you see?"
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
              // "Videos like this" points at the video: one of its pictures
              // stays in view, small, above the profile.
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
