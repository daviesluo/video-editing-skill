import { Composition } from "remotion";
import "./brand/fonts";
import { FRAME } from "./brand/tokens";
import { Cover, coverMetadata, type CoverProps } from "./brand/Cover";
import { Example } from "./episodes/Example";
import { CutAwayLab, LAB_DEFAULTS } from "./lab/CutAwayLab";
import { episodeMetadata } from "./lib/episode";

// Each episode is a composition whose length comes from its narration, and
// each has a cover composition, Cover<NN>, that freezes one of its frames.
// The lead-in and tail are read from the timeline (build.py copies them
// from episode.json); the numbers here are only a fallback.
const EP = { fps: FRAME.fps, width: FRAME.width, height: FRAME.height, durationInFrames: 600 } as const;

const COVERS: CoverProps[] = [
  { id: "00-example", ep: "Example", part: 1, cue: "map@6", offset: 0.4, title: "Can one script drive | *every word?*", size: 104, lead: 0.3, tail: 1.4, qa: false, pictureY: 60 },
];

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Example" component={Example} {...EP} defaultProps={{ id: "00-example", lead: 0.3, tail: 1.4, qa: false }} calculateMetadata={episodeMetadata} />
    {/* A lab: one still per set of props (scripts/variants.mjs), to explore
        a design away from any episode. */}
    <Composition id="CutAwayLab" component={CutAwayLab} {...EP} durationInFrames={1} defaultProps={LAB_DEFAULTS} />
    {COVERS.map((c) => (
      <Composition key={c.id} id={`Cover${c.id.slice(0, 2)}`} component={Cover} {...EP} durationInFrames={1} defaultProps={c} calculateMetadata={coverMetadata} />
    ))}
  </>
);
