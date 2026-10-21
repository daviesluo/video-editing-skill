// Renders one still per set of props from a single bundle, for comparing
// design options side by side. A change of look goes to the owner as two
// or three finished options rendered this way, and one is picked before
// anything is rebuilt.
//   node scripts/variants.mjs <composition> <outDir> '<[{"name":..., "props":{...}}, ...]>' [frame]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [id, outDir, listJson, frameArg] = process.argv.slice(2);
const list = JSON.parse(listJson);
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const { name, props } of list) {
  const composition = await selectComposition({ serveUrl, id, inputProps: props, chromiumOptions: { gl: "swangle" } });
  const output = path.resolve(outDir, `${name}.png`);
  await renderStill({ composition, serveUrl, output, frame: Number(frameArg ?? 0), inputProps: props, chromiumOptions: { gl: "swangle" } });
  console.log(output);
}
fs.rmSync(serveUrl, { recursive: true, force: true });
