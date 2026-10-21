import { EM } from "./archivo800.ts";

// Caption pages: what the Captions component shows at once. Kept free of
// React and Remotion, so scripts/caption-pages.ts can list every page of an
// episode and bin/selftest.sh can test the rules in plain Node.
//
// The rules, and why: a page holds up to three words that fit one line; a
// word is never left alone on a page unless it is its whole phrase ("Follow
// for part" then "2." is the failure this exists for); a number stays with
// the word after it; a page never ends on a word that belongs to the next
// ("a", "an", "no"); a phrase the episode keeps whole ("Reno, Nevada") is
// one page even across a comma; and a page may be set at 92 to 80 percent
// size rather than strand a word.

export type Word = { text: string; start: number; end: number };
// `scale` sets the page a little smaller when that keeps it on one line
// instead of leaving a word alone on the next page.
export type Page = { words: Word[]; start: number; end: number; scale: number };

export const MAX_WORDS = 3;
export const SIZE = 76;
export const TRACK = -0.01;
export const GAP = 0.28;
// The caption box is 680 px wide; a page must fit on one line with room
// to spare, or it wraps and leaves one word alone on a line. The widths
// leave out kerning, which only narrows a line.
const FIT = 660;
// Page sizes, largest first, with the cost of each step down. A smaller
// page costs more than one more page (10) but less than a word left alone
// (15), so size drops only to keep a word company.
const SCALES: [number, number][] = [
  [1, 0],
  [0.92, 11],
  [0.86, 12],
  [0.8, 13],
];

// Width in px of a page set in the caption face (Archivo 800), from the
// font's own advance widths (pipeline/fontwidths.py), with the gap the
// row puts between words.
const widths = EM as Record<string, number>;
export const lineWidth = (ws: string[]) =>
  (ws.reduce((w, t) => w + [...t].reduce((a, c) => a + (widths[c] ?? 0.6) + TRACK, 0), 0) + GAP * (ws.length - 1)) * SIZE;

const NUMBER = /^[≈~]?\d[\d,.]*$/;
// A page should not end on a word that belongs to the next one: "eleven
// dates no" then "one in Britain" split "no one", and "Follow for a" left
// the article hanging. "a", "an" and "no" cost almost as much
// as a word left alone; other articles and prepositions only tip a tie, so
// a short "When the" still beats splitting "space station".
const BIND_HARD = new Set(["a", "an", "no"]);
const BIND = new Set(["the", "its", "their", "his", "her", "my", "our", "your", "every", "to", "of", "in", "on", "at", "for", "from", "by", "with", "and", "or", "than", "into"]);
const binds = (w: string) => {
  const k = w.toLowerCase().replace(/[^a-z]/g, "");
  return BIND_HARD.has(k) ? 11 : BIND.has(k) ? 1 : 0;
};

const splitPhrase = (ws: Word[], held: (i: number) => boolean = () => false): { words: Word[]; scale: number }[] => {
  const n = ws.length;
  const best: { cost: number; from: number; scale: number }[] = [{ cost: 0, from: -1, scale: 1 }];
  for (let i = 1; i <= n; i++) {
    best[i] = { cost: Infinity, from: -1, scale: 1 };
    // Up to two words more than MAX_WORDS only for a phrase the episode
    // keeps whole ("has two birth dates": "has two" then "birth dates"
    // parted a number from its noun; "4 feet 8" then "and a half inches"
    // showed a figure that was never said).
    for (let j = Math.max(0, i - MAX_WORDS - 2); j < i; j++) {
      if (i - j > MAX_WORDS && !Array.from({ length: i - j - 1 }, (_, k) => held(j + 1 + k)).every(Boolean)) continue;
      const page = ws.slice(j, i);
      const w = lineWidth(page.map((x) => x.text));
      const fit = SCALES.find(([k]) => w * k <= FIT) ?? (page.length === 1 ? [1, 0] : undefined);
      if (!fit) continue;
      const pause = j > 0 ? Math.min(1, Math.max(0, ws[j].start - ws[j - 1].end) / 0.5) : 0;
      const cost =
        best[j].cost +
        10 +
        fit[1] +
        (page.length === 1 && n > 1 ? 15 : 0) +
        (j > 0 && NUMBER.test(ws[j - 1].text) ? 3 : 0) +
        (i < n ? binds(ws[i - 1].text) : 0) +
        (i < n && held(i) ? 40 : 0) -
        2 * pause;
      if (cost < best[i].cost) best[i] = { cost, from: j, scale: fit[0] };
    }
  }
  const pages: { words: Word[]; scale: number }[] = [];
  for (let i = n; i > 0; i = best[i].from) pages.unshift({ words: ws.slice(best[i].from, i), scale: best[i].scale });
  return pages;
};

// Words that read as one unit stay on one page: each episode lists them
// ("a new one", "the 2nd", "space station") as `caption_keep` in its
// episode.json, which build.py copies into the timeline as `keep`.
const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9’']/g, "");
const heldBreaks = (words: Word[], keep: string[]): Set<number> => {
  const held = new Set<number>();
  const ws = words.map((w) => norm(w.text));
  for (const phrase of keep) {
    const p = phrase.split(/\s+/).map(norm).filter(Boolean);
    for (let s = 0; s + p.length <= ws.length; s++) {
      if (p.every((x, k) => ws[s + k] === x)) for (let k = 1; k < p.length; k++) held.add(s + k);
    }
  }
  return held;
};

// Pages break on punctuation, then as splitPhrase chooses, so the caption
// follows the voice's phrasing instead of an even split.
// A compound too long to share a line with its neighbours ("gauge-changing
// tracks," does not fit even at 80 %) may be listed in `split`: it is then
// set as two caption words broken after its hyphen, "gauge-" and
// "changing", the time shared by letters, so neither half is left alone on
// a page (episode.json caption_split).
const splitCompounds = (words: Word[], split: string[]): Word[] =>
  words.flatMap((w) => {
    const bare = w.text.replace(/[^\p{L}\p{N}-]/gu, "");
    const at = w.text.indexOf("-");
    if (!split.includes(bare) || at < 1) return [w];
    const a = w.text.slice(0, at + 1);
    const b = w.text.slice(at + 1);
    const mid = w.start + ((w.end - w.start) * a.length) / w.text.length;
    return [
      { ...w, text: a, end: mid },
      { ...w, text: b, start: mid },
    ];
  });

export const paginate = (input: Word[], keep: string[] = [], split: string[] = []): Page[] => {
  const words = splitCompounds(input, split);
  const held = heldBreaks(words, keep);
  const phrases: { ws: Word[]; from: number }[] = [];
  let cur: Word[] = [];
  let from = 0;
  words.forEach((w, i) => {
    if (!cur.length) from = i;
    cur.push(w);
    const next = words[i + 1];
    // A kept phrase runs across a comma ("Reno, Nevada").
    if (!next || (/[.,?!;:—]$/.test(w.text) && !held.has(i + 1))) {
      phrases.push({ ws: cur, from });
      cur = [];
    }
  });
  return phrases
    .flatMap(({ ws, from: f }) => splitPhrase(ws, (i) => held.has(f + i)))
    .map(({ words: ws, scale }) => ({ words: ws, start: ws[0].start, end: ws[ws.length - 1].end, scale }));
};
