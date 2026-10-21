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
// timeline is fetched here, so a composition has no length until
// build.py <ep> voice has written it.
export const episodeMetadata: CalculateMetadataFunction<EpisodeProps> = async ({ props }) => {
  const res = await fetch(staticFile(`episodes/${props.id}/timeline.json`));
  if (!res.ok) throw new Error(`No timeline for ${props.id}: run pipeline/build.py voice first`);
  const timeline = (await res.json()) as Timeline;
  // The lead-in and tail come from episode.json, copied into the timeline
  // by build.py, so stills, covers and the render can never disagree on
  // them; the props are only a fallback.
  const lead = timeline.lead ?? props.lead;
  const tail = timeline.tail ?? props.tail;
  return {
    durationInFrames: Math.ceil((lead + timeline.duration + tail) * FRAME.fps),
    props: { ...props, lead, tail, timeline },
  };
};
