import type { CalculateMetadataFunction } from "remotion";
import { staticFile } from "remotion";
import { FRAME } from "../brand/tokens";
import type { Timeline } from "./cues";

export { cueAt, shiftWords } from "./cues";
export type { Segment, Timeline, TimedWord, Word } from "./cues";

export type EpisodeProps = {
  id: string;
  lead: number;
  tail: number;
  qa: boolean;
  timeline?: Timeline;
  // Leaves out every text overlay, for covers.
  bare?: boolean;
  // Covers only: moves the picture's subject down, px, leaving the page and
  // its scrims where they are (shifting the whole frame shows a band of
  // empty page at the top).
  pictureY?: number;
};

// The duration comes from the narration: lead-in + voice + tail. The
// timeline is fetched here so a composition without a voice yet still
// bundles.
export const episodeMetadata: CalculateMetadataFunction<EpisodeProps> = async ({ props }) => {
  const res = await fetch(staticFile(`episodes/${props.id}/timeline.json`));
  if (!res.ok) throw new Error(`No timeline for ${props.id}: run pipeline/build.py voice first`);
  const timeline = (await res.json()) as Timeline;
  return {
    durationInFrames: Math.ceil((props.lead + timeline.duration + props.tail) * FRAME.fps),
    props: { ...props, timeline },
  };
};
