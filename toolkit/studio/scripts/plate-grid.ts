// Writes, for every pixel centre of a plate, the longitude and latitude that
// a named projection puts there (float32 pairs, NaN off the map), so
// pipeline/reproject.py can warp imagery onto projections it has no
// closed-form inverse for. A pixel counts as on the map only if projecting
// its point forward lands back within half a pixel.
//   node --experimental-strip-types scripts/plate-grid.ts laea-europe 4096 3042 out.bin
import { writeFileSync } from "node:fs";
import { PROJECTIONS } from "../src/lib/projections.ts";

const [name, ws, hs, out] = process.argv.slice(2);
const make = PROJECTIONS[name];
if (!make) throw new Error(`unknown projection ${name}`);
const w = Number(ws);
const h = Number(hs);
const p = make(w, h);
const grid = new Float32Array(w * h * 2).fill(Number.NaN);
for (let y = 0; y < h; y++) {
  for (let x = 0; x < w; x++) {
    const ll = p.invert?.([x + 0.5, y + 0.5]);
    if (!ll || !Number.isFinite(ll[0]) || !Number.isFinite(ll[1])) continue;
    const back = p(ll);
    if (!back || Math.abs(back[0] - x - 0.5) > 0.5 || Math.abs(back[1] - y - 0.5) > 0.5) continue;
    grid[(y * w + x) * 2] = ll[0];
    grid[(y * w + x) * 2 + 1] = ll[1];
  }
}
writeFileSync(out, Buffer.from(grid.buffer));
