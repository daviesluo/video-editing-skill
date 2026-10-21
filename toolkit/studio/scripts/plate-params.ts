// Prints the fitted parameters of a named projection for a plate size, as
// JSON for pipeline/reproject.py:
//   node --experimental-strip-types scripts/plate-params.ts mercator-world 4096 3000
import { PROJECTIONS } from "../src/lib/projections.ts";

const [name, w, h] = process.argv.slice(2);
const make = PROJECTIONS[name];
if (!make) throw new Error(`unknown projection ${name}; known: ${Object.keys(PROJECTIONS).join(", ")}`);
const p = make(Number(w), Number(h));
const type = name.split("-")[0];
console.log(JSON.stringify({ name, type, width: Number(w), height: Number(h), k: p.scale(), t: p.translate(), rotate: p.rotate() }));
