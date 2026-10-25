import { useEffect } from "react";
import { continueRender, delayRender, getInputProps } from "remotion";

// QA only (input prop `coverProbe: true`, see scripts/covers.mjs): after the
// cover is laid out, measures the title block (every `data-cover-title`) and the
// picture's subject, the union of everything visible inside
// `data-cover-subject`, and logs them as "COVER|<json>", boxes as
// [left, top, right, bottom] in frame pixels. pipeline/covercheck.py holds
// the rules they are checked against.
const ON = Boolean((getInputProps() as { coverProbe?: boolean }).coverProbe);

type Box = [number, number, number, number];

// A straight level or upright line has a box of zero height or width and
// still counts: skipping it once left a cover's whole equator line out of
// its measured subject.
const union = (a: Box | null, r: DOMRect): Box | null => {
  if (r.width <= 0 && r.height <= 0) return a;
  const b: Box = [r.left, r.top, r.right, r.bottom];
  return a ? [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])] : b;
};

// Opacity as seen: the product of every ancestor's.
const seen = (el: Element | null): number => {
  let o = 1;
  for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity);
  return o;
};

const textBox = (root: Element, minOpacity: number): Box | null => {
  let box: Box | null = null;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.textContent?.trim() || seen(n.parentElement) < minOpacity) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    for (const rect of r.getClientRects()) box = union(box, rect);
  }
  return box;
};

const SHAPES = "path, circle, ellipse, line, polyline, polygon, rect";

const shapeBox = (root: Element, minOpacity: number): Box | null => {
  let box: Box | null = null;
  for (const el of root.querySelectorAll(SHAPES)) {
    const cs = getComputedStyle(el);
    const paint = (cs.fill !== "none" && Number(cs.fillOpacity) > minOpacity) || (cs.stroke !== "none" && Number(cs.strokeOpacity) > minOpacity);
    if (!paint || seen(el) < minOpacity) continue;
    box = union(box, el.getBoundingClientRect());
  }
  return box;
};

const merge = (a: Box | null, b: Box | null): Box | null =>
  a && b ? [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])] : (a ?? b);

const measure = () => {
  // The title is every block marked `data-cover-title` (a title set in
  // parts: only the first part was measured once, and a cover whose last
  // line ran into its picture passed).
  let title: Box | null = null;
  for (const el of document.querySelectorAll("[data-cover-title]")) title = merge(title, textBox(el, 0.05));
  let subject: Box | null = null;
  for (const el of document.querySelectorAll("[data-cover-subject]")) subject = merge(subject, merge(shapeBox(el, 0.05), textBox(el, 0.05)));
  const round = (b: Box | null) => (b ? b.map((v) => Math.round(v)) : null);
  console.log(`COVER|${JSON.stringify({ title: round(title), subject: round(subject) })}`);
};

export const CoverProbe: React.FC = () => {
  useEffect(() => {
    if (!ON) return;
    const handle = delayRender("cover probe");
    // Two frames: fonts and layout settle before measuring.
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        measure();
        continueRender(handle);
      }),
    );
  });
  return null;
};
