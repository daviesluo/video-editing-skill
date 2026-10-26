import { useEffect } from "react";
import { continueRender, delayRender, getInputProps } from "remotion";
import { SAFE } from "../brand/tokens";
import { CHARS } from "./archivoChars";

// QA only (input prop `orphans: true`, see scripts/stills.mjs): after the
// frame is laid out, finds every block of text with a line that holds a
// single word, and logs it as "ORPHAN|<text>". A line never ends with one
// word alone on it: a lone last word reads as a layout accident, and it is
// checked by measurement because the eye misses it on a contact sheet. A
// block is either a wrapping flex row of word items (captions), a row of
// inline-block word masks (KineticTitle), or the lowest element holding
// the text with only inline content (labels, body text, sources).
const ON = Boolean((getInputProps() as { orphans?: boolean }).orphans);

type Word = { text: string; top: number; height: number };

const lines = (words: Word[]): Word[][] => {
  const out: Word[][] = [];
  for (const w of words) {
    const cur = out[out.length - 1];
    if (cur && Math.abs(w.top - cur[0].top) < cur[0].height * 0.5) cur.push(w);
    else out.push([w]);
  }
  return out;
};

const textWords = (el: Element): Word[] => {
  const words: Word[] = [];
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent ?? "";
    for (const m of text.matchAll(/\S+/g)) {
      const r = document.createRange();
      r.setStart(n, m.index ?? 0);
      r.setEnd(n, (m.index ?? 0) + m[0].length);
      const box = r.getClientRects()[0];
      if (box && box.width > 0) words.push({ text: m[0], top: box.top, height: box.height });
    }
  }
  return words;
};

const inlineOnly = (el: Element) =>
  [...el.querySelectorAll("*")].every((c) => getComputedStyle(c).display.startsWith("inline") && getComputedStyle(c).display !== "inline-flex");

const scan = () => {
  const found = new Set<string>();
  for (const el of document.querySelectorAll("div, span, p, b")) {
    // A line still typing in (marked data-typing) is judged once it is
    // whole: lines that grow from the centre leave a word alone for a beat.
    // A news excerpt set large in a narrow column (marked data-excerpt)
    // holds one word a line as a matter of course (the owner, 2026-10-26).
    if (el.closest("[data-typing], [data-excerpt]")) continue;
    const cs = getComputedStyle(el);
    let words: Word[] = [];
    if (cs.display.includes("flex") && cs.flexWrap === "wrap") {
      words = [...el.children]
        .map((c) => ({ text: (c.textContent ?? "").trim(), box: c.getBoundingClientRect() }))
        .filter((c) => c.text && c.box.width > 0)
        .map((c) => ({ text: c.text, top: c.box.top, height: c.box.height }));
    } else if (
      !cs.display.startsWith("inline") &&
      el.children.length >= 2 &&
      ![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent?.trim()) &&
      [...el.children].filter((c) => c.tagName !== "BR").every((c) => getComputedStyle(c).display === "inline-block")
    ) {
      // A headline set word by word (kit/Type.tsx KineticTitle): each word is
      // an inline-block mask whose own box does not move while the word
      // rises inside it, so its lines are measured on the masks. A probe
      // that skipped these once let "The Julian / calendar" through.
      words = [...el.children]
        .map((c) => ({ text: (c.textContent ?? "").trim(), box: c.getBoundingClientRect() }))
        .filter((c) => c.text && c.box.width > 0)
        .map((c) => ({ text: c.text, top: c.box.top, height: c.box.height }));
    } else if (!cs.display.startsWith("inline") && (el.textContent ?? "").trim() && inlineOnly(el)) {
      // The lowest block holding text, whether its words are its own text
      // or sit in inline spans (a line typed a word at a time sets each
      // word in a span; a probe that wanted the block's own text skipped
      // those).
      words = textWords(el);
    }
    const ls = lines(words);
    // Any line of one word, not only the last: a title set in forced lines
    // left one word alone in its middle, and a last-line test passed it.
    if (ls.length >= 2 && ls.some((l) => l.length === 1)) found.add(words.map((w) => w.text).join(" "));
  }
  for (const t of found) console.log(`ORPHAN|${t}`);
};

// Text the platform's own interface would cover or the player would crop
// (SAFE in brand.json): every visible run of text must sit inside the box
// and clear of the right-hand button column. Logged as
// "UNSAFE|<text>|<left>,<top>,<right>,<bottom>".
const seenOpacity = (el: Element | null): number => {
  let o = 1;
  for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity);
  return o;
};

