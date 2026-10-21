// Renders covers from one bundle into ../covers/, each with its measured
// layout beside it (kit/CoverProbe.tsx), then checks them against the cover
// rules (pipeline/covercheck.py):
//   node scripts/covers.mjs [Cover01,Cover02,...] [outDir]
// Without ids it renders every composition whose id starts with "Cover".
// Exits non-zero if a cover breaks a rule. Look at each cover at full size
// and in the 3:4 tile as well: the check measures geometry, not whether a
// frame caught something mid-fade.
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [ids, outArg] = process.argv.slice(2);
const outDir = path.resolve(outArg ?? "../covers");
fs.mkdirSync(outDir, { recursive: true });
const inputProps = { coverProbe: true };
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const all = ids
  ? ids.split(",")
  : (await getCompositions(serveUrl, { inputProps, chromiumOptions: { gl: "swangle" } })).map((c) => c.id).filter((c) => c.startsWith("Cover"));
const pngs = [];
for (const id of all) {
  const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions: { gl: "swangle" } });
  const n = composition.id.slice(5);
  const output = path.join(outDir, `cover-${n}.png`);
  let layout = null;
  await renderStill({
    composition,
    serveUrl,
    output,
    frame: 0,
    inputProps,
    chromiumOptions: { gl: "swangle" },
    onBrowserLog: (log) => {
      if (log.text.startsWith("COVER|")) layout = JSON.parse(log.text.slice(6));
    },
  });
  if (!layout) throw new Error(`${composition.id}: the cover probe logged nothing`);
  fs.writeFileSync(path.join(outDir, `cover-${n}.json`), JSON.stringify(layout, null, 1) + "\n");
  pngs.push(output);
  console.log(output, JSON.stringify(layout));
}
fs.rmSync(serveUrl, { recursive: true, force: true });
const python = process.env.PYTHON ?? (fs.existsSync("../.venv/bin/python") ? "../.venv/bin/python" : "python3");
try {
  execFileSync(python, [path.resolve("../pipeline/covercheck.py"), ...pngs], { stdio: "inherit" });
} catch {
  process.exit(1);
}
