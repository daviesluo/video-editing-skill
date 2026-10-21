// Lists every caption page of an episode, flagging a page of one word that
// follows an unfinished page (the "Follow for part" / "2." failure):
//   node --experimental-strip-types scripts/caption-pages.ts <id> [...]
// Read every page before rendering; a page that splits a phrase the eye
// reads as one unit ("in the" / "South Pacific") goes into caption_keep.
import fs from "node:fs";
import path from "node:path";
import { lineWidth, paginate } from "../src/kit/paginate.ts";

for (const id of process.argv.slice(2)) {
  const tl = JSON.parse(fs.readFileSync(path.resolve("public/episodes", id, "timeline.json"), "utf8"));
  const pages = paginate(tl.words, tl.keep ?? [], tl.split ?? []);
  console.log(`== ${id}: ${pages.length} pages`);
  pages.forEach((p, i) => {
    const text = p.words.map((w) => w.text).join(" ");
    const prev = pages[i - 1];
    const lone = p.words.length === 1 && !/[.,?!;:—]$/.test(prev?.words[prev.words.length - 1].text ?? ".");
    const flag = lone ? "  <- one word after an unfinished page" : "";
    const size = p.scale < 1 ? `  (${Math.round(p.scale * 100)}%)` : "";
    const px = String(Math.round(lineWidth(p.words.map((w) => w.text)) * p.scale)).padStart(4);
    console.log(`${p.start.toFixed(2).padStart(6)}  ${px}px  ${text}${size}${flag}`);
  });
}
