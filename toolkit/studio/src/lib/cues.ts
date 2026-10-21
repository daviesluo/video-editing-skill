// Cue lookup, free of Remotion so tests and scripts can run it in Node.
// Scenes and sound effects key off words, never seconds: "seg" is the
// segment's first word, "seg@k" its k-th word (from 0), "seg$" the end of
// its last word. When the narration is re-voiced or re-timed, every cue
// follows its word; a hard-coded second would not.

export type Word = { text: string; start: number; end: number };
export type TimedWord = Word & { seg: string };
export type Segment = { start: number; end: number; first: number; last: number };
export type Timeline = {
  duration: number;
  words: TimedWord[];
  segments: Record<string, Segment>;
  // Phrases the captions never split across pages (episode.json caption_keep).
  keep?: string[];
  // Hyphenated words the captions may break after the hyphen (caption_split).
  split?: string[];
};

export const cueAt = (tl: Timeline, lead: number, cue: string): number => {
  const m = /^([\w-]+)(?:@(\d+)|(\$))?$/.exec(cue);
  if (!m) throw new Error(`bad cue ${cue}`);
  const seg = tl.segments[m[1]];
  if (!seg) throw new Error(`no segment ${m[1]}`);
  if (m[3]) return lead + seg.end;
  const k = Number(m[2] ?? 0);
  // A cue past its own sentence is a stale word number left by a wording
  // change (pipeline/recue.py moves cues with their words).
  if (seg.first + k > seg.last) throw new Error(`cue ${cue} is past the end of its segment (${seg.last - seg.first + 1} words)`);
  return lead + tl.words[seg.first + k].start;
};

export const shiftWords = (tl: Timeline, lead: number): Word[] =>
  tl.words.map((w) => ({ text: w.text, start: w.start + lead, end: w.end + lead }));
