import { Composition } from "remotion";
import "./brand/fonts";
import { FRAME } from "./brand/tokens";
import { Cover, coverMetadata, type CoverProps } from "./brand/Cover";
import { Example } from "./episodes/Example";
import { episodeMetadata } from "./lib/episode";

// Each episode is a composition whose length comes from its narration, and
// each has a cover composition, Cover<NN>, that freezes one of its frames.
// lead and tail must match episode.json's audio_lead and tail, which the
// mix uses.
const EP = { fps: FRAME.fps, width: FRAME.width, height: FRAME.height, durationInFrames: 600 } as const;

const COVERS: CoverProps[] = [
  { id: "00-example", ep: "Example", part: 1, cue: "map@6", offset: 0.4, title: "Can one script drive | *every word?*", size: 104, lead: 0.3, tail: 1.4, qa: false, pictureY: 60 },
];

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Example" component={Example} {...EP} defaultProps={{ id: "00-example", lead: 0.3, tail: 1.4, qa: false }} calculateMetadata={episodeMetadata} />
    {COVERS.map((c) => (
      <Composition key={c.id} id={`Cover${c.id.slice(0, 2)}`} component={Cover} {...EP} durationInFrames={1} defaultProps={c} calculateMetadata={coverMetadata} />
    ))}
  </>
);
