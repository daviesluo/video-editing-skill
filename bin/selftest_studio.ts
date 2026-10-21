// Copyright 2026 The video-editing-skill authors. Licensed under the Apache
// License 2.0, whose text is the LICENSE file in this package.
//
// Unit tests for the studio's pure modules: caption pagination and word
// cues. Run by bin/selftest.sh, which counts the "ok" and "FAIL" lines; it
// can also run alone, with Node 22.18 or newer and nothing installed:
//
//   node --experimental-strip-types bin/selftest_studio.ts

import { lineWidth, paginate, type Page, type Word } from "../toolkit/studio/src/kit/paginate.ts";
import { cueAt, type Timeline } from "../toolkit/studio/src/lib/cues.ts";

let passed = 0;
let failed = 0;
const fail = (msg: string): never => {
  throw new Error(msg);
};
const check = (label: string, fn: () => void) => {
  try {
    fn();
    passed++;
    console.log(`  ok   ${label}`);
  } catch (e) {
    failed++;
    console.log(`  FAIL ${label}: ${(e as Error).message}`);
  }
};

// Words of a sentence, evenly timed, with a longer gap after punctuation.
const words = (text: string): Word[] => {
  let t = 0;
  return text.split(" ").map((w) => {
    const word = { text: w, start: t, end: t + 0.3 };
    t += /[.,?!:;]$/.test(w) ? 0.65 : 0.36;
    return word;
  });
};
const show = (pages: Page[]) => pages.map((p) => p.words.map((w) => w.text).join(" "));
const FIT = 660;

console.log("captions: pages that never strand a word");

check("a kept phrase stays on one page across its comma ('Reno, Nevada,')", () => {
  const pages = show(paginate(words("Next, in part 6: is Reno, Nevada, east or west of Los Angeles?"), ["Reno, Nevada", "Los Angeles"]));
  if (!pages.some((p) => p.includes("Reno, Nevada,"))) fail(pages.join(" / "));
  if (pages.includes("Nevada,")) fail(pages.join(" / "));
});

check("without the keep, the comma ends the phrase and 'Nevada,' stands alone", () => {
  const pages = show(paginate(words("is Reno, Nevada, east or west of Los Angeles?"), []));
  if (!pages.includes("Nevada,")) fail(pages.join(" / "));
});

check("'Follow for part 2.' never leaves '2.' alone on a page", () => {
  const pages = show(paginate(words("Enjoy stories like this? Follow for part 2.")));
  if (pages.some((p) => p === "2.")) fail(pages.join(" / "));
});

check("no page holds one word inside a longer phrase", () => {
  const text =
    "From London, you’d come out in the South Pacific, just over 200 kilometres from the Antipodes Islands, named because they lie near London’s opposite point.";
  const ws = words(text);
  const pages = paginate(ws, ["South Pacific", "the Antipodes Islands", "200 kilometres"]);
  pages.forEach((p, i) => {
    const prev = pages[i - 1];
    const prevEnd = prev ? prev.words[prev.words.length - 1].text : ".";
    if (p.words.length === 1 && !/[.,?!;:]$/.test(prevEnd) && !/[.,?!;:]$/.test(p.words[0].text)) fail(`"${p.words[0].text}" alone`);
  });
});

check("a number stays with the word after it", () => {
  const pages = paginate(words("Only about 800 km² of it has land on the other side."), ["of it has land"]);
  for (const p of pages) {
    const last = p.words[p.words.length - 1].text;
    if (/^\d[\d,.]*$/.test(last)) fail(`page ends on the number: ${show(pages).join(" / ")}`);
  }
});

check("a page never ends on 'a', 'an' or 'no' inside a phrase", () => {
  for (const text of ["Eleven dates no one in Britain ever lived.", "Follow for a new one every day."]) {
    const pages = show(paginate(words(text)));
    if (pages.slice(0, -1).some((p) => /\b(a|an|no)$/i.test(p))) fail(pages.join(" / "));
  }
});

check("every page fits the caption line at its size", () => {
  const text = "The International Space Station passes over, and its crew are closer to it than anyone on land.";
  for (const p of paginate(words(text), ["International Space Station"])) {
    const w = lineWidth(p.words.map((x) => x.text)) * p.scale;
    if (p.words.length > 1 && w > FIT) fail(`${show([p])} is ${Math.round(w)} px`);
  }
});

check("a page is set smaller (92 to 80 percent) rather than strand a word", () => {
  // "Kerguelen Islands." is about 706 px at full size, over the 660 px line.
  const pages = paginate(words("Kerguelen Islands."), []);
  if (pages.length !== 1 || pages[0].scale !== 0.92) fail(show(pages).join(" / ") + ` at ${pages.map((p) => p.scale)}`);
});

check("pages keep every word, in order, and time each page by its words", () => {
  const ws = words("Dig straight down into the Earth. Where would you come out on the other side?");
  const pages = paginate(ws, ["on the other side"]);
  const flat = pages.flatMap((p) => p.words.map((w) => w.text));
  if (flat.join(" ") !== ws.map((w) => w.text).join(" ")) fail(flat.join(" "));
  for (const p of pages) if (p.start !== p.words[0].start || p.end !== p.words[p.words.length - 1].end) fail("page times");
});

check("a listed compound breaks after its hyphen, its time shared by letters", () => {
  const ws = words("Trains use special gauge-changing tracks.");
  const pages = paginate(ws, [], ["gauge-changing"]);
  const flat = pages.flatMap((p) => p.words);
  const a = flat.find((w) => w.text === "gauge-");
  const b = flat.find((w) => w.text === "changing");
  if (!a || !b) fail(show(pages).join(" / "));
  if (a!.end !== b!.start || !(a!.start < a!.end && b!.start < b!.end)) fail("times");
});

console.log("cues: every time comes from a word");

const tl: Timeline = {
  duration: 4,
  words: [
    { text: "Dig", seg: "hook", start: 0.0, end: 0.3 },
    { text: "down.", seg: "hook", start: 0.4, end: 0.8 },
    { text: "Where", seg: "next", start: 2.0, end: 2.3 },
    { text: "now?", seg: "next", start: 2.4, end: 2.9 },
  ],
  segments: {
    hook: { start: 0.0, end: 0.8, first: 0, last: 1 },
    next: { start: 2.0, end: 2.9, first: 2, last: 3 },
  },
};

check("'seg', 'seg@k' and 'seg$' resolve to words, with the lead added", () => {
  const near = (a: number, b: number) => Math.abs(a - b) < 1e-9;
  if (!near(cueAt(tl, 0.3, "next"), 2.3)) fail("seg");
  if (!near(cueAt(tl, 0.3, "next@1"), 2.7)) fail("seg@k");
  if (!near(cueAt(tl, 0.3, "hook$"), 1.1)) fail("seg$");
});

check("a stale cue past its segment, or an unknown segment, is refused", () => {
  for (const bad of ["hook@2", "nope", "hook@x"]) {
    let threw = false;
    try {
      cueAt(tl, 0, bad);
    } catch {
      threw = true;
    }
    if (!threw) fail(`${bad} was accepted`);
  }
});

console.log(`TS ${passed} ${failed}`);
process.exit(failed ? 1 : 0);