const unsafe = () => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent?.trim();
    if (!text || seenOpacity(n.parentElement) < 0.05) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    const rects = [...r.getClientRects()].filter((b) => b.width > 0 && b.height > 0);
    if (!rects.length) continue;
    let [l, t, rt, b] = [Math.min(...rects.map((x) => x.left)), Math.min(...rects.map((x) => x.top)), Math.max(...rects.map((x) => x.right)), Math.max(...rects.map((x) => x.bottom))];
    // What a mask (an ancestor with overflow hidden) cuts away is not seen.
    for (let e = n.parentElement; e; e = e.parentElement) {
      if (getComputedStyle(e).overflow === "visible") continue;
      const c = e.getBoundingClientRect();
      [l, t, rt, b] = [Math.max(l, c.left), Math.max(t, c.top), Math.min(rt, c.right), Math.min(b, c.bottom)];
    }
    if (rt - l < 2 || b - t < 2) continue;
    // Wholly off the frame (a label on the far side of a map) is not seen.
    if (rt < 0 || l > 1080 || b < 0 || t > 1920) continue;
    const rail = rt > SAFE.railX && b > SAFE.railY && t < SAFE.bottom;
    if (t < SAFE.top || b > SAFE.bottom || l < SAFE.left || rt > SAFE.right || rail)
      console.log(`UNSAFE|${text}|${[l, t, rt, b].map((v) => Math.round(v)).join(",")}`);
  }
};

// Every visible character must be one the vendored face can set: anything
// else falls back to another font, which breaks the one-typeface rule and
// can differ between machines. Logged as "GLYPH|<char>|<text>".
const SETTABLE = new Set([...CHARS, "\n", "\t"]);
const glyphs = () => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set<string>();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent ?? "";
    if (!text.trim() || seenOpacity(n.parentElement) < 0.05) continue;
    for (const ch of text) {
      if (SETTABLE.has(ch) || seen.has(ch)) continue;
      seen.add(ch);
      console.log(`GLYPH|${ch}|${text.trim()}`);
    }
  }
};

// Page type that runs into a picture: text set on the page (not marked
// data-on-picture, as subtitles and credits set on a clip on purpose are)
// whose letters meet the box of an element marked data-picture (a photo or
// clip layer), as clipped by its masks. Logged as "CLASH|<text>|<overlap
// in px>". A framing change once laid a photo's edge across the last line
// for 2.3 s, and no other check could see it.
const visibleBox = (el: Element) => {
  let { left: l, top: t, right: rt, bottom: b } = el.getBoundingClientRect();
  for (let e = el.parentElement; e; e = e.parentElement) {
    if (getComputedStyle(e).overflow === "visible") continue;
    const c = e.getBoundingClientRect();
    [l, t, rt, b] = [Math.max(l, c.left), Math.max(t, c.top), Math.min(rt, c.right), Math.min(b, c.bottom)];
  }
  return { l, t, rt, b };
};

const clash = () => {
  const pictures = [...document.querySelectorAll("[data-picture]")].filter((p) => seenOpacity(p) >= 0.05).map(visibleBox).filter((p) => p.rt - p.l > 1 && p.b - p.t > 1);
  if (!pictures.length) return;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent?.trim();
    const own = n.parentElement;
    if (!text || !own || seenOpacity(own) < 0.05 || own.closest("[data-picture], [data-on-picture]")) continue;
    const range = document.createRange();
    range.selectNodeContents(n);
    let worst = 0;
    for (const box of range.getClientRects()) {
      // The letters, not the line box: a tenth off the top and the bottom.
      const t = box.top + box.height * 0.1;
      const b = box.bottom - box.height * 0.1;
      for (const p of pictures) {
        const w = Math.min(box.right, p.rt) - Math.max(box.left, p.l);
        const h = Math.min(b, p.b) - Math.max(t, p.t);
        if (w > 0 && h > 0) worst = Math.max(worst, Math.round(h));
      }
    }
    if (worst > 0) console.log(`CLASH|${text}|${worst}`);
  }
};

export const OrphanProbe: React.FC = () => {
  useEffect(() => {
    if (!ON) return;
    const handle = delayRender("orphan probe");
    // Two frames: fonts and layout settle before measuring.
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        scan();
        unsafe();
        glyphs();
        clash();
        // Proof the probe ran on this still: scripts/stills.mjs fails a
        // still without it. A composition that stopped mounting the probe
        // once "passed" every scan with six texts outside the box.
        console.log("PROBE|ok");
        continueRender(handle);
      }),
    );
  });
  return null;
};
