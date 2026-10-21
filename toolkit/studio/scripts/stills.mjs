// Renders stills of one composition at several times from a single bundle,
// for design review, the picture audit and QA. Times are seconds of video.
//   node scripts/stills.mjs <composition> <outDir> <t1,t2,...|every:0.5> [propsJson]
// With ORPHANS=1 the orphan and safe-zone probe runs on every still and
// prints "ORPHAN <time> <text>" for a block whose last line holds one word
// "UNSAFE <time> <text>|<box>" for text outside the safe box, and "GLYPH
// <time> <char>|<text>" for a character the vendored face cannot set. Scan
// the whole episode every 0.5 s, and every cover, before any render; it
// must report 0 findings.
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [id, outDir, times, propsJson] = process.argv.slice(2);
if (!id || !outDir || !times) {
  console.error("usage: node scripts/stills.mjs <composition> <outDir> <t1,t2,...|every:0.5> [propsJson]");
  process.exit(2);
}
const inputProps = { ...(propsJson ? JSON.parse(propsJson) : {}), ...(process.env.ORPHANS ? { orphans: true } : {}) };
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions: { gl: "swangle" } });
const seconds = (composition.durationInFrames - 1) / composition.fps;
const list = times.startsWith("every:")
  ? Array.from({ length: Math.floor(seconds / Number(times.slice(6))) + 1 }, (_, k) => k * Number(times.slice(6)))
  : times.split(",").map(Number);
let hits = 0;
for (const t of list) {
  const frame = Math.min(composition.durationInFrames - 1, Math.max(0, Math.round(t * composition.fps)));
  const output = path.resolve(outDir, `${id}-${t.toFixed(2)}.png`);
  await renderStill({
    composition,
    serveUrl,
    output,
    frame,
    inputProps,
    chromiumOptions: { gl: "swangle" },
    onBrowserLog: (log) => {
      for (const kind of ["ORPHAN", "UNSAFE", "GLYPH"]) {
        if (log.text.startsWith(`${kind}|`)) {
          hits++;
          console.log(`${kind} ${t.toFixed(2)} ${log.text.slice(kind.length + 1)}`);
        }
      }
    },
  });
  if (!process.env.ORPHANS) console.log(output);
}
// Each bundle is about 100 MB in the temporary folder; left behind, a day
// of stills fills the disk.
fs.rmSync(serveUrl, { recursive: true, force: true });
if (process.env.ORPHANS) console.log(`${list.length} stills scanned, ${hits} findings`);
process.exit(hits ? 1 : 0);
